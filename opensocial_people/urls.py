# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('opensocial_people.views',
                       url(r'^people$',
                           'people',
                           {'user': '@me',
                            'group': '@friends'},
                            name="people"),            
                        
                        (r'^people/(?P<user>@?\w+)$',
                        'people',
                        {'group': '@friends'}),
            
                        (r'^people/(?P<user>@?\w+)/(?P<group>@?\w+)$',
                        'people'),
            
                        (r'^people/(?P<user>@?\w+)/(?P<group>@?\w+)/(?P<tuser>@?\w+)$',
                        'people'),
            
        )
