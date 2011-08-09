from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class Relationship(models.Model):
    """ The Relationship model describes a link between two users """
    
    
    user_id = models.ForeignKey(User, related_name='initial_user')
    group_id = models.ForeignKey(Group, related_name='relationship_group')
    person = models.ForeignKey(User, related_name='target_user')
    
    class Meta:
        unique_together = ('user_id',
                           'group_id',
                           'person')
    