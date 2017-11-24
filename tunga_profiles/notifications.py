import datetime

from django.contrib.auth import get_user_model
from django_rq.decorators import job

from tunga.settings import TUNGA_STAFF_UPDATE_EMAIL_RECIPIENTS, TUNGA_URL, SLACK_STAFF_INCOMING_WEBHOOK, \
    SLACK_ATTACHMENT_COLOR_GREEN, SLACK_ATTACHMENT_COLOR_RED, SLACK_STAFF_PROFILES_CHANNEL
from tunga_profiles.models import DeveloperApplication, Skill, DeveloperInvitation, UserProfile
from tunga_tasks.models import Task
from tunga_utils import slack_utils
from tunga_utils.constants import USER_TYPE_DEVELOPER
from tunga_utils.emails import send_mail
from tunga_utils.helpers import clean_instance


@job
def send_new_developer_email(instance):
    instance = clean_instance(instance, DeveloperApplication)
    subject = "{} has applied to become a Tunga developer".format(instance.display_name)
    to = TUNGA_STAFF_UPDATE_EMAIL_RECIPIENTS
    ctx = {
        'application': instance,
    }
    send_mail(subject, 'tunga/email/new_developer_application', to, ctx)


@job
def send_developer_application_received_email(instance):
    instance = clean_instance(instance, DeveloperApplication)
    subject = "Your application to become a Tunga developer has been received"
    to = [instance.email]
    ctx = {
        'application': instance
    }
    send_mail(subject, 'tunga/email/developer_application_received', to, ctx)


@job
def send_developer_accepted_email(instance):
    instance = clean_instance(instance, DeveloperApplication)
    subject = "Your application to become a Tunga developer has been accepted"
    to = [instance.email]
    ctx = {
        'application': instance,
        'invite_url': '%s/signup/developer/%s/' % (TUNGA_URL, instance.confirmation_key)
    }
    if send_mail(subject, 'tunga/email/developer_application_accepted', to, ctx):
        instance.confirmation_sent_at = datetime.datetime.utcnow()
        instance.save()


@job
def send_new_skill_email(instance):
    instance = clean_instance(instance, Skill)
    subject = "New skill created"
    to = TUNGA_STAFF_UPDATE_EMAIL_RECIPIENTS

    users = get_user_model().objects.filter(userprofile__skills=instance)
    tasks = Task.objects.filter(skills=instance)
    ctx = {
        'skill': instance.name,
        'users': users,
        'tasks': tasks
    }
    send_mail(subject, 'tunga/email/new_skill', to, ctx)


@job
def send_developer_invited_email(instance, resend=False):
    instance = clean_instance(instance, DeveloperInvitation)
    subject = "You have been invited to become a Tunga {}".format(
        instance.get_type_display().lower()
    )
    to = [instance.email]
    ctx = {
        'invite': instance,
        'invite_url': '%s/signup/invite/%s/' % (TUNGA_URL, instance.invitation_key, )
    }
    if send_mail(subject, 'tunga/email/user_invitation', to, ctx):
        if resend:
            instance.used = False
            instance.resent = True
            instance.resent_at = datetime.datetime.utcnow()
        else:
            instance.invitation_sent_at = datetime.datetime.utcnow()
        instance.save()

        if not resend:
            send_new_developer_invitation_sent_email(instance)


@job
def send_new_developer_invitation_sent_email(instance):
    instance = clean_instance(instance, DeveloperInvitation)
    subject = "{} has been invited to become a Tunga {}".format(
        instance.first_name,
        instance.get_type_display().lower()
    )
    to = [instance.created_by.email]
    to.extend(TUNGA_STAFF_UPDATE_EMAIL_RECIPIENTS)
    ctx = {
        'invite': instance
    }
    send_mail(subject, 'tunga/email/user_invitation_sent', to, ctx)


@job
def send_developer_invitation_accepted_email(instance):
    instance = clean_instance(instance, DeveloperInvitation)
    subject = "{} has accepted your invitation to become a Tunga {}".format(
        instance.first_name,
        instance.get_type_display().lower()
    )
    to = [instance.created_by.email]
    ctx = {
        'invite': instance
    }
    send_mail(subject, 'tunga/email/user_invitation_accepted', to, ctx)


@job
def notify_user_profile_updated_slack(instance, edited=None):
    instance = clean_instance(instance, UserProfile)

    if instance.user.type != USER_TYPE_DEVELOPER:
        return

    profile_url = '{}/developer/{}'.format(TUNGA_URL, instance.user.username)
    slack_msg = "{}'s profile has been updated | <{}|Review on Tunga>".format(
        instance.user.display_name,
        profile_url
    )

    attachments = [
        {
            slack_utils.KEY_TITLE: instance.user.display_name,
            slack_utils.KEY_TITLE_LINK: profile_url,
            slack_utils.KEY_TEXT: '*Name:* {}\n'
                                  '*Location:* {}\n'
                                  '*Skills*: {}\n'
                                  '*Verified:* {}'.format(
                instance.user.display_name,
                instance.location,
                str(instance.skills),
                instance.user.verified and 'True' or 'False'
            ),
            slack_utils.KEY_MRKDWN_IN: [slack_utils.KEY_TEXT],
            slack_utils.KEY_COLOR: instance.user.verified and SLACK_ATTACHMENT_COLOR_GREEN or SLACK_ATTACHMENT_COLOR_RED
        }
    ]

    slack_utils.send_incoming_webhook(
        SLACK_STAFF_INCOMING_WEBHOOK,
        {
            slack_utils.KEY_TEXT: slack_msg,
            slack_utils.KEY_ATTACHMENTS: attachments,
            slack_utils.KEY_CHANNEL: SLACK_STAFF_PROFILES_CHANNEL
        }
    )
