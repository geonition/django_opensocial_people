from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core import serializers
from django.db.utils import IntegrityError
from django.db import transaction
from django.utils import simplejson as json
from geonition_utils.HttpResponseExtenders import HttpResponseNotImplemented
from geonition_utils.HttpResponseExtenders import HttpResponseCreated
from geonition_utils.HttpResponseExtenders import HttpResponseConflict
from geonition_utils.HttpResponseExtenders import HttpResponseUnauthorized
from geonition_utils.views import RequestHandler
from models import Relationship
    
class People(RequestHandler):
    
    def __init__(self):
        pass
    
    def get(self, request, *args, **kwargs):
        
        #get the values
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)
                    
        if user == '@me' and request.user.is_authenticated():
            person_object = request.user
            
        elif request.user.is_authenticated():
            person_object = User.objects.get(username=user)
            
        else:
            return HttpResponseForbidden("You need to sign in to make requests")
        
        return HttpResponseNotImplemented("no not yet!")
        
    def post(self, request, *args, **kwargs):
        
        #get the values
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)
        
        if request.user.is_authenticated():
            initial_user = user
            relationship_type = group
                
            return create_relationship(request, initial_user, relationship_type)
        else:
            return HttpResponseUnauthorized("The user needs to be authenticated to make this request")
            

def create_relationship(request, initial_user, relationship_type):
    """ This function creates a realtionship from intial_user with
    relation_type to target user that is in the request.POST payload """
    
    #the user is only allowed to create relationships for him/herself            
    if initial_user != '@me' and request.user.username != initial_user:
        return HttpResponseForbidden("You are not allowed to create this relationship")

    iuser = request.user #should always be @me or the username of @me
    
    gtype = relationship_type
    
    tuser = None
    try:
        tuser = User.objects.get(username = request.POST.get('id', None))
    except User.DoesNotExist:
        return HttpResponseNotFound("The target user of the relationship was not found")
    
    relationship = Relationship(user_id = iuser,
                                group_id = gtype,
                                person = tuser)
    
    sid = transaction.savepoint()
    try:
        relationship.save()
        return HttpResponseCreated("The relationship was created")
    except Relationship.DoesNotExist:
        return HttpResponseNotFound("The relationship could not be created")
    except IntegrityError:
        transaction.savepoint_rollback(sid)
        return HttpResponseConflict("This relationship already exists")

def people_not_implemented():
    """ This function returns people service specific message for not
    implemented feature """
    return HttpResponseNotImplemented("This part of people service has not been implemented")