# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('softgis_open_social.views',
            url(r'^groups/(\d+)/(\d+)*$',
                'groups',
                name="api_groups"),

        )
