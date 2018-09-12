from django.contrib.auth import get_user_model
from django_rq.decorators import job

from tunga_projects.models import Project, InterestPoll
from tunga_projects.notifications.email import notify_interest_poll_email
from tunga_projects.notifications.slack import notify_project_slack_dev
from tunga_utils.constants import PROJECT_STAGE_OPPORTUNITY, USER_TYPE_DEVELOPER
from tunga_utils.helpers import clean_instance
from tunga_utils.hubspot_utils import create_or_update_project_hubspot_deal


@job
def sync_hubspot_deal(project, **kwargs):
    project = clean_instance(project, Project)
    create_or_update_project_hubspot_deal(project, **kwargs)


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
