from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
import datetime, random, string

# Create your models here.
class Members(models.Model):
	GENDER_CHOICES = (
			('M', 'Male'),
			('F', 'Female'),
		)
	TITLE_CHOICES = (
			('Mr.', 'Mr.'),
			('Ms.', 'Ms.'),
			('Mrs.', 'Mrs.'),
		)
	code = models.CharField(max_length = 4, null = False, unique = True, editable = False)
	title = models.CharField(max_length = 5, null=True, choices=TITLE_CHOICES)
	name = models.CharField(max_length=100, null=True, unique=True)
	# country = models.CharField(max_length=100, null=True)
	country = CountryField()
	gender = models.CharField(max_length=100, null=True, choices=GENDER_CHOICES)
	city = models.CharField(max_length=100, null=True)
	IsActive = models.BooleanField(default=True)
	date_added = models.DateTimeField(auto_now_add=True)
	date_modified = models.DateTimeField(editable=False, null=True)

	def save(self, *args, **kwargs):
		code = ''.join([random.choice(string.uppercase) for n in xrange(4)])
		if not self.id:
			self.created = datetime.datetime.today()
		self.modified = datetime.datetime.today()
		self.code = code
		super(Members, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name

class Userlevel(models.Model):
	userlevel = models.CharField(max_length=5, null=True)

	def __unicode__(self):
		return self.userlevel

class Users(models.Model):
	user = models.OneToOneField(User)
	userlevel = models.ForeignKey(Userlevel, default=1)
	def __unicode__(self):
		return self.user

class Dashboard(models.Model):
	user = models.ForeignKey(Users, default=1)
	activity = models.CharField(max_length=100, null=True)
	description = models.CharField(max_length=100, null=True)