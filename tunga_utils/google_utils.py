from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from django.conf import settings

# Email of the Service Account
SERVICE_ACCOUNT_EMAIL = settings.SERVICE_ACCOUNT_EMAIL

# Path to the Service Account's Private Key file
SERVICE_ACCOUNT_PKCS12_FILE_PATH = settings.SERVICE_ACCOUNT_PKCS12_FILE_PATH

def list_users(user_email):
    """Build and returns an Admin SDK Directory service object authorized with the service accounts
    that act on behalf of the given user.

    params:
      user_email: The email of the user. Needs permissions to access the Admin APIs. (ADMIN)
    Returns:
      Admin SDK directory service object.
    """

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL,
        SERVICE_ACCOUNT_PKCS12_FILE_PATH,
        'notasecret',
        scopes=[settings.GOOGLE_ADMIN_USER_DIRECTORY_ENDPOINT])

    delegated_credentials = credentials.create_delegated(user_email)
    http_auth = delegated_credentials.authorize(Http())
    service = build('admin', 'directory_v1', http=http_auth)
    return service.users().list(customer='my_customer', maxResults=10, orderBy='email', domain=settings.GOOGLE_ADMIN_DOMAIN).execute()


def subscribe_to_new_users(user_email):
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL,
        SERVICE_ACCOUNT_PKCS12_FILE_PATH,
        'notasecret',
        scopes=[settings.GOOGLE_ADMIN_USER_DIRECTORY_READONLY, settings.GOOGLE_ADMIN_USER_DIRECTORY_ENDPOINT])
    delegated_credentials = credentials.create_delegated(user_email)
    http_auth = delegated_credentials.authorize(Http())
    service = build('admin', 'directory_v1', http=http_auth)
    return service
