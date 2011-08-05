# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

import sys, os

urlpatterns = patterns('softgis_client.views',
                
            #javascript API for the REST
            url(r'^softgis.js',
                'javascript_api',
                name="api_javascript"),
            
            #javascript API for the REST
            url(r'^test.html',
                'test_api',
                name="api_test"),
            
            #get a csfr token for REST clients
            url(r'^csrf',
                'csrf',
                name="api_csrf"),
            
        )
