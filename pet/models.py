# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from annoying.fields import AutoOneToOneField
from django.db.models import signals
from django.urls import reverse
import datetime
# Create your models here.


class Pet(models.Model):
    dog = 'Chó'
    cat = 'Mèo'
    pet_choices = ((dog, 'Dog'), (cat, 'Cat'))
    petType = models.CharField(choices = pet_choices, max_length = 10)
    petName = models.CharField(max_length=100)
    petCode = models.CharField(max_length=100, unique = True)
    petHistory = models.TextField(blank=True, null=True)
    petAppearance = models.TextField(blank=True, null=True)
    petHabit = models.TextField(blank=True, null=True)
    lifeSpan_min = models.IntegerField(
        default=10,
        validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    lifeSpan_max = models.IntegerField(
        default=5,
        validators=[MaxValueValidator(50), MinValueValidator(1)]
    )
    others = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.petName

    def get_absolute_url(self):
        return reverse("pet:pet detail", kwargs={"pet_code": self.petCode})

class PetGallery(models.Model):
    image = models.ImageField(upload_to='gallery/')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    timeCreate = models.DateTimeField(auto_now_add=True, blank=True)

    def __unicode__(self):
        return self.pet.petName

    def get_api_like_url(self):
        return reverse('pet:like image api', kwargs={"pet_code": self.pet.petCode, "im_id": self.id})

class UserProfile(models.Model):
    user = AutoOneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='user_avatars', default='user_avatars/default-avatar.jpg')
    male = 'Nam'
    female = 'Nữ'
    gender_choices = ((male, 'Male'), (female, 'Female'))
    gender = models.CharField(choices=gender_choices, max_length=10)
    dateOfBirth = models.DateField(default=datetime.date.today)
    intro = models.TextField(max_length=100, default="")
    phone = models.CharField(max_length=15, default="")
    follows = models.ManyToManyField("self", related_name='followers', symmetrical=False,
                                     blank=True)
    favorite_pet = models.ManyToManyField(
        Pet, related_name='followers', blank=True)
    liked_images = models.ManyToManyField(PetGallery, related_name='users_like', blank=True)
    
    def __str__(self):
        return self.user.username

class Purchase(models.Model):
    available = models.BooleanField(default = True)
    timeCreate = models.DateTimeField(auto_now_add=True, blank=True)
    price = models.FloatField(default=0)
    image = models.ImageField(upload_to='upload/', default='upload/non-im.jpg')
    description = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='pet_purchases', blank=True, null=True)
    owner = models.ForeignKey(UserProfile, related_name = 'purchases' ,on_delete=models.CASCADE)
    subscribers = models.ManyToManyField(UserProfile, related_name = 'subscribed_purchases', blank = True)

    def __unicode__(self):
        return self.pet.petName + ": %.0f" % self.price + 'VNĐ'

    class Meta:
        ordering = ('timeCreate', 'price', 'available')


class Comment(models.Model):
    post = models.ForeignKey(Purchase, related_name='comments')
    author = models.ForeignKey(User, related_name='user_comments')
    text = models.TextField(default = "")
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

def create_userprofile(sender, instance, created, **kwargs):
    """Create userprofile for every new user."""
    if created:
        instance.userprofile.save()

signals.post_save.connect(create_userprofile, sender=User, weak=False,
                          dispatch_uid='create_userprofile')
