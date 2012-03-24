from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import simplejson as json
from geonition_utils.HttpResponseExtenders import HttpResponseBadRequest
from geonition_utils.HttpResponseExtenders import HttpResponseNotImplemented
from geonition_utils.HttpResponseExtenders import HttpResponseConflict
from geonition_utils.HttpResponseExtenders import HttpResponseCreated
from geonition_utils.HttpResponseExtenders import HttpResponseUnauthorized
from geonition_utils.models import JSON
from geonition_utils.views import RequestHandler
from models import Person
from models import Relationship
    
class People(RequestHandler):
    
    def __init__(self):
        pass
    
    def get_real_name(self,
                      request,
                      username = None,
                      groupname = None):
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
        if request.user.has_perm('opensocial_people.data_view'):
            person_objects = Person.objects.all()
        else:
            person_objects = Person.objects.filter(user = request.user)
        
        #create a relationship queryset
        relationship_objects = Relationship.objects.all()
        
        #filter the Persons according to groups
        if user and tuser and group:
            if user != '@all':
                relationship_objects = relationship_objects.filter(initial_user__username = user)
            
            relationship_objects = relationship_objects.filter(group = group)
            relationship_objects = relationship_objects.filter(target_user__username = tuser)
        
        elif user and group:
            if user != '@all':
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
            return HttpResponseForbidden("You are not permitted "
                                         "to make this request")
          
        # handle the get parameters
        if getattr(settings, 'USE_MONGODB', False):
            
            spec = {}
            for key, value in request.GET.items():
                try:
                    value = json.loads(value)
                except ValueError:
                    pass
                
                if key.endswith('__min'):
                    key = key.replace('__min', '')
                    if spec.has_key(key):
                        spec[key].update({'$gte': value})
                    else:
                        spec[key] = {'$gte': value}
                        
                elif key.endswith('__max'):
                    key = key.replace('__max', '')
                    if spec.has_key(key):
                        spec[key].update({'$lte': value})
                    else:
                        spec[key] = {'$lte': value}
                else:
                    spec[key] = value
                
            if spec != {}:
                mqs = JSON.mongodb.find(spec,
                                        collection='opensocial_people.person')
                mqs = mqs.values_list('id', flat=True)
                person_objects = person_objects.filter(json_data__id__in = mqs)
                
        #get the time parameter from get parameters #TODO
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
            entry = []
            for person in person_objects:
                entry.append(person.json())
                
            retobj['entry'] = entry
                
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
        """
        Put requests updates an person object.
        """
        
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
            new_person = person.update(request.raw_post_data)
            
            return HttpResponse(json.dumps(new_person.json()),
                                content_type='application/json')
     
    def delete(self, request, *args, **kwargs):
        
        #get the kwargs
        user = kwargs.get('user', None)
        group = kwargs.get('group', None)
        tuser = kwargs.get('tuser', None)
        
        names = self.get_real_name(request,
                                   username=user,
                                   groupname=group)
        user = names[0]
        group = names[1]
        
        if not request.user.is_authenticated():
            return HttpResponseUnauthorized("You need to sign in to make "
                                            "this request")
            
        elif request.user.username != user:
            
            return HttpResponseUnauthorized("You can only modify your own "
                                            "relationships")
        
        else:
            relationship = Relationship.objects.filter(initial_user__username=user)
            relationship = relationship.filter(target_user__username=tuser)
            relationship = relationship.filter(group=group)
            relationship.delete()
            
            return HttpResponse("The relationship was deleted",
                                content_type='application/json')

def supported_fields(request):
    """
    This view function returns the supportedFields for the person object
    querying.
    
    This needs to be improved in some nice manner. Also performance issues
    will arrise. But works at the moment,,
    """
    
    with_types = request.GET.get('types', 'false')
    with_types = json.loads(with_types)
    
    distinct_persons = Person.objects.only('json_data__json_string').distinct()
    
    fields = {}
    for per in distinct_persons:
        fields.update(per.get_fields())
    
    if not with_types:
        fields = fields.keys()
        
    return HttpResponse(json.dumps(fields))
    
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
        if request.META['CONTENT_TYPE'] == 'application/json':
            post_dict = json.loads(request.raw_post_data)
            tuser = User.objects.get(username = post_dict.get('id', None))
        else:
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