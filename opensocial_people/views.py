from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.utils import translation
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User, Group
import logging
import sys

if sys.version_info >= (2, 6):
    import json
else:
    import simplejson as json

# set the ugettext _ shortcut
_ = translation.ugettext

logger = logging.getLogger('api.open_social.view')


def groups(request, user_id, group_id):
    """
    This function handles the groups administration part of the softgis REST api
    
    On GET request this function returns the group(s) the user is enorlled in
    If group_id specified than it returns the details of that group
    
    
    Returns:
        200 if successful and user exists
        400 if bad request
        409 forbiden if not logged in

    """
   
    if (user_id == ""):
        logger.warning("The user_id can not be empty")
        return HttpResponseBadRequest("Specify the user_id for the group request")
        
    #check if authenticated
    if not request.user.is_authenticated():
        return HttpResponseForbidden(_(u"You haven't signed in."))
        
    
        
    if(request.method == "GET"):
    
        if group_id == None:
           
            groups = User.objects.get(pk=user_id).groups.all()
            group_collection = {"result" : { "entry" : []} }
            for g in groups:
                group_collection.get("result").get("entry").append({"id" : g.id, "title" : g.name})

            return HttpResponse(json.dumps(group_collection),
                        mimetype="application/json")    
        else:    
            group = User.objects.get(pk=user_id).groups.all().get(pk=group_id)
            
            group_details  = {"id" : group.id, "title" : group.name}

            return HttpResponse(json.dumps(group_details),
                        mimetype="application/json")    
        
  