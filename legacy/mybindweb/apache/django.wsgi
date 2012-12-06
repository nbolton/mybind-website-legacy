import os, sys
sys.path.append('/srv/sites')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mybindweb.settings_live'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
