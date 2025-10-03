SECRET_KEY = 'REPLACE'

DEBUG = True
ALLOWED_HOSTS = ['*']

from integration_utils.bitrix24.local_settings_class import LocalSettingsClass

NGROK_URL = 'http://localhost:8000/'

APP_SETTINGS = LocalSettingsClass(
    portal_domain='REPLACE',
    app_domain='127.0.0.1:8000',
    app_name='BitrixDeals',
    salt='REPLACE',
    secret_key='REPLACE',
    application_bitrix_client_id='REPLACE',
    application_bitrix_client_secret='REPLACE',
    application_index_path='/',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bitrixdeals',
        'USER': 'REPLACE',
        'PASSWORD': 'REPLACE',
        'HOST': 'localhost',
    },
}
