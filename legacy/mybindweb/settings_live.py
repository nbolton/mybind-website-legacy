from settings import *

LIVE = True
DEBUG = False
ONLINE = True

EMAIL_HOST = 'mail.mybind.com'
EMAIL_HOST_USER = 'auto-email@mybind.com'
EMAIL_HOST_PASSWORD = '4AZBPg2dvMxkiVDD01kr'

BASE = '/srv/sites/mybindweb'

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'mybind'
DATABASE_USER = 'mybindweb'
DATABASE_PASSWORD = 'Fluhe5Q8ZUEnAkvvohpt'

MEDIA_ROOT = r'%s/media' % BASE

ADMIN_MEDIA_ROOT = r'/usr/lib/python2.5/site-packages/django/contrib/admin/media'

TEMPLATE_DIRS = (
    r'%s/templates' % BASE
)
