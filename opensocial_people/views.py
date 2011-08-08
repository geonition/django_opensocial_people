from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.utils import translation
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from django.db import transaction
from geonition_utils.HttpResponseExtenders import HttpResponseNotImplemented
from geonition_utils.HttpResponseExtenders import HttpResponseCreated
from geonition_utils.HttpResponseExtenders import HttpResponseConflict
from models import Relationship
import logging
import sys

if sys.version_info >= (2, 6):
    import json
else:
    import simplejson as json

def people(request, *args, **kwargs):
    """
    This function handles the people service requests
    """
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        
        if request.user.is_authenticated():
            initial_user = kwargs.get('user', None)
            relationship_type = kwargs.get('group', None)
            
            if initial_user == None:
                initial_user = args[0]
                
                if relationship_type == None and len(args) > 1:
                    relationship_type = args[1]
                elif relationship_type == None:
                    relationship_type = '@friends'
            
            elif relationship_type == None:
                relationship_type = args[0]
            
            if initial_user != '@me' and request.user.username != initial_user:
                return HttpResponseForbidden("You are not allowed to create this relationship")
                
                
            return create_relationship(request, initial_user, relationship_type)
        else:
            return HttpResponseForbidden("The user needs to be authenticated to make this request")
        
    return people_not_implemented(request)


def create_relationship(request, initial_user, relationship_type):
    
    iuser = None
    if initial_user == '@me':
        iuser = request.user
    else:
        try:
            iuser = User.objects.get(username = initial_user)
        except User.DoesNotExist:
            return HttpResponseNotFound("The specified user was not found")
            
    gtype = None
    try:
        gtype = Group.objects.get(name = relationship_type)
    except Group.DoesNotExist:
        return HttpResponseNotFound("The specified group was not found")
    
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

def people_not_implemented(request):
    return HttpResponseNotImplemented("This part of people service is not implemented")