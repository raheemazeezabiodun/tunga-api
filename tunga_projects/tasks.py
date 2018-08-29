import datetime

from dateutil.relativedelta import relativedelta
from django_rq.decorators import job

from tunga_auth.models import TungaUser
from tunga_payments.models import Invoice
from tunga_projects.models import Project, ProgressEvent
from tunga_utils.constants import STATUS_INITIATED, PROGRESS_EVENT_MILESTONE, \
    INVOICE_TYPE_PURCHASE, INVOICE_TYPE_SALE


@job
def weekly_report(projects):
    active_projects = Project.objects.filter(id__in=projects)
    for project in active_projects:
        right_now = datetime.datetime.utcnow()
        past_by_3_days = right_now - relativedelta(days=3)
        next_week = right_now + relativedelta(days=7)

        print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
        print "project %s" % project
        pm_id = project.pm.id
        pm = TungaUser.objects.get(id=pm_id).display_name

        payments = Invoice.objects.filter(
            project=project,
            status=STATUS_INITIATED,
            type=INVOICE_TYPE_SALE,
            paid=False
        )
        pay_outs = Invoice.objects.filter(
            project=project,
            status=STATUS_INITIATED,
            type=INVOICE_TYPE_PURCHASE,
            paid=False
        )
        mile_stones = ProgressEvent.objects.filter(
            project__archived=False,
            due_at__range=[past_by_3_days, next_week],
            type=PROGRESS_EVENT_MILESTONE
        )

        print "pm    %s" % pm
        print "milestones    %s" % mile_stones
        print "payouts    %s" % pay_outs
        print "payments    %s" % payments
