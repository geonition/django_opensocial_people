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
                        
                        (r'^people/(?P<user>@?\w+)$',
                        People.as_view(),
                        {'group': '@friends'}),
            
                        (r'^people/(?P<user>@?\w+)/(?P<group>@?\w+)$',
                        People.as_view()),
            
                        (r'^people/(?P<user>@?\w+)/(?P<group>@?\w+)/(?P<tuser>@?\w+)$',
                        People.as_view()),
            
        )
