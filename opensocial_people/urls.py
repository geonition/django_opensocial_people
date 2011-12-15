# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from views import People

urlpatterns = patterns('opensocial_people.views',
                        url(r'^people$',
                           People.as_view(),
                           {'user': '@me',
                            'group': '@friends'},
                            name="people"),
                        
                        #this should work as defined in opensocial 2.0
                        #except with one addition if passed with ?types=true
                        #it returns a json with keys as fields and values as
                        # the type of the field
                        (r'^people/@supportedFields$',
                        'supported_fields'),
                        
                        (r'^people/(?P<user>@?[-+_\w]+)$',
                        People.as_view(),
                        {'group': '@friends'}),
            
                        (r'^people/(?P<user>@?[-+_\w]+)/(?P<group>@?\w+)$',
                        People.as_view()),
                        
                        (r'^people/(?P<user>@?[-+_\w]+)/(?P<group>@?\w+)/(?P<tuser>@?\w+)$',
                        People.as_view()),
            
        )
