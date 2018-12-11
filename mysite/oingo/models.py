# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    state = models.CharField(max_length=50, default="online")
    last_lon = models.FloatField(blank=True)
    last_lat = models.FloatField(blank=True)

    def __str__(self):
        return self.user




class Schedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    repetition = models.IntegerField()
    from_date = models.DateField()
    to_date = models.DateField()

    def __str__(self):
        return "from_date: %s, to_date: %s, start_time: %s, end_time: %s, repetition: %s" % (
            self.from_date, self.to_date, self.start_time, self.end_time, self.repetition)


class Location(models.Model):
    lname = models.CharField(max_length=50)
    lon = models.FloatField()
    lat = models.FloatField()

    def __str__(self):
        return self.lname


class Tag(models.Model):
    tname = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.tname

class Note(models.Model):
    note_content = models.TextField()
    publish_time = models.DateTimeField(auto_now=True)
    visiable_group = models.IntegerField()
    allow_comment = models.BooleanField()
    visiable_radius = models.FloatField()
    schedule = models.OneToOneField(Schedule, related_name="note", on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name="notes", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="posted_notes", on_delete=models.CASCADE)

    # for attach
    tags = models.ManyToManyField(Tag, related_name="notes")

    def __str__(self):
        return self.note_content



class Filter(models.Model):
    user = models.ForeignKey(User, related_name="filters", on_delete=models.CASCADE)
    start_time = models.TimeField(blank=True)
    end_time = models.TimeField(blank=True)
    repetition = models.IntegerField(blank=True)
    from_date = models.DateField(blank=True)
    to_date = models.DateField(blank=True)
    lname = models.CharField(max_length=50, blank=True)
    lon = models.FloatField(blank=True)
    lat = models.FloatField(blank=True)
    radius = models.FloatField(blank=True)
    state = models.CharField(max_length=50, blank=True)
    tname = models.ForeignKey(Tag, related_name="filters", on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.user, self.tname


class Area(models.Model):
    aname = models.CharField(max_length=50)
    lon = models.FloatField()
    lat = models.FloatField()
    radius = models.FloatField()
    locations = models.ManyToManyField(Location, related_name="areas")

    def __str__(self):
        return self.aname


class Friendship(models.Model):
    user = models.ForeignKey(User, related_name="friend_list", on_delete=models.CASCADE)
    firends = models.ManyToManyField(User)


class Comment(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    note = models.ForeignKey(Note, related_name="comments", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user, self.note, self.content


# class Attach(models.Model):
#     pass


# class Belong(models.Model):
#     pass


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
