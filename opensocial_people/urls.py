# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('softgis_open_social.views',
            url(r'^people/(\d+)/(\d+)*$',
                'people',
                name="api_people"),

        )
