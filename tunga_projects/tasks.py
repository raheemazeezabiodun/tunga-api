import datetime

from dateutil.relativedelta import relativedelta
from django.template.loader import render_to_string
from django_rq.decorators import job
from weasyprint import HTML

from tunga_auth.models import TungaUser
from tunga_payments.models import Invoice, Payment
from tunga_projects.models import Project, ProgressEvent
from tunga_utils.constants import PROGRESS_EVENT_MILESTONE, \
    INVOICE_TYPE_PURCHASE, INVOICE_TYPE_SALE


@job
def weekly_project_report(projects):
    active_projects = Project.objects.filter(id__in=projects)

    projects_ = []
    for project in active_projects:
        right_now = datetime.datetime.utcnow()
        past_by_3_days = right_now - relativedelta(days=3)
        next_week = right_now + relativedelta(days=7)

        pm_id = project.pm.id or project.owner.id
        pm = TungaUser.objects.get(id=pm_id).display_name

        sales_invoices = Invoice.objects.filter(
            project=project,
            type=INVOICE_TYPE_SALE,
            paid=False
        ).values_list('id', flat=True)

        payments = Payment.objects.filter(
            invoice__id__in=list(sales_invoices),
            paid_at__isnull=True)

        purchase_invoices = Invoice.objects.filter(
            project=project,
            type=INVOICE_TYPE_PURCHASE,
            paid=False
        ).values_list('id', flat=True)
        payouts = Payment.objects.filter(
            invoice__id__in=list(purchase_invoices),
            paid_at__isnull=True)

        milestones = ProgressEvent.objects.filter(
            project=project,
            due_at__range=[past_by_3_days, next_week],
            type=PROGRESS_EVENT_MILESTONE
        )

        projects_.append({'payments': payments,
                          'payouts': payouts,
                          'milestones': milestones,
                          'pm': pm,
                          'title': project.title
                          })
    ctx = {"projects": projects_, "week": datetime.datetime.utcnow().isocalendar()[1]}
    rendered_html = render_to_string("tunga/pdf/weekly_project_report.html", context=ctx).encode(encoding="UTF-8")
    pdf_file = HTML(string=rendered_html, encoding='utf-8').write_pdf()


@job
def weekly_payment_report(paid, unpaid_overdue, unpaid):
    paid_invoices = Invoice.objects.filter(id__in=paid)
    over_due_invoices = Invoice.objects.filter(id__in=unpaid_overdue)
    unpaid_invoices = Invoice.objects.filter(id__in=unpaid)
    ctx = {"paid_invoices": paid_invoices,
           "over_due_invoices": over_due_invoices,
           "unpaid_invoices": unpaid_invoices,
           "week": datetime.datetime.utcnow().isocalendar()[1]}
    rendered_html = render_to_string("tunga/pdf/weekly_payment_report.html", context=ctx).encode(encoding="UTF-8")
    pdf_file = HTML(string=rendered_html, encoding='utf-8').write_pdf()
