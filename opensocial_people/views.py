from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core import serializers
from django.db.utils import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.utils import simplejson as json
from geonition_utils.HttpResponseExtenders import HttpResponseNotImplemented
from geonition_utils.HttpResponseExtenders import HttpResponseCreated
from geonition_utils.HttpResponseExtenders import HttpResponseConflict
from geonition_utils.HttpResponseExtenders import HttpResponseUnauthorized
from geonition_utils.views import RequestHandler
from models import Relationship
from models import Person
from datetime import datetime
    
class People(RequestHandler):
    
    def __init__(self):
        pass
    
    def get(self, request, *args, **kwargs):
        
        #get the values
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)
        tuser = kwargs.get('tuser', None)
        
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized("You need to authenticate to "
                                            "make this request")
        
        #if the tuser is given the tuser Person object should be returned
        if tuser and request.user.has_perm('opensocial_people.data_view'):
            person_object = Person.objects.filter(user__username = tuser)
            
        elif tuser:
            return HttpResponseForbidden("You are not permitted"
                                         " to make this request")
        #get the right person for user
        elif user == '@me' or user == request.user.username:
            person_object = Person.objects.filter(user = request.user)
 
        elif request.user.has_perm('opensocial_people.data_view'):
            person_object = Person.objects.filter(user__username = user)
            
        else:
            return HttpResponseForbidden("You are not permitted"
                                         " to make this request")
        
        
        #get the time parameter from get parameters TODO
        time = datetime.today()
            
        #query the time
        person_object = person_object.filter(
            Q(time__create_time__lte = time),
            Q(time__expire_time__gte=time) | Q(time__expire_time = None))
        
        #default person includes django user values
        default_person = {
            "id": request.user.id,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": {
                "value": request.user.email,
                "type": "",
                "primary": True
            }
        }
        if len(person_object) == 0:
            return HttpResponse(json.dumps(default_person))
        elif len(person_object) == 1:
            json.loads(person_object[0].json.json_string).update(default_person)
            return HttpResponse(json.dumps(default_person))
        else:
            retobj = {
                "totalResults": len(person_object),
                "entry": []
            }
            for person in person_object:
                retobj.append(json.loads(person_object[0].json.json_string).update(default_person))
            
            return HttpResponse(json.dumps(retobj))
        
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
    
    relationship = Relationship(initial_user = iuser,
                                group = gtype,
                                target_user = tuser)
    
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