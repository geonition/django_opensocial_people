from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.test.client import Client
from django.core.urlresolvers import reverse

import sys

if sys.version_info >= (2, 6):
    import json
else:
    import simplejson as json
    
class PeopleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = None
        
    def test_people(self):
        
        pass