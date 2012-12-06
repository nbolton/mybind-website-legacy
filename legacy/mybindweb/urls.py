from mybindweb import views
from django.conf import settings
from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

# we always have media
urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^(favicon.ico)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^(robots.txt)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# only have views and admin if online
if settings.ONLINE:
    urlpatterns += patterns('',
        (r'^$', views.index),
        (r'^register/started/(.*)/$', views.register_started),
        (r'^register/verify/(.*)/$', views.register_verify),
        (r'^register/form/$', views.register_form),
        (r'^register/done/$', views.register_done),
        (r'^zones/$', views.zones_index),
        (r'^zones/new/$', views.zones_new),
        (r'^zones/edit/(.*)/$', views.zones_edit),
        (r'^zones/delete/(.*)/$', views.zones_delete),
        (r'^account/$', views.account_index),
        (r'^login/$', views.login),
        (r'^logout/$', views.logout),
        (r'^about/$', views.about),
        (r'^help/$', views.help),
        (r'^contact/$', views.contact),
        (r'^admin/', include(admin.site.urls)),
    )
    
    if settings.LIVE:
            urlpatterns += patterns('',
                    (r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_ROOT}),
            )
else:
    urlpatterns += patterns('',
        (r'.*', views.offline),
    )
