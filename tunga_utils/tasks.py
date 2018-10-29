from django_rq.decorators import job
from dateutil.parser import parse

from tunga_utils import hubspot_utils


@job
def log_calendly_event_hubspot(data):
    event_details = data.get('event', None)
    start_time = parse(event_details.get('start_time', None))

    invitee_details = data.get('invitee', dict())
    email = 'apps@davidsemakula.com' or invitee_details.get('email')
    name = invitee_details.get('name')
    first_name = invitee_details.get('first_name')
    last_name = invitee_details.get('last_name')

    contact_vid = hubspot_utils.get_hubspot_contact_vid(email, firstname=first_name or '', lastname=last_name or '')

    if contact_vid:
        questions_and_answers = data.get('questions_and_answers', [])
        payload = {
            "engagement": {
                "active": True,
                hubspot_utils.KEY_TYPE: "NOTE"
            },
            "associations": {
                "contactIds": [contact_vid],
                "companyIds": [],
                "dealIds": []
            },
            "metadata": {
                "body": "Scheduled a call via Calendly\n{}\n\n{}".format(
                    '\n'.join(
                        ['*{}:* {}'.format(item[0], item[1]) for item in
                         [
                             ['Name', name],
                             ['Email', invitee_details.get('email')],
                             ['Start Time', '*{}* at *{} UTC*'.format(
                                 start_time.strftime("%a, %d %b, %Y"),
                                 start_time.strftime("%I:%M %p")
                             )]
                         ]]),
                    '\n'.join(
                        ['{}:\n{}'.format(item.get('question'), item.get('answer')) for item in questions_and_answers]
                    )
                )
            }
        }

        hubspot_utils.create_custom_hubspot_engagement(payload)
