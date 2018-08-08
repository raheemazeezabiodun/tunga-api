from django_rq import job

from tunga.settings import TUNGA_URL
from tunga_projects.models import Participation
from tunga_utils.emails import send_mail
from tunga_utils.helpers import clean_instance


@job
def notify_new_participant_email_dev(participation):
    participation = clean_instance(participation, Participation)

    subject = "Project invitation from {}".format(participation.created_by.first_name)
    to = [participation.user.email]
    ctx = {
        'inviter': participation.created_by,
        'invitee': participation.user,
        'project': participation.project,
        'project_url': '{}/projects/{}/'.format(TUNGA_URL, participation.project.id)
    }
    send_mail(
        subject, 'tunga/email/project_invitation', to, ctx
    )
