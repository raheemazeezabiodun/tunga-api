import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.template.loader import render_to_string
from django_rq.decorators import job
from weasyprint import HTML

from tunga.settings import TUNGA_URL
from tunga_payments.models import Invoice
from tunga_projects.models import Project, InterestPoll, Participation
from tunga_projects.notifications.email import notify_interest_poll_email
from tunga_projects.notifications.slack import notify_project_slack_dev
from tunga_utils.constants import PROJECT_STAGE_OPPORTUNITY, USER_TYPE_DEVELOPER, STATUS_INTERESTED, STATUS_ACCEPTED, \
    PROJECT_STAGE_ACTIVE, PROGRESS_EVENT_MILESTONE, INVOICE_TYPE_SALE, INVOICE_TYPE_PURCHASE
from tunga_utils.helpers import clean_instance
from tunga_utils.hubspot_utils import create_or_update_project_hubspot_deal


@job
def sync_hubspot_deal(project, **kwargs):
    project = clean_instance(project, Project)
    create_or_update_project_hubspot_deal(project, **kwargs)


@job
def activate_project(project):
    project = clean_instance(project, Project)

    approved_polls = project.interestpoll_set.filter(status=STATUS_INTERESTED, approval_status=STATUS_ACCEPTED)
    for poll in approved_polls:
        Participation.objects.update_or_create(
            project=project, user=poll.user,
            defaults=dict(
                status=STATUS_ACCEPTED,
                responded_at=poll.responded_at,
                created_by=poll.created_by or poll.project.user
            )
        )


@job
def manage_interest_polls(project, remind=False):
    project = clean_instance(project, Project)

    if project.stage != PROJECT_STAGE_OPPORTUNITY:
        # Only poll dev interest for opportunities
        return

    if remind:
        notify_project_slack_dev.delay(project.id, reminder=True)

    developers = get_user_model().objects.filter(type=USER_TYPE_DEVELOPER, userprofile__skills__in=project.skills.all())

    for developer in developers:
        interest_poll, created = InterestPoll.objects.update_or_create(
            project=project, user=developer,
            defaults=dict(created_by=project.user)
        )

        if created or remind:
            notify_interest_poll_email.delay(interest_poll.id, reminder=not created)


@job
def weekly_project_report(render_format='pdf', weeks_ago=0):
    projects = Project.objects.filter(stage=PROJECT_STAGE_ACTIVE, archived=False)
    today = datetime.datetime.utcnow()
    week_start = (today - datetime.timedelta(days=today.weekday(), weeks=weeks_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = (week_start + datetime.timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)

    report = []
    for project in projects:
        milestones = project.progressevent_set.filter(
            type=PROGRESS_EVENT_MILESTONE, due_at__gte=week_start, due_at__lte=week_end
        ).order_by('due_at')
        payments = project.invoice_set.filter(
            (
                Q(type=INVOICE_TYPE_SALE) &
                Q(issued_at__gte=week_start - datetime.timedelta(days=14)) &
                Q(issued_at__lte=week_end - datetime.timedelta(days=14))
                # Client invoices are due 14 days after the issue date
            ) |
            (
                Q(type=INVOICE_TYPE_PURCHASE) &
                Q(issued_at__gte=week_start) &
                Q(issued_at__lte=week_end)
                # Dev invoices are due on the issue date
            )
        ).order_by('issued_at')
        report.append(dict(
            project=dict(
                title=project.title,
                pm=(project.pm or project.user).display_name
            ),
            milestones=milestones,
            payments=[payment for payment in payments if payment.type == INVOICE_TYPE_SALE],
            payouts=[payment for payment in payments if payment.type == INVOICE_TYPE_PURCHASE]
        ))

    ctx = dict(
        week_start=week_start,
        week_end=week_end,
        week_number=week_start.isocalendar()[1],
        projects=report[13:17]
    )

    html = render_to_string("tunga/pdf/project_report.html", context=ctx).encode(encoding="UTF-8")
    if render_format == 'html':
        return html
    return HTML(string=html, encoding='utf-8').write_pdf()


@job
def weekly_payment_report(render_format='pdf', weeks_ago=0):
    today = datetime.datetime.utcnow()
    week_start = (today - datetime.timedelta(days=today.weekday(), weeks=weeks_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = (week_start + datetime.timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)

    upcoming_this_week = Invoice.objects.filter(
        type=INVOICE_TYPE_SALE,
        paid=False,
        issued_at__gte=week_start - datetime.timedelta(days=14),
        issued_at__lte=week_end - datetime.timedelta(days=14),
        # Client invoices are due 14 days after the issue date
    ).order_by('issued_at')

    paid_last_week = Invoice.objects.filter(
        type=INVOICE_TYPE_SALE,
        paid=True,
        paid_at__gte=week_start - datetime.timedelta(days=7),
        paid_at__lte=week_end - datetime.timedelta(days=7),
    ).order_by('paid_at')

    overdue = Invoice.objects.filter(
        type=INVOICE_TYPE_SALE,
        paid=False,
        issued_at__gte=week_end - datetime.timedelta(days=14),
        # Client invoices are due 14 days after the issue date so don't include those due this week
    ).order_by('issued_at')

    def clean_payments(payments):
        return dict(
            items=[
                dict(
                    id=payment.id,
                    title=payment.title,
                    project=dict(
                        id=payment.project.id,
                        title=payment.project.title,
                        owner=payment.project.owner or payment.project.user,
                        url='{}/projects/{}'.format(TUNGA_URL, payment.project.id)
                    ),
                    amount=payment.amount,
                    issued_at=payment.issued_at,
                    due_at=payment.due_at,
                    paid_at=payment.paid_at,
                )
                for payment in payments
            ],
            total=sum([payment.amount for payment in payments])
        )

    ctx = dict(
        week_start=week_start,
        week_end=week_end,
        week_number=week_start.isocalendar()[1],
        paid=clean_payments(paid_last_week),
        overdue=clean_payments(overdue),
        upcoming=clean_payments(upcoming_this_week)
    )

    html = render_to_string("tunga/pdf/payment_report.html", context=ctx).encode(encoding="UTF-8")
    if render_format == 'html':
        return html
    return HTML(string=html, encoding='utf-8').write_pdf()
