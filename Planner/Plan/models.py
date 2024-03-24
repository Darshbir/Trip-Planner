from django.db import models
from django.contrib.auth.models import User
from django.db.models import DateField
from django.utils import timezone
from django.core.validators import MinValueValidator
# Create your models here.

class BITSUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bits_id = models.CharField(max_length=10)
    campus = models.CharField(max_length = 10)
    batch = models.IntegerField(max_length = 10)

    class Meta:
        unique_together = [['bits_id', 'campus', 'batch']]

    def __str__(self):
        return f"{self.user.username} ({self.bits_id} {self.campus})"

class Location(models.Model):
    name = models.CharField(max_length=100)
    has_airport = models.BooleanField(default=True)
    airport_code = models.CharField(max_length=3, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name


class Trip(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(BITSUser, on_delete=models.CASCADE)
    destination = models.ForeignKey(Location, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

#multiple tentative plans for a trip
class Plan(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    creator = models.ForeignKey(BITSUser, on_delete=models.CASCADE)
    travel_cost = models.PositiveIntegerField()
    is_followed = models.BooleanField(default=False)

#multiple plans can have the same events
class Event(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE,  related_name='events')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    activities = models.TextField()
    cost = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    date = models.DateField() #No validator incase u hv to add ongng trip which could hv started a day or 2 ago
    

class Group(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_leader')
    members = models.ManyToManyField(User, related_name='group_members', blank = True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def add_member(self, user):
        self.members.add(user)

class GroupJoinRequest(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='join_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Join request from {self.requester.username} for group {self.group.name}"