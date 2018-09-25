###############################################################################
# _*_ coding: utf-8
import json

import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from django.utils import six

from tunga_utils import hubspot_utils
from tunga_utils.models import ExternalEvent
from tunga_utils.notifications.slack import notify_hubspot_deal_changes_slack


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Tunga Notify HubSpot events
        """
        # command to run: python manage.py tunga_notify_hubspot_events
        last_12_hours = datetime.datetime.utcnow() - relativedelta(hours=50)
        events = ExternalEvent.objects.filter(notification_sent_at__isnull=True, created_at__gte=last_12_hours)

        deal_event_changes = dict()
        deal_event_ids = dict()

        for event in events:
            payload = json.loads(event.payload)
            for event_details in type(payload) is list and payload or [payload]:
                subscription_type = event_details.get(hubspot_utils.KEY_SUBSCRIPTION_TYPE)
                if subscription_type in [
                    hubspot_utils.KEY_VALUE_DEAL_CREATED,
                    hubspot_utils.KEY_VALUE_DEAL_DELETION,
                    hubspot_utils.KEY_VALUE_DEAL_PROPERTY_CHANGE
                ]:
                    deal_id = event_details.get(hubspot_utils.KEY_OBJECT_ID)

                    existing_deal_event_ids = deal_event_ids.get(deal_id, [])
                    existing_deal_event_payloads = deal_event_changes.get(deal_id, [])

                    if event.id not in existing_deal_event_ids:
                        existing_deal_event_ids.append(event.id)
                    existing_deal_event_payloads.append(event_details)

                    deal_event_ids[deal_id] = existing_deal_event_ids
                    deal_event_changes[deal_id] = existing_deal_event_payloads

        for deal_id, changes in six.iteritems(deal_event_changes):
            notify_hubspot_deal_changes_slack.delay(deal_id, changes, deal_event_ids.get(deal_id, []))
