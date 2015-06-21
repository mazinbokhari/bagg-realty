from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bagg_realty.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # admin
    url(r'^admin/', include(admin.site.urls)),

    # realty_management
    url(r'^$', 'realty_management.views.index', name='index'),
    url(r'^all/(?P<model_name>\w+)$', 'realty_management.views.show_all', name='show_all'),
    url(r'^one/(?P<model_name>\w+)/(?P<key>.*)$', 'realty_management.views.show_one', name='show_one'),
    url(r'^(?P<action>\w+)/(?P<form_name>\w+)/(?P<key>.*)$', 'realty_management.views.modify_info', name='modify_info'),
    url(r'^delete$', 'realty_management.views.delete_info', name='delete_info'),
    url(r'^search$', 'realty_management.views.search', name='search'),
    url(r'^map$', 'realty_management.views.map', name='map'),
)
