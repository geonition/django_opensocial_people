from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
    
class PeopleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('user1', 'test1@test.com', 'user1')
        self.user2 = User.objects.create_user('user2', 'test2@test.com', 'user2')
        self.user3 = User.objects.create_user('user3', 'test3@test.com', 'user3')    
        self.user4 = User.objects.create_user('user4', 'test4@test.com', 'user4')
        
        self.group1 = Group(name='@family')
        self.group1.save()
    
    def test_people_rest(self):
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
        
    def test_relationship_create(self):
        # if the user is not authenticated it cannot create relationships
        url = "%s%s" % (reverse('people'), "/user1/@friends")
        
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          401,
                          "The post request without authentication did not return 401 Unauthorized")
        
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
        
        
        # test creation with not existing group
        url = "%s%s" % (reverse('people'), "/@me/no_group")
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          404,
                          "Creating relationship with non existing group did not return 404 not found")
        
        
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
        
        
        