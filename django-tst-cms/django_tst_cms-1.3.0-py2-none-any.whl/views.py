from django.views.generic import TemplateView
#from home.forms import HomeForm
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect

import json, pytz, requests

import ast

#from django.contrib.auth.models import User



def home(request):
    user = request.user
    args = {'user': user}
    return render(request, 'alerts/home.html', args)

