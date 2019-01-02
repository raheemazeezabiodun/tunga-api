from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http

# Email of the Service Account
SERVICE_ACCOUNT_EMAIL = 'tunga-email@tunga-emails-226113.iam.gserviceaccount.com'

# Path to the Service Account's Private Key file
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '/Users/azeezraheem/Downloads/tunga-emails-226113-057a6ea3d2dc.p12'

def list_users(user_email):
    """Build and returns an Admin SDK Directory service object authorized with the service accounts
    that act on behalf of the given user.

    Args:
      user_email: The email of the user. Needs permissions to access the Admin APIs.
    Returns:
      Admin SDK directory service object.
    """

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL,
        SERVICE_ACCOUNT_PKCS12_FILE_PATH,
        'notasecret',
        scopes=['https://www.googleapis.com/auth/admin.directory.user'])

    #credentials = credentials.create_delegated(user_email)

    #return build('admin', 'directory_v1', credentials=credentials)
    delegated_credentials = credentials.create_delegated(user_email)
    http_auth = delegated_credentials.authorize(Http())
    service = build('admin', 'directory_v1', http=http_auth)
    return service.users().list(customer='my_customer', maxResults=10, orderBy='email', domain='getcava.com').execute()


def subscribe_to_new_users(user_email):
    credentials = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL,
        SERVICE_ACCOUNT_PKCS12_FILE_PATH,
        'notasecret',
        scopes=['https://www.googleapis.com/auth/admin.directory.user.readonly, https://www.googleapis.com/auth/admin.directory.user'])
    delegated_credentials = credentials.create_delegated(user_email)
    http_auth = delegated_credentials.authorize(Http())
    service = build('admin', 'directory_v1', http=http_auth)
    return service
