# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.template.context import RequestContext
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import *
from django.db.models import Count
from .forms import *
from django.views.generic import ListView
from django.views.generic.base import RedirectView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts, get_default_password_validators, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from notify.signals import notify
import numpy as np
from PIL import Image
import requests
import pickle

def index(request):
    return render(request, 'index.html')

def pet_list(request):
    pet_list = Pet.objects.all()
    return render(request, 'pet_list.html', {'pet_list': pet_list})

def find_pet(request):
    image_form = SearchFrom(request.POST or None, request.FILES)

    if image_form.is_valid():
        img = Image.open(image_form.cleaned_data.get("image"))
        data = np.array(img,dtype=np.float32)
        print(data.shape)
        url = "http://localhost:5050/classify"
        print("post file")
        r = requests.post(url,data=pickle.dumps(data[:,:,:3]))
        print("get respone")
        return HttpResponseRedirect(reverse('pet:pet detail', kwargs={'pet_code': r.content}))
    else:
        messages.error(request, "Error") 

def user_profile(request, user_id):
    try:
        user_to_display = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'user_profile.html', {'user_to_display': user_to_display})

def my_profile(request):
    return render(request, 'my_profile.html')

def edit_profile(request):
    user = request.user
    edit_form = EditProfileForm(request.POST or None, request.FILES)
    # print edit_form
    if request.method == 'POST':
        if edit_form.is_valid():
            user.first_name = edit_form.cleaned_data['first_name']
            user.last_name = edit_form.cleaned_data['last_name']
            user.email = edit_form.cleaned_data['email']
            user.userprofile.gender = edit_form.cleaned_data['gender']
            user.userprofile.dateOfBirth = edit_form.cleaned_data['dateOfBirth']
            user.userprofile.avatar = edit_form.cleaned_data['avatar']
            user.save()
            user.userprofile.save()
            return HttpResponseRedirect(reverse('pet:current user profile'))
        else:
            messages.error(request, "Error") 
    context = {
        'edit_form': edit_form
    }
    return render(request, "edit_profile.html", context)

def user_list(request, filter_type):
    user = request.user.userprofile
    object_list = UserProfile.objects.exclude(id = user.id)
    if filter_type == 'followers':
        object_list = sorted(object_list, key=lambda x: -len(x.followers.all()))
    elif filter_type == 'purchases':
        object_list = sorted(object_list, key=lambda x: -len(x.purchases.all()))

    return render(request, 'users.html', context={'object_list': object_list})

def user_follow(request, user_id):
    try:
        user_to_follow = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    current_user = request.user.userprofile
    user_to_follow.userprofile.followers.add(current_user)
    
    notify.send(current_user, recipient=user_to_follow, actor=current_user, \
    verb='followed you.', nf_type='followed_by_one_user')

    return render(request, 'user_profile.html', context={'user_to_display': user_to_follow})

def user_unfollow(request, user_id):
    try:
        user_to_unfollow = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    current_user = request.user.userprofile
    user_to_unfollow.userprofile.followers.remove(current_user)
    return render(request, 'user_profile.html', context={'user_to_display': user_to_unfollow})


def pet_detail(request, pet_code):
    try:
        pet = Pet.objects.get(petCode=pet_code)
    except Pet.DoesNotExist:
        raise Http404("Pet does not exist")

    gallery = pet.petgallery_set.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(gallery, 15)
    
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)

    return render(request, 'pet_detail.html', {'pet': pet, 'images': images})

class Pet_follow(RedirectView):
    pattern_name = 'pet follow'
    def get_redirect_url(self, *args, **kwargs):
        try:
            pet_to_follow = Pet.objects.get(pk=self.kwargs.get('pet_id'))
        except Pet.DoesNotExist:
            raise Http404("Pet does not exist")

        current_user = self.request.user.userprofile
        pet_to_follow.followers.add(current_user)
        return pet_to_follow.get_absolute_url()

class Pet_unfollow(RedirectView):
    pattern_name = 'pet unfollow'
    def get_redirect_url(self, *args, **kwargs):
        try:
            pet_to_unfollow = Pet.objects.get(pk=self.kwargs.get('pet_id'))
        except Pet.DoesNotExist:
            raise Http404("Pet does not exist")

        current_user = self.request.user.userprofile
        pet_to_unfollow.followers.remove(current_user)
        return pet_to_unfollow.get_absolute_url()

class LikeImage(RedirectView):
    pattern_name = 'like image'

    def get_redirect_url(self, *args, **kwargs):
        im = PetGallery.objects.get(pk=self.kwargs.get('im_id'))
        pet_code = self.kwargs.get('pet_code')
        pet = Pet.objects.get(petCode=pet_code)
        user = self.request.user.userprofile
        url_ = pet.get_absolute_url()
        if user in im.users_like.all():
            im.users_like.remove(user)
        else:
            im.users_like.add(user)
        return url_

class LikeImageAPI(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, im_id, pet_code, format=None):
        im = PetGallery.objects.get(pk=im_id)
        pet = Pet.objects.get(petCode=pet_code)
        user = self.request.user.userprofile
        url_ = pet.get_absolute_url()
        updated = False
        liked = False
        if user.user.is_authenticated():
            if user in im.users_like.all():
                im.users_like.remove(user)
                liked = False
            else:
                im.users_like.add(user)
                liked = True

            updated = True

        data = {
            "updated": updated,
            "liked": liked
        }

        return Response(data)


def purchases(request, filter_type, pet_type):
    if pet_type == 'all':
        object_list = Purchase.objects.all()
    else:
        object_list = Purchase.objects.all().filter(pet__petType=pet_type)
    object_list = object_list.filter(available=True)
    return render(request, 'purchases.html', 
                  context={'typeFilter': filter_type, 'typePet': pet_type, 'object_list': object_list})

def pet_custom_purchases(request, pet_code, filter_type):
    object_list = Purchase.objects.all().filter(pet__petCode=pet_code)
    try:
        pet = Pet.objects.get(petCode=pet_code)
    except Pet.DoesNotExist:
        raise Http404("Pet does not exist")
    object_list = object_list.filter(available=True)
    return render(request, 'pet_custom_purchases.html', 
                  context={'typeFilter': filter_type, 'pet': pet, 'object_list': object_list})

def other_users_purchases(request, user_id, filter_type, pet_type):
    if pet_type == 'all':
        object_list = Purchase.objects.all()
    else:
        object_list = Purchase.objects.all().filter(pet__petType=pet_type)
    try:
        current_user = request.user.userprofile
        user = User.objects.get(pk=user_id).userprofile
    except User.DoesNotExist:
        raise Http404("User does not exist")

    object_list = object_list.filter(owner=user)
    return render(request, 'purchases.html', 
                  context={'typeFilter': filter_type, 'typePet': pet_type, 'object_list': object_list,\
                            'cur_user': current_user, 'user': user})

def purchase_follow(request,purchase_id):
    try:
        purchase_to_follow = Purchase.objects.get(pk=purchase_id)
    except Purchase.DoesNotExist:
        raise Http404("Purchase does not exist")
    current_user = request.user.userprofile
    purchase_to_follow.subscribers.add(current_user)

    return render(request, 'purchase_detail.html', context={'purchase': purchase_to_follow})

def purchase_unfollow(request,purchase_id):
    try:
        purchase_to_unfollow = Purchase.objects.get(pk=purchase_id)
    except Purchase.DoesNotExist:
        raise Http404("Purchase does not exist")
    current_user = request.user.userprofile
    purchase_to_unfollow.subscribers.remove(current_user)

    return render(request, 'purchase_detail.html', context={'purchase': purchase_to_unfollow})


def add_purchase(request):
    user = request.user
    form = PurchaseForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            purchase = Purchase.objects.create(timeCreate=datetime.datetime.now(), owner= user.userprofile)
            purchase.price = form.cleaned_data['price']
            purchase.description = form.cleaned_data['description']
            purchase.phone = form.cleaned_data['phone']
            pet = form.cleaned_data['pet']
            purchase.pet = pet
            purchase.image = form.cleaned_data['image']
            purchase.save()
            following_users = [u.user for u in pet.followers.all()]
            if len(following_users) > 0:
                notify.send(request.user, recipient_list=following_users, actor=pet,
                            verb='added', target = purchase, nf_type='new_purchase')
            return HttpResponseRedirect(reverse('pet:pet purchases', kwargs={'filter_type': 'price', 'pet_type':'all'}))
    context = {
        "form": form,
    }
    return render(request, "add_purchase.html", context)

def purchase_detail(request, purchase_id):
    try:
        purchase = Purchase.objects.get(pk = purchase_id)
    except Purchase.DoesNotExist:
        raise Http404("Purchase does not exist")
    comment_form = CommentForm(request.POST or None)

    if request.method == 'POST':
        if comment_form.is_valid():
            new_comment = Comment.objects.create(post = purchase, author = request.user)
            new_comment.text = comment_form.cleaned_data['text']
            new_comment.save()
            notify.send(request.user, recipient=purchase.owner.user, actor= request.user,
                        verb='commented on your ', target=purchase, nf_type='comment')
            return render(request, 'purchase_detail.html', {'purchase': purchase})
    
    return render(request, 'purchase_detail.html', {'purchase': purchase, 'comment_form': comment_form})

def my_purchases(request, filter_type, pet_type):
    userprofile = request.user.userprofile

    if pet_type == 'all':
        object_list = userprofile.purchases.all()
    else:
        object_list = userprofile.purchases.all().filter(pet__petType=pet_type)
    if filter_type == 'subscribers':
        object_list = sorted(object_list, key=lambda x: -
                             len(x.subscribers.all()))

    return render(request, 'my_purchases.html', 
            context={'typeFilter': filter_type, 'typePet': pet_type, 'object_list': object_list})

def edit_purchase(request, purchase_id):
    purchase = Purchase.objects.get(pk=purchase_id)
    edit_form = EditPurchaseForm(request.POST or None, request.FILES)
    if request.method == 'POST':
        if edit_form.is_valid():
            purchase.price = edit_form.cleaned_data['price']
            purchase.description = edit_form.cleaned_data['description']
            purchase.available = edit_form.cleaned_data['available']
            purchase.phone = edit_form.cleaned_data['phone']
            purchase.save()
            following_users = [u.user for u in purchase.subscribers.all()]
            notify.send(request.user, recipient_list=following_users, actor=purchase,
                        verb='modified', nf_type='edit_purchase')
            return HttpResponseRedirect(reverse('pet:my purchases', kwargs={'filter_type': 'timeCreate', 'pet_type': 'all'}))
        else:
            messages.error(request, "Error")
    context = {
        'form': edit_form,
        'purchase': purchase        
    }
    return render(request, "edit_purchase.html", context)

def register_complete(request):
    form = RegisterForm(request.POST or None)

    context = {
        "form": form,
        "error": None,
    }
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                validate_password(password)
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            email=email, password=password)
                user.save()                                       
                return render(request, 'registration/registration_complete.html')
            except ValidationError:
                print(password_validators_help_texts(get_default_password_validators()))
                context['error'] = password_validators_help_texts(get_default_password_validators())

    return render(request, "registration/registration_form.html", context)

