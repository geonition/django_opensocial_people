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

