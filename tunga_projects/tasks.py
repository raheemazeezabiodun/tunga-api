from django_rq.decorators import job

from tunga_projects.models import Project
from tunga_utils.helpers import clean_instance
from tunga_utils.hubspot_utils import create_or_update_project_hubspot_deal


@job
def sync_hubspot_deal(project, **kwargs):
    project = clean_instance(project, Project)
    create_or_update_project_hubspot_deal(project, **kwargs)
