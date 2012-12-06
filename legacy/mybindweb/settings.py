# Django settings for mybind project.

LIVE = False
DEBUG = True
ONLINE = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Nick Bolton', 'nick@mybind.com'),
)

CONTACT_FORM = 'nick@mybind.com'

MANAGERS = ADMINS

EMAIL_HOST = 'mail.rensoft.net'
EMAIL_HOST_USER = 'development@auto-email.rensoft.net'
EMAIL_HOST_PASSWORD = 'vFFElu4OZwE05tiqPuui'

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = '../mybind.db3'

ACTIVATE_FROM_NAME = 'MyBind'
ACTIVATE_FROM_EMAIL = 'activate@mybind.com'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = r'media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lfe$(&g3a5wwik57&(ghqd%dnl0-8$2^4mws46i0jdn!2@u%-u'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'mybindweb.urls'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'mybindweb'
)

LOGIN_URL = '/login/'

AUTHENTICATION_BACKENDS = (
    'mybindweb.auth.AuthBackend',
)
