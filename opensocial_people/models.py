from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import IntegrityError
from geonition_utils.manager import MongoDBManager
from geonition_utils.models import JSON
from geonition_utils.models import TimeD
from django.conf import settings
import django
from datetime import datetime
import sys

class Relationship(models.Model):
    """ The Relationship model describes a link between two users """
    
    initial_user = models.ForeignKey(User, related_name='initial_user')
    group = models.CharField(max_length = 10)
    target_user = models.ForeignKey(User, related_name='target_user')
    
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
            
    def update(self, json_string, *args, **kwargs):
        """
        Updates this persons information.
        
        If the new information is the same as the saved one
        then nothing is done, otherwise the old person is
        expired and a new person is created.
        """
        
        if self.json.json_string != json_string:
            
            #set old feature as expired
            self.time.expire()
            
            #save the new property
            new_json = JSON(collection='opensocial_people.person',
                            json_string=json_string)
            new_time = TimeD()
            new_person = Person(user = self.user,
                                json = new_json,
                                time = new_time)
            new_json.save()
            new_time.save()
            new_person.save()
        
    def delete(self, *args, **kwargs):
        self.time.expire()
        
    class Meta:
        unique_together = (("time", "json_data", "user"),)
        permissions = (
            ("data_view", "Can view other's data"),
        )
        
