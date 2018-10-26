from algoliasearch import algoliasearch

from tunga.settings import ALGOLIA_APP_ID, ALGOLIA_ADMIN_KEY, ALGOLIA_INDEX

CHUNK_SIZE = 100


def get_index():
    client = algoliasearch.Client(ALGOLIA_APP_ID, ALGOLIA_ADMIN_KEY)
    return client.init_index(ALGOLIA_INDEX)


def add_objects(data):
    if data:
        for i in range(0, len(data), CHUNK_SIZE):
            chunk = data[i:i + CHUNK_SIZE]

            get_index().add_objects(chunk)
