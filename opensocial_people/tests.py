from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.test.client import Client
from django.utils import simplejson as json
from models import Relationship
from models import Person

class PeopleTest(TestCase):
    
    def setUp(self):
        
        #create the client to be used
        self.client = Client()
        
        #create users
        self.user1 = User.objects.create_user('user1',
                                              'testa@test.com',
                                              'user1')
        self.user2 = User.objects.create_user('user2',
                                              'testb@test.com',
                                              'user2')
        self.user3 = User.objects.create_user('user3',
                                              'testc@test.com',
                                              'user3')    
        self.user4 = User.objects.create_user('user4',
                                              'testd@test.com',
                                              'user4')
        self.user5 = User.objects.create_user('user5',
                                              'teste@test.com',
                                              'user5')
        self.user6 = User.objects.create_user('user6',
                                              'testf@test.com',
                                              'user6')
        self.user7 = User.objects.create_user('user7',
                                              '',
                                              'user7')
        
        #create a group
        self.group1 = Group(name='@family')
        self.group1.save()
        self.group2 = Group(name="data_view_permission")
        self.group2.save()
        permission = Permission.objects.get(codename="data_view")
        self.group2.permissions.add(permission)
        
        #create a relationship
        r = Relationship(initial_user = self.user5,
                         group = self.group1,
                         target_user = self.user6)
        r.save()
        r = Relationship(initial_user = self.user5,
                         group = self.group1,
                         target_user = self.user7)
        r.save()
        r = Relationship(initial_user = self.user6,
                         group = self.group1,
                         target_user = self.user7)
        r.save()
        
        
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
                        "The user should not be able to "
                        "query data without beeing authenticated")
        
        
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
                          'testa@test.com',
                          'The email was not some@some.org for user1')
        
        #query other persons
        url = "%s%s" % (reverse('people'), "/user2/@self")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                        403,
                        "The user should not be able to query "
                        "other persons without permissions")
        
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
        
        #query with with help of others relationship
        url = "%s%s" % (reverse('people'), "/user6/@family/user7")
        response = self.client.get(url)
        
        self.assertContains(response,
                            '"id":',
                            status_code=200)
        
        #query with not existing relationship
        url = "%s%s" % (reverse('people'), "/user1/@family/user2")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                        404,
                        'querying with relationship that does not exist '
                        'should return not found')
        
        
        #query with not existing user
        url = "%s%s" % (reverse('people'), "/so-me_cool+user/@self")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                        404,
                        'querying with relationship that does not exist '
                        'should return not found')
        
        #check that it is not a django error page
        self.assertNotContains(response,
                               "<html>",
                               status_code=404)
        
    def test_person_collection_get(self):
        
        #not signed in should return unauthorized
        url = "%s%s" % (reverse('people'), "/user5/@family")
        response = self.client.get(url)
        
        self.assertEquals(response.status_code,
                          401,
                          'Response should have been 401 as the user '
                          'was not authenticated')
        
        #sign in
        self.client.login(username='user5',
                          password='user5')
        response = self.client.get(url)
        self.assertContains(response,
                            '"id"',
                            status_code=200)
        
        
        #query user 5 family should return user6 and user7
        self.assertContains(response,
                            '"username": "user6"',
                            status_code = 200)
        self.assertContains(response,
                            '"username": "user7"',
                            status_code = 200)
        
        #query user5 @self should return user5
        url = "%s%s" % (reverse('people'), "/user5/@self")
        
        response = self.client.get(url)
        self.assertContains(response,
                            '"username": "user5"',
                            status_code = 200)
        
        #tests querying with different GET parameters
        
        #give permission to user5 data_view
        self.user5.user_permissions.add(Permission.objects.get(codename='data_view'))
        
        #set age, gender and car values to each person
        person_values1 = {
            'age': 25,
            'gender': 'male',
            'car': False
        }
        person_values2 = {
            'age': 26,
            'gender': 'female',
            'car': True
        }
        person1 = Person.objects.filter(user=self.user1)[0]
        person1.update(json.dumps(person_values1))
        person2 = Person.objects.filter(user=self.user2)[0]
        person2.update(json.dumps(person_values2))
        
        #should return all users
        url = "%s%s" % (reverse('people'), "/@all/@self")
        response = self.client.get(url)
        self.assertContains(response,
                            '"username": "user5"',
                            status_code = 200)
        self.assertContains(response,
                            '"username": "user1"',
                            status_code = 200)
        self.assertContains(response,
                            '"username": "user2"',
                            status_code = 200)
        self.assertContains(response,
                            '"age": 25',
                            status_code = 200)
        self.assertContains(response,
                            '"age": 26',
                            status_code = 200)
        
        #should only return user1
        url = "%s%s" % (reverse('people'), "/@all/@self?age=25")
        response = self.client.get(url)
        self.assertContains(response,
                            '"username": "user1"',
                            status_code = 200)
        self.assertNotContains(response,
                            '"username": "user2"',
                            status_code = 200)
        
        #should only contain user2
        url = "%s%s" % (reverse('people'), "/@all/@self?age__max=25&gender=male&car=false")
        response = self.client.get(url)
        self.assertContains(response,
                            '"username": "user1"',
                            status_code = 200)
        self.assertNotContains(response,
                            '"username": "user2"',
                            status_code = 200)
        
        #should only contain user1
        url = "%s%s" % (reverse('people'), "/@all/@self?age__min=26")
        response = self.client.get(url)
        self.assertNotContains(response,
                            '"username": "user1"',
                            status_code = 200)
        self.assertContains(response,
                            '"username": "user2"',
                            status_code = 200)
        
        #querying a range should return only user2
        url = "%s%s" % (reverse('people'), "/@all/@self?age__min=26&age__max=26")
        response = self.client.get(url)
        self.assertNotContains(response,
                            '"username": "user1"',
                            status_code = 200)
        self.assertContains(response,
                            '"username": "user2"',
                            status_code = 200)
        
    def test_person_update(self):
        #updating the person with PUT requests
        #opensocial defines this with POST request but that conflicts with
        #the relationship creation and REST principles
        
        #authenticate and get person (user1)
        self.client.login(username='user1', password='user1')
        
        #get a person
        url = "%s%s" % (reverse('people'), "/@me/@self")
        response = self.client.get(url)
        
        person_dict = json.loads(response.content)
        
        #change some value in person
        person_dict['first_name'] = 'Toffe'
        person_dict['last_name'] = 'guess'
        
        #update the person
        response = self.client.put(url,
                                   data=json.dumps(person_dict),
                                   content_type='application/json')
        
        #update the person twice with same values should return a person
        response = self.client.put(url,
                                   data=json.dumps(person_dict),
                                   content_type='application/json')
        
        #get the same person and check the value
        response = self.client.get(url)
        
        new_person_dict = json.loads(response.content)
        self.assertEquals(new_person_dict['first_name'],
                          'Toffe',
                          'The first name was not updated')
        self.assertEquals(new_person_dict['last_name'],
                          'guess',
                          'The last name was not updated')
        
        #test that only part of the profile can be updated
        new_values = {'new_value': True}
        response = self.client.put(url,
                                   data=json.dumps(new_values),
                                   content_type='application/json')
        new_person_dict = json.loads(response.content)
        self.assertEquals(new_person_dict['last_name'],
                          'guess',
                          'The last name was not the same after update')
        
        self.assertEquals(new_person_dict['new_value'],
                          True,
                          'The new value was added')
               
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
                                    json.dumps({'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''}),
                                    content_type='application/json')
        
        self.assertEquals(response.status_code,
                          201,
                          "The create relationship request did not "
                          "return 201 created")
        
        
        # test success with other group
        # post to /people/@me/family with target person as post content
        url = "%s%s" % (reverse('people'), "/@me/@family")
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "The create relationship request did not "
                          "return 201 created")
        
        
        # test creation with not existing group,
        # should not matter and returns 201
        url = "%s%s" % (reverse('people'), "/@me/no_group")
        response = self.client.post(url,
                                    {'id': 'user2',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "Creating relationship with non existing group "
                          "did not return 201 created")
        
        
        # test creation with not existing user
        url = "%s%s" % (reverse('people'), "/user1/@friends")
        response = self.client.post(url,
                                    {'id': 'non_exist',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          404,
                          "Creating relationship with non existing user "
                          "did not return 404 not found")
        
        
        # group_id should dafault to @friends
        url = "%s%s" % (reverse('people'), "/user1")
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "Creating relationship with default @friends "
                          "as group did not return 201 created")
        
        
        # user_id should default to @me and group to @friends
        url = reverse('people')
        response = self.client.post(url,
                                    {'id': 'user4',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          201,
                          "Creating relationship with default @me as user "
                          "did not return 201 created")
        
        # test duplicate relationship
        # post to /people/@me/@friends with target person as post conent
        url = reverse('people')
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          409,
                          "Creating duplicate identical relationships "
                          "did not return 409 conflict")
        
        
        # user can only create relationships for himself/herself
        url = "%s%s" % (reverse('people'), "/user2/@friends")
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          403,
                          "Creating relationship for other users "
                          "did not return 403 forbidden")
        
        #try to create relationship for not existing user also other then @me
        url = "%s%s" % (reverse('people'), "/no_user/@friends")
        response = self.client.post(url,
                                    {'id': 'user3',
                                     'displayName': '',
                                     'thumbnailUrl': ''})
        
        self.assertEquals(response.status_code,
                          403,
                          "Creating relationship for other users "
                          "did not return 403 forbidden")
        
    def test_relationship_delete(self):
        #authenticate the user
        self.client.login(username='user5', password='user5')
        
        #delete one of the relationships created in setup
        url = "%s%s" % (reverse('people'), "/user5/@family/user6")
        
        response = self.client.delete(url)
        
        self.assertContains(response,
                               '',
                               status_code=200)
        
        #query the family members and check that user6 is there
        url = "%s%s" % (reverse('people'), "/user5/@family")
        response = self.client.get(url)
        
        self.assertNotContains(response,
                               'user6',
                               status_code=200)
     
    def test_person_supported_fields(self):
        url = "%s%s" % (reverse('people'), '/@supportedFields')
        response = self.client.get(url)
        
        self.assertEquals(json.loads(response.content),
                          ["username",
                           "last_name",
                           "time.create_time",
                           "email.primary",
                           "email.value",
                           "email.type",
                           "id",
                           "email.verified",
                           "first_name",
                           "displayName",
                           "time.expire_time",
                           "email"],
                          "The supported fields returned was not correct")
        
        #return fields with the json types as values
        url = "%s%s" % (reverse('people'), '/@supportedFields?types=true')
        response = self.client.get(url)
        self.assertEquals(json.loads(response.content),
                          {"username": "string",
                           "last_name": "string",
                           "time.create_time": "string",
                           "email.primary": True,
                           "email.value": "string",
                           "email.type": "string",
                           "id": "string",
                           "email.verified": True,
                           "first_name": "string",
                           "displayName": "string",
                           "time.expire_time": "string",
                           "email": "object"},
                          "The supported field types returned was not correct")
    
    def test_email(self):
        url = "%s%s" % (reverse('people'), "/@me/@self")
        self.client.login(username='user7', password='user7')
        mail.outbox = []
        
        #test with email in opensocial format
        values = {
            'email': {
                'value': u'test1@test.com',
                'primary': True
            }
        }
        response = self.client.put(url,
                                   data=json.dumps(values),
                                   content_type='application/json')
        
        self.assertEquals(json.loads(response.content).has_key('email'),
                          True,
                          'no email was found from response')
        
        #not confirmed yet, should return empty email
        self.assertEquals(json.loads(response.content)['email'],
                          {u'primary': True,
                           u'type': u'',
                           u'value': u'test1@test.com',
                           u'verified': False},
                          'the email object was not correct')
        
        #one confirmation email should have been sent
        self.assertEquals(len(mail.outbox),
                          1,
                          'The email saving did not send a confirmation email')
        self.assertEquals('test1@test.com',
                          mail.outbox[0].to[0],
                          'The email sent did not go to the right address')
        
        #confirm and try again
        email_address = EmailAddress.objects.get(email = "test1@test.com")
        email_confirmation = EmailConfirmation.objects.get(email_address = email_address)

        response = self.client.get(reverse('api_emailconfirmation',
                                           args=[email_confirmation.confirmation_key]))
        
        response = self.client.get(url)
        
        self.assertEquals(json.loads(response.content)['email'],
                          {u'value': u'test1@test.com',
                           u'primary': True,
                           u'type': u'',
                           u'verified': True},
                          'wrong email found from response')
        
        #test changing email in invalid format
        values = {
            'email': 'test2@test.com'
        }
        
        response = self.client.put(url,
                                   data=json.dumps(values),
                                   content_type='application/json')
        
        self.assertEquals(json.loads(response.content).has_key('email'),
                          True,
                          'no email was found from response')
        
        self.assertEquals(json.loads(response.content)['email'],
                          {u'value': u'test1@test.com',
                           u'primary': True,
                           u'type': u'',
                           u'verified': True},
                          'the wrong email was found from response')
        
        #two confirmation emails should have been sent
        self.assertEquals(len(mail.outbox),
                          2,
                          'The email saving did not send a confirmation email')
        self.assertEquals('test2@test.com',
                          mail.outbox[1].to[0],
                          'The email sent did not go to the right address')
        
        #confirm and try again
        email_address = EmailAddress.objects.get(email = "test2@test.com")
        email_confirmation = EmailConfirmation.objects.get(email_address = email_address)

        response = self.client.get(reverse('api_emailconfirmation',
                                           args=[email_confirmation.confirmation_key]))
        
        response = self.client.get(url)
        
        self.assertEquals(json.loads(response.content)['email'],
                          {'value': 'test2@test.com',
                           'primary': True,
                           'type': '',
                           'verified': True},
                          'after confirmation the email was not changed')
        
        #test changing to empty email
        values = {
            'email': ''
        }
        response = self.client.put(url,
                                   data=json.dumps(values),
                                   content_type='application/json')
        
        self.assertEquals(json.loads(response.content).has_key('email'),
                          True,
                          'no email was found from response')
        
        self.assertEquals(json.loads(response.content)['email'],
                          {u'value': u'',
                           u'primary': False,
                           u'type': u'',
                           'verified': False},
                          'empty email was not updated to empty')
        
        #test adding same email twice
        values = {
            'email': 'test2@test.com'
        }
        response = self.client.put(url,
                                   data=json.dumps(values),
                                   content_type='application/json')
        response = self.client.put(url,
                                   data=json.dumps(values),
                                   content_type='application/json')
        
        #validate email
        email_address = EmailAddress.objects.get(email = "test2@test.com")
        email_confirmation = EmailConfirmation.objects.get(email_address = email_address)

        response = self.client.get(reverse('api_emailconfirmation',
                                args=[email_confirmation.confirmation_key]))
        
        response = self.client.get(url)
        
        
        self.assertEquals(json.loads(response.content).has_key('email'),
                          True,
                          'no email was found from response')
        
        self.assertEquals(json.loads(response.content)['email'],
                          {u'value': u'test2@test.com',
                           u'primary': True,
                           u'type': u'',
                           u'verified': True},
                          'no email was found from response')
        
        
        #creating a user with email should send a confirmation email
        mail.outbox = []
        User.objects.create_user(username="hasanemail",
                                 password="email",
                                 email="very_unique@unique.com")
        
        self.assertEquals(len(mail.outbox),
                          1,
                          'email was not sent when creating a user')
        
    def tearDown(self):
        
        self.user1.delete()
        self.user2.delete()
        self.user3.delete()
        self.user4.delete()
        self.user5.delete()
        self.user6.delete()
        self.user7.delete()
        self.group1.delete()
        self.group2.delete()
        
        
        