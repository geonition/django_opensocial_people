from django.db import models
from django.contrib.auth.models import User, Group

"""
class SoftgisGroup(models.Model):
    group = models.ForeignKey(Group)
    private = models.BooleanField()
    
class Person(models.Model):
    user = models.ForeignKey(User)
    group_invitations =  models.ManyToManyField(SoftgisGroup, verbose_name="group_invitations")
    groups_owned = models.ManyToManyField(SoftgisGroup, verbose_name="groups_owned")
"""    