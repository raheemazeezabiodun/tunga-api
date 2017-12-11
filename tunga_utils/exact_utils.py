from exactonline.api import ExactApi
from exactonline.storage import IniStorage

from tunga.settings import BASE_DIR


def get_api():
    storage = IniStorage(BASE_DIR + '/tunga/exact.ini')
    return ExactApi(storage=storage)
