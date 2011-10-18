from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import simplejson as json
from geonition_utils.models import JSON
from geonition_utils.models import TimeD

class Relationship(models.Model):
    """ The Relationship model describes a link between two users """
    
    initial_user = models.ForeignKey(User, related_name='initial_user')
    group = models.CharField(max_length = 10)
    target_user = models.ForeignKey(User, related_name='target_user')
    
    
    def __unicode__(self):
        return u"%s -> %s -> %s" % (self.initial_user.username,
                                    self.group,
                                    self.target_user.username)
        
    class Meta:
        unique_together = ('initial_user',
                           'group',
                           'target_user')
        

#this can be used instead of writing getattr everywhere
USE_MONGODB = getattr(settings, "USE_MONGODB", False)

class Person(models.Model):
    """
    additional possibly changing values to connect to
    a Person
    """
    user = models.ForeignKey(User)
    json_data = models.ForeignKey(JSON)
    time = models.ForeignKey(TimeD)        
        
    def update(self, json_string):
        """
        Updates this persons information.
        
        If the new information is the same as the saved one
        then nothing is done, otherwise the old person is
        expired and a new person is created.
        """
        
        if self.json_data.json_string != json_string:
            
            #this one throws an error if not valid json --> know how to use it
            #otherwise you get a 500
            json_dict = json.loads(json_string)
            
            #set old feature as expired
            self.time.expire()
            self.save()
            
            #save the new property
            new_json = JSON(collection='opensocial_people.person',
                            json_string=json_string)
            new_json.save()
            
            new_time = TimeD()
            new_time.save()
            new_person = Person(user = self.user,
                                json_data = new_json,
                                time = new_time)
            new_person.save()
            
            #check the values that should be updated in the user model
            if json_dict.has_key('first_name'):
                self.user.first_name = json_dict['first_name']
            if json_dict.has_key('last_name'):
                self.user.last_name = json_dict['last_name']
            if json_dict.has_key('email') and json_dict['email'].has_key('value'):
                self.user.email = json_dict['email']['value']
            #save the user
            self.user.save()
            
            return new_person
        
    def delete(self):
        self.time.expire()
    
    def json(self):
        """
        This function returns a dictionary representation of this
        object
        """
        #default person includes django user values
        default_person = {
            "id": self.user.username,
            "displayName": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": {
                "value": self.user.email,
                "type": "",
                "primary": True
            }
        }
        json_data_dict = json.loads(self.json_data.json_string)
        json_data_dict.update(default_person)
        return json_data_dict
    
    def get_fields(self):
        """
        This function returns a dictionary with keys and their
        coresponding JSON type as value.
        """
        person_fields = {
            'id': 'string',
            'username': 'string',
            'displayName': 'string',
            'first_name': 'string',
            'last_name': 'string',
            'email': 'object',
            'email.value': 'string',
            'email.type': 'string',
            'email.primary': True
        }
        fields = self.json_data.get_fields()
        fields.update(self.time.get_fields())
        fields.update(person_fields)
        
        return fields
        
    def __unicode__(self):
        return u'for user %s' % (self.user.username,)
        
    class Meta:
        #does this really index the text field?
        unique_together = (("time", "json_data", "user"),)
        permissions = (
            ("data_view", "Can view other's data"),
        )

# a signal reciever is added to create e person after a django user
# has been created
def create_person(sender, instance, created, **kwargs):
    
    if created:
        default_person = {
            "id": instance.id,
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": {
                "value": instance.email,
                "type": "",
                "primary": True
            }
        }
        json_obj = JSON(collection='opensocial_people_person',
                        json_string=json.dumps(default_person))
        json_obj.save()
        time_obj = TimeD()
        time_obj.save()
        
        Person(user=instance,
               json_data=json_obj,
               time=time_obj).save()
        
        #create relationship for oneself
        Relationship(initial_user=instance,
                     group='@self',
                     target_user=instance).save()

post_save.connect(create_person,
                  sender=User,
                  dispatch_uid="opensocial_people.person")