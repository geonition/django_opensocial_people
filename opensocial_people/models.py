from copy import deepcopy
from datetime import datetime
from time import mktime
from time import time
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import NoReverseMatch
from django.core.urlresolvers import reverse
from django.core.validators import email_re
from django.db import IntegrityError
from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import Signal
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.hashcompat import sha_constructor
from geonition_utils.models import JSON
from geonition_utils.models import TimeD
from random import random

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
            
        json_dict = self.json()
        old_dict = deepcopy(json_dict)
        # this one throws an error if not valid json -->
        # you get a 500
        json_dict.update(json.loads(json_string))

        if old_dict != json_dict:
            #set old feature as expired
            self.time.expire()
            self.save()
            
            #check the values that should be updated in the user model
            
            if json_dict.has_key('first_name'):
                self.user.first_name = json_dict['first_name']
            if json_dict.has_key('last_name'):
                self.user.last_name = json_dict['last_name']

            self.json_data.remove_values(['first_name',
                                          'last_name'])
            
            #save the user
            self.user.save()
            
            #save the new property
            new_json = JSON(collection='opensocial_people.person',
                            json_string=json.dumps(json_dict))
            new_json.save()
            
            new_time = TimeD()
            new_time.save()
            new_person = Person(user = self.user,
                                json_data = new_json,
                                time = new_time)
            new_person.save()
            
            return new_person
        
        else:
            return self
        
    def delete(self):
        self.time.expire()
    
    def json(self):
        """
        This function returns a dictionary representation of this
        object
        """
        #query email for person
        email_obj = EmailAddress.objects.all()
        
        try:
            email_obj = email_obj.filter(user = self.user,
                                         primary = True)
            email_obj = email_obj.latest('updated')
        
            #default person includes django user values
            default_person = {
                "id": self.user.username,
                "displayName": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": {
                    "value": email_obj.email,
                    "type": email_obj.type,
                    "primary": email_obj.primary,
                    "verified": email_obj.verified
                }
            }
        except EmailAddress.DoesNotExist:
            #default person includes django user values
            default_person = {
                "id": self.user.username,
                "displayName": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": {
                    "value": '',
                    "type": '',
                    "primary": False,
                    "verified": False
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
            'email.primary': True,
            'email.verified': True
        }
        fields = self.json_data.get_fields()
        fields.update(self.time.get_fields())
        fields.update(person_fields)
        
        return fields
        
    def __unicode__(self):
        return u'person obj for %s' % (self.user.username,)
        
    class Meta:
        #does this really index the text field?
        unique_together = (("time", "json_data", "user"),)
        permissions = (
            ("data_view", "Can view other's data"),
        )


def create_person(sender, instance, created, **kwargs):
    """
    This signal is meant to create a person object
    when a new django user is created
    """
    
    if created:
        default_person = {
            "id": instance.id,
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": {
                "value": instance.email,
                "type": "",
                "primary": True,
                "verified": False
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
"""
The rest is copied from the email_rest application to provide email
confirmation this is needed in all applications so it is good to embed it
let's clean it up later when needed.
"""

def get_send_mail():
    """
    A function to return a send_mail function suitable for use in the app. It
    deals with incompatibilities between signatures.
    """
    # favour django-mailer but fall back to django.core.mail
    if "mailer" in settings.INSTALLED_APPS:
        from mailer import send_mail
    else:
        from django.core.mail import send_mail as _send_mail
        def send_mail(*args, **kwargs):
            del kwargs["priority"]
            return _send_mail(*args, **kwargs)
    return send_mail

email_confirmed = Signal(providing_args=["email_address"])

send_mail = get_send_mail()

# this code based in-part on django-registration
class EmailAddressManager(models.Manager):

    def add_email(self, user, email):
        #check conflict, weired DatabaseError thrown otherwise
        #TODO check why DatabaseError is thrown
        existing_email = self.filter(email=email)
        
        if len(existing_email) == 0:
            #creates an object EmailAddress and sends the confirmation key
            email_address = self.create(user=user, email=email)
            EmailConfirmation.objects.send_confirmation(email_address)
            return email_address    
        
    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except EmailAddress.DoesNotExist:
            return None
        
    def delete_user_emails(self, user):
        self.filter(user = user).delete()
  

class EmailAddress(models.Model):

    user = models.ForeignKey(User)
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    primary = models.BooleanField(default=False)
    updated = models.TimeField(auto_now=True)
    type = models.CharField(default='',
                            max_length=20)

    objects = EmailAddressManager()

    def set_as_primary(self):
        old_primary = EmailAddress.objects.get_primary(self.user)
        
        if old_primary:
            old_primary.primary = False
            old_primary.save()
        
        self.primary = True
        self.save()
        self.user.email = self.email
        self.user.save()
        return True

    def __unicode__(self):
        return u"%s (%s)" % (self.email, self.user)

    class Meta:
        verbose_name = u"e-mail address"
        verbose_name_plural = u"e-mail addresses"
        unique_together = (
            ("user", "email"),
        )


class EmailConfirmationManager(models.Manager):

    def confirm_email(self, confirmation_key):
        try:
            confirmation = self.get(confirmation_key=confirmation_key)
        except self.model.DoesNotExist:
            return None
        
        if not confirmation.key_expired():
            
            email_address = confirmation.email_address
            email_address.verified = True
            email_address.set_as_primary()
            email_address.save()
            email_confirmed.send(sender=self.model,
                                 email_address=email_address)
            
            #update the User object with the confirmed email
            email_address.user.email = email_address.email
            email_address.user.save()
            
            return email_address

    def send_confirmation(self, email_address):
        #check email addres
        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + email_address.email).hexdigest()
        current_site = Site.objects.get_current()
        
        path = reverse('api_emailconfirmation',
                        args=[confirmation_key])
        
        #TODO this should definitelly be https or?   
        activate_url = u"http://%s%s" % (unicode(current_site.domain), path)
        
        context = {
            "user": email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "confirmation_key": confirmation_key,
        }
        
        subject = render_to_string(
            "emailconfirmation/email_confirmation_subject.txt", context)
        
        # remove superfluous line breaks
        subject = "".join(subject.splitlines())
        message = render_to_string(
            "emailconfirmation/email_confirmation_message.txt", context)
        
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [email_address.email],
                  priority="high")
        
        return self.create(
            email_address=email_address,
            sent=datetime.now(),
            confirmation_key=confirmation_key)

    def delete_expired_confirmations(self):
        for confirmation in self.all():
            if confirmation.key_expired():
                confirmation.delete()
    

class EmailConfirmation(models.Model):

    email_address = models.ForeignKey(EmailAddress)
    sent = models.DateTimeField()
    confirmation_key = models.CharField(max_length=40)

    objects = EmailConfirmationManager()

    def key_expired(self):
        expiration_date = self.sent + timedelta(
            days=getattr(settings, "EMAIL_CONFIRMATION_DAYS", 3))
        return expiration_date <= datetime.now()
        
    key_expired.boolean = True

    def __unicode__(self):
        return u"confirmation for %s" % self.email_address

    class Meta:
        verbose_name = u"e-mail confirmation"
        verbose_name_plural = u"e-mail confirmations"


#email saving signal
def confirm_email(sender, instance, **kwargs):
    person_email = instance.json_data.json().get('email', {})
    primary = False
    type = ''
    try:
        temp_person_email = person_email.get('value', '')
        primary = person_email.get('primary', False)
        type = person_email.get('type', '')
        person_email = temp_person_email
    except AttributeError:
        pass
    
    
    email_address = None
    
    if email_re.match(person_email):
        email_address = EmailAddress.objects.add_email(instance.user,
                                                        person_email)            
    
    #person email confirmation if user was created some other way
    elif person_email == '':
        
        cdate= instance.user.date_joined
        seconds = time() - mktime(cdate.timetuple())
        timediff = timedelta(seconds=seconds)
        
        # problem with id being none when person object is updated
        # new person created but not because user is created
        if instance.id == None and email_re.match(instance.user.email):
            email_address = EmailAddress.objects.add_email(instance.user,
                                                        instance.user.email)
            
        else:
            instance.user.email = ''
            instance.user.save()
            
            EmailAddress.objects.delete_user_emails(instance.user)
            
        
    if email_address != None:
        email_address.primary = primary
        email_address.type = type
        email_address.save()
    
    
    instance.json_data.remove_values(['email'])


post_save.connect(confirm_email,
                  sender=Person,
                  dispatch_uid="opensocial_people_person")