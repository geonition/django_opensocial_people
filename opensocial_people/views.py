from datetime import datetime
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.utils import simplejson as json
from geonition_utils.HttpResponseExtenders import HttpResponseNotImplemented
from geonition_utils.HttpResponseExtenders import HttpResponseConflict
from geonition_utils.HttpResponseExtenders import HttpResponseCreated
from geonition_utils.HttpResponseExtenders import HttpResponseUnauthorized
from geonition_utils.views import RequestHandler
from models import Person
from models import Relationship
    
class People(RequestHandler):
    
    def __init__(self):
        pass
    
    def get_real_name(self,
                      request,
                      username=None,
                      groupname= None):
        """
        This function returns the real unique name for
        the generic name like @me or @self
        
        Returns a tuple with the username first
        and the default groupname second.
        """
        #look for the right username
        if username == '@me' or username == None:
            username = request.user.username
            
        if groupname == None:
            groupname = '@self'

        return (username, groupname)        
        
    def get(self, request, *args, **kwargs):
        
        #get the values
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)
        tuser = kwargs.get('tuser', None)
        
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized("You need to authenticate to "
                                            "make this request")
    
        names = self.get_real_name(request,
                                   username=user,
                                   groupname=group)
        user = names[0]
        group = names[1]
            
        if not request.user.has_perm('opensocial_people.data_view') \
            and request.user.username != user:
            return HttpResponseForbidden("You are not permitted "
                                         "to make this request")
        
        #create a person queryset
        person_objects = Person.objects.all()
        
        #create a relationship queryset
        relationship_objects = Relationship.objects.all()
        
        #filter the Persons according to groups
        if user and tuser and group:
            relationship_objects = relationship_objects.filter(initial_user__username = user)
            relationship_objects = relationship_objects.filter(group = group)
            relationship_objects = relationship_objects.filter(target_user__username = tuser)
        
        elif user and group:
            relationship_objects = relationship_objects.filter(initial_user__username = user)
            relationship_objects = relationship_objects.filter(group = group)
            
        #filter the persons that is not target users in the relationships
        target_user_ids = relationship_objects.values_list('target_user',
                                                           flat=True)
        
        person_objects = person_objects.filter(user__in = target_user_ids)
        
        #if the tuser is given the tuser Person object should be returned
        if tuser and request.user.has_perm('opensocial_people.data_view'):
            person_objects = person_objects.filter(user__username = tuser)    
        
        elif tuser:
            return HttpResponseForbidden("You are not permitted"
                                         " to make this request")
          
        #get the time parameter from get parameters TODO
        time = datetime.today()
        
        #query the time
        person_objects = person_objects.filter(
            Q(time__create_time__lt = time),
            Q(time__expire_time__gt=time) | Q(time__expire_time = None))
            
        if len(person_objects) == 0:
            return HttpResponseNotFound('The person or persons you requested '
                                        'for was not found')
        elif len(person_objects) == 1:
            return_person = person_objects[0].json()
            return HttpResponse(json.dumps(return_person))
        
        else:
            retobj = {
                "totalResults": len(person_objects),
                "entry": []
            }
            for person in person_objects:
                retobj['entry'].append(person.json())
                
            return HttpResponse(json.dumps(retobj))
        
    def post(self, request, *args, **kwargs):
        
        #get the values
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)
        
        names = self.get_real_name(request,
                                   username=user,
                                   groupname=group)
        user = names[0]
        group = names[1]
        
        if request.user.is_authenticated():
            initial_user = user
            relationship_type = group
                
            return create_relationship(request, initial_user, relationship_type)
        else:
            return HttpResponseUnauthorized("The user needs to be "
                                            "authenticated to make this "
                                            "request")
    def put(self, request, *args, **kwargs):
        
        #get the values, only user matters
        user = kwargs.get('user', None)
        
        names = self.get_real_name(request,
                                   username=user)
        user = names[0]
        
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized("You need to sign in to make "
                                            "this request")
            
        elif request.user.username != user:
            
            return HttpResponseUnauthorized("You can only modify your own "
                                            "profile")
        
        else:
            person = Person.objects.filter(user = request.user)
            person = person.latest('time__create_time')
            person.update(request.raw_post_data)
            
            return HttpResponse(json.dumps(person.json()),
                                content_type='application/json')
            

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