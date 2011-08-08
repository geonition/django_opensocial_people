# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

urlpatterns = patterns('opensocial_people.views',
            url(r'^people$',
                'people',
                {'user': '@me',
                 'group': '@friends'},
                name="people"),
            
            (r'^people/@me/@friends$',
                'people',
                {'user': '@me',
                 'group': '@friends'}),
            (r'^people/@me/(\w+)$',
                'people',
                {'user': '@me'}),
            
            (r'^people/(\w+)/@self$',
                'people',
                {'group':'@self'}),
            
            (r'^people/(\w+)/@friends$',
                'people',
                {'group':'@friends'}),
            (r'^people/(\w+)/@friends/(\w+)$',
                'people',
                {'group':'@friends'}),
            
            (r'^people/(\w+)$',
                'people',
                {'group': '@friends'}),
            (r'^people/(\w+)/(\w+)$',
                'people'),
            (r'^people/(\w+)/(\w+)/(\w+)$',
                'people'),
        )
