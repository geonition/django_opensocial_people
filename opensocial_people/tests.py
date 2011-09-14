from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils import simplejson as json
from models import Relationship
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

class PeopleTest(TestCase):
    def setUp(self):
        
        #create the client to be used
        self.client = Client()
        
        #create users
        self.user1 = User.objects.create_user('user1', 'test1@test.com', 'user1')
        self.user2 = User.objects.create_user('user2', 'test2@test.com', 'user2')
        self.user3 = User.objects.create_user('user3', 'test3@test.com', 'user3')    
        self.user4 = User.objects.create_user('user4', 'test4@test.com', 'user4')
        self.user5 = User.objects.create_user('user5', 'test5@test.com', 'user5')
        self.user6 = User.objects.create_user('user6', 'test6@test.com', 'user6')
        self.user7 = User.objects.create_user('user7', 'test7@test.com', 'user7')
        
        #create a group
        self.group1 = Group(name='@family')
        self.group1.save()
        self.group2 = Group(name="data_view_permission")
        self.group2.save()
        self.group2.permissions.add(Permission.objects.get(codename="data_view"))
        
        #create a relationship
        r = Relationship(initial_user = self.user5,
                         group = self.group1,
                         target_user = self.user6)
        r = Relationship(initial_user = self.user5,
                         group = self.group1,
                         target_user = self.user7)
        
        #give users permissions
        self.user5.groups.add(self.group2)
        
        #create values for users profiles
        self.user1.first_name = "First1"
        self.user1.last_name = "Last1"
        self.user1.email = "some@some.org"
        self.user1.save()
    
    def test_people_rest(self):
        """
        These functions will throw an error
        if urls are not set.
        """
        base_url = reverse('people')
        self.client.get(base_url)
        
        url = "%s%s" % (base_url, "/user1")
        self.client.get(url)
        
        url = "%s%s" % (url, "/@friends")
        self.client.get(url)
        
        url = "%s%s" % (url, "/user3")
        self.client.get(url)
        
        url = "%s%s" % (base_url, "/@me/@friends")
        self.client.get(url)
        
    def test_person_get(self):
        
        #get person without beeing authenticated
        url = "%s%s" % (reverse('people'), "/@me/@self")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                        401,
                        "The user should not be able to query data without beeing authenticated")
        
        
        #authenticate and get person (user1)
        self.client.login(username='user1', password='user1')
        
        #query the authenticated users information
        url = "%s%s" % (reverse('people'), "/@me/@self")
        response = self.client.get(url)
        
        self.assertContains(response,
                            '"id":',
                            status_code=200)
        
        url = "%s%s" % (reverse('people'), "/user1/@self")
        response = self.client.get(url)
        
        self.assertContains(response,
                            '"id":',
                            status_code=200)
        
        #check the saved user1 data from django user
        response_dict = json.loads(response.content)
        self.assertEquals(response_dict['first_name'],
                          'First1',
                          'The first_name was not First1 for user1')
        self.assertEquals(response_dict['last_name'],
                          'Last1',
                          'The first_name was not Last1 for user1')
        self.assertEquals(response_dict['email']['value'],
                          'some@some.org',
                          'The email was not some@some.org for user1')
        
        #query other persons
        url = "%s%s" % (reverse('people'), "/user2/@self")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                        403,
                        "The user should not be able to query other persons without permissions")
        
        #query a user without permission should return 403
        url = "%s%s" % (reverse('people'), "/user1/@family/user6")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                          403,
                            "A user should not be able to query others data "
                            "without permissions")
        
        #logout user1 and login as user5 with permissions
        self.client.logout()
        self.client.login(username='user5',
                          password='user5')
        url = "%s%s" % (reverse('people'), "/user5/@family/user6")
        response = self.client.get(url)
        
        self.assertContains(response,
                            '"id":',
                            status_code=200)
        
    def test_person_collection_get(self):
        
        url = "%s%s" % (reverse('people'), "/user5/@family")
        response = self.client.get(url)
      
    def test_relationship_create(self):
        # if the user is not authenticated it cannot create relationships
        url = "%s%s" % (reverse('people'), "/user1/@friends")
        
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          401,
                          "The post request without authentication did not "
                          "return 401 Unauthorized")
        
        # authenticate user
        self.client.login(username='user1', password='user1')
        
        # test success with normal create relationship query
        # post to /people/@me/@friends with target person as post content
        url = "%s%s" % (reverse('people'), "/@me/@friends")
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "The create relationship request did not return 201 created")
        
        
        # test success with other group
        # post to /people/@me/family with target person as post content
        url = "%s%s" % (reverse('people'), "/@me/@family")
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "The create relationship request did not return 201 created")
        
        
        # test creation with not existing group, should not matter and returns 201
        url = "%s%s" % (reverse('people'), "/@me/no_group")
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "Creating relationship with non existing group did not return 201 created")
        
        
        # test creation with not existing user
        url = "%s%s" % (reverse('people'), "/user1/@friends")
        response = self.client.post(url,
                                    {'id': 'non_exist',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          404,
                          "Creating relationship with non existing user did not return 404 not found")
        
        
        # group_id should dafault to @friends
        url = "%s%s" % (reverse('people'), "/user1")
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "Creating relationship with default @friends as group did not return 201 created")
        
        
        # user_id should default to @me and group to @friends
        url = reverse('people')
        response = self.client.post(url,
                                    {'id': 'user4',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "Creating relationship with default @me as user did not return 201 created")
        
        # test duplicate relationship
        # post to /people/@me/@friends with target person as post conent
        url = reverse('people')
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          409,
                          "Creating duplicate identical relationships did not return 409 conflict")
        
        
        # user can only create relationships for himself/herself
        url = "%s%s" % (reverse('people'), "/user2/@friends")
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          403,
                          "Creating relationship for other users did not return 403 forbidden")
        
        #try to create relationship for not existing user also other then @me
        url = "%s%s" % (reverse('people'), "/no_user/@friends")
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          403,
                          "Creating relationship for other users did not return 403 forbidden")
        
        
        
    
       
    def tearDown(self):
        
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.user4.delete()
        self.group1.delete()
        
        
        