"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.test.client import Client
from django.core.urlresolvers import reverse

import sys

if sys.version_info >= (2, 6):
    import json
else:
    import simplejson as json
    
class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = None
        
        user1 = User.objects.create_user('user1','', 'passwd')
        self.client.login(username='user1', password='passwd')
        
        
    def test_group(self):
        
        group1 = Group.objects.create(name="Group1")
        group2 = Group.objects.create(name="Group2")
        
        
        user2 = User.objects.create_user('user2','', 'passwd')
        user3 = User.objects.create_user('user3','', 'passwd')
                
        user2.groups.add(group1, group2)
        user3.groups.add(group1)
               
        user2.save()
        user3.save()
        
        response = self.client.get(reverse('api_groups',
                                           args=[user2.id]))
        
        #user 2
        self.assertEquals(response.status_code,
                200,
                "the group inquiry didn't work")
         
        responsejson = json.loads(response.content)        
        resultjson = {"result" : { "entry" : [{"id" : group1.id, "title" : "Group1"}, {"id" : group2.id, "title" : "Group2"}] } }
        
        self.assertEquals(responsejson, resultjson, "The user groups are wrong when using open social API for user2")
        
        
        #user 3
        response = self.client.get(reverse('api_groups',
                                           args=[user3.id]))
        
        self.assertEquals(response.status_code,
                200,
                "the group inquiry didn't work")
         
        responsejson = json.loads(response.content)        
        resultjson = {"result" : { "entry" : [{"id" : group1.id, "title" : "Group1"}] } }
        
        self.assertEquals(responsejson, resultjson, "The user groups are wrong when using open social API for user3")
        
        #user 2 group2
        response = self.client.get(reverse('api_groups',
                                           args=[user2.id, group2.id]))
        
        self.assertEquals(response.status_code,
                200,
                "the group inquiry didn't work")
         
        responsejson = json.loads(response.content)        
        resultjson = {"id" : group2.id, "title" : "Group2"}
        
        self.assertEquals(responsejson, resultjson, "The user groups details are wrong when using open social API for user2 and group2")
        
        #user 3 group 1
        
        response = self.client.get(reverse('api_groups',
                                           args=[user3.id, group1.id]))
        
        self.assertEquals(response.status_code,
                200,
                "the group inquiry didn't work")
         
        responsejson = json.loads(response.content)        
        resultjson = {"id" : group1.id, "title" : "Group1"}
        
        self.assertEquals(responsejson, resultjson, "The user groups details are wrong when using open social API for user3 and group1")