#!/usr/bin/env python
# -*- coding: latin-1 -*-

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from app.forms import *
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from app.models import *

import string
import random
from subprocess import Popen, call, PIPE
from shlex import split

from sms import *

globalCode = ''

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold"}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('app/base.html', context_dict, context)

def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'app/registro.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

@login_required
def editar(request):
        # Like before, get the request's context.
        context = RequestContext(request)

        # A boolean value for telling the template whether the registration was successful.
        # Set to False initially. Code changes value to True when registration succeeds.
        editado = False

        # If it's a HTTP POST, we're interested in processing form data.
        profile = UserProfile.objects.get(user=request.user)
        if request.method == 'POST':
            # Attempt to grab information from the raw form information.
            # Note that we make use of both UserForm and UserProfileForm.
            #user_form = UserForm(data=request.POST)
            profile_form = UserProfileForm(data=request.POST, instance=profile)

            # If the two forms are valid...
            if profile_form.is_valid():
                # Save the user's form data to the database.
                #user = user_form.save()

                # Now we hash the password with the set_password method.
                # Once hashed, we can update the user object.
                #user.set_password(user.password)
                #user.save()

                # Now sort out the UserProfile instance.
                # Since we need to set the user attribute ourselves, we set commit=False.
                # This delays saving the model until we're ready to avoid integrity problems.
                profile = profile_form.save(commit=True)
                #profile.user = user

                # Now we save the UserProfile model instance.
                profile.save()

                # Update our variable to tell the template registration was successful.
                editado = True

            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal.
            # They'll also be shown to the user.
            else:
                print user_form.errors, profile_form.errors

        # Not a HTTP POST, so we render our form using two ModelForm instances.
        # These forms will be blank, ready for user input.
        else:
            #user_form = UserForm()
            profile_form = UserProfileForm(instance=profile)

        # Render the template depending on the context.
        return render_to_response(
                'app/editar.html',
                {'profile_form': profile_form, 'editado': editado},
                context)

@login_required
def open(request):
    context = RequestContext(request)
    match = False
    numc=''
    if request.method == 'POST': # If the form has been submitted...
        form = OpenForm(request.POST) # A form bound to the POST data
        cadena_rec = request.POST['code']
        if form.is_valid(): # All validation rules pass
            if cadena_rec == globalCode:
                match = True
                Popen(split("sudo /usr/local/bin/abrir.sh"))
    else:
        profile = UserProfile.objects.get(user=request.user)
        profile_form = UserProfileForm(data=request.POST, instance=profile)
        numc = profile.numcel
        global globalCode
        globalCode = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase ) for _ in range(5))
        form = OpenForm() # An unbound form
        Popen(split("sudo /usr/local/bin/sms.py "+str(profile.numcel)+" "+str(globalCode)))
        

    return render_to_response('app/open.html', {
        'form': form, 'match': match, 'numc': numc
    }, context)
#----------------------------------------------------------------
@login_required
def config(request):
    context = RequestContext(request)
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        if username == 'admin':
            editado = False
            cur_config = Config.objects.get(pk=1)
            if request.method == 'POST': # If the form has been submitted...
                config_form = ConfigForm(data=request.POST, instance=cur_config)
                usrs_form = EditUsersForm(data=request.POST)
                if config_form.is_valid(): #and usrs_form.is_valid():
                    configuration = config_form.save(commit=True)
                    configuration.save()
                    editado=True
                    ##
            else:
                config_form = ConfigForm(instance=cur_config)
                usrs_form = EditUsersForm()

    return render_to_response('app/config.html', {
        'config_form': config_form, 'usrs_form': usrs_form
    }, context)
#----------------------------------------------------------------
def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/app/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('app/login.html', {}, context)

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/app/')
