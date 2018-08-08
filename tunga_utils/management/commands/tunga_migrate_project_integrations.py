import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from slacker import Slacker

from tunga_projects.models import Project
from tunga_projects.utils import save_project_metadata
from tunga_tasks.models import Integration
from tunga_utils import slack_utils
from tunga_utils.constants import APP_INTEGRATION_PROVIDER_SLACK


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate progress events
        """
        # command to run: python manage.py tunga_migrate_project_integrations

        task_integrations = Integration.objects.filter(provider=APP_INTEGRATION_PROVIDER_SLACK)
        for integration in task_integrations:
            print('integration: ', integration.id, integration.provider, integration.token, integration.task.id, integration.task.summary)

            try:
                project = Project.objects.get(legacy_id=integration.task.id)
            except ObjectDoesNotExist:
                project = None

            if project:
                # Project must exist
                print('project: ', project.id, project.title)

                if integration.token and integration.token_extra:
                    print('token', integration.token_extra)

                    token_response = json.loads(integration.token_extra)

                    token_info = {
                        'token': integration.token,
                        'token_extra': integration.token_extra,
                        'team_name': token_response['team_name'],
                        'team_id': token_response['team_id'],
                        'channel_id': integration.channel_id,
                        'channel_name': integration.channel_name,
                    }

                    if 'bot' in token_response:
                        token_info['bot_access_token'] = token_response['bot'].get('bot_access_token')
                        token_info['bot_user_id'] = token_response['bot'].get('bot_user_id')

                    # Turn on docs and reports sharing by default
                    meta_info = dict(slack_share_tunga_docs='true', slack_share_tunga_reports='true')
                    slack_client = Slacker(integration.token)
                    channel_response = slack_client.channels.list(exclude_archived=True)
                    if channel_response.successful:
                        channels = channel_response.body.get(slack_utils.KEY_CHANNELS, None)

                        if channels:
                            simple_channels = []

                            for channel in channels:
                                simple_channels.append(
                                    dict(
                                        id=channel.get('id', None),
                                        name=channel.get('name', None)
                                    )
                                )

                            meta_info['slack_channels'] = json.dumps(simple_channels)
                    for meta_key in token_info:
                        meta_info['slack_{}'.format(meta_key)] = token_info[meta_key]

                    print('meta info', meta_info)
                    save_project_metadata(project.id, meta_info)
                else:
                    print('token details missing', integration.id, integration.provider, integration.token, integration.token_extra, integration.task.id, integration.task.summary)
            else:
                print('project not migrated', integration.task.id)
