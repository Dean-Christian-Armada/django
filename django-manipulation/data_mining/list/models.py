from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
import datetime, random, string, hashlib

# Create your models here.
class Userlevel(models.Model):
	userlevel = models.CharField(max_length=50, null=True)
	def __unicode__(self):
		return self.userlevel

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
	userlevel = models.ForeignKey(Userlevel, default=1)
	code = models.CharField(max_length = 4, null = False, editable = False)
	title = models.CharField(max_length = 5, null=True, choices=TITLE_CHOICES)
	name = models.CharField(max_length=100, null=True, unique=True)
	username = models.CharField(max_length=100, null= True, unique=True)
	password = models.CharField(max_length=100, null=True )
	old_password = models.CharField(max_length=100, null=True, editable=False)
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
		if self.old_password is None: 
			self.password = hashlib.md5(self.password).hexdigest()
			self.old_password = self.password
		elif self.old_password != self.password:
			self.password = hashlib.md5(self.password).hexdigest()
			self.old_password = self.password
		else:
			pass
		for field_name in ['name', 'city']:
			val = getattr(self, field_name, False)
			if val:
				setattr(self, field_name, val.title())
		super(Members, self).save(*args, **kwargs)

	def __unicode__(self):
		return self.name
		
	class Meta:
		verbose_name_plural = "Bio"

class Marines(models.Model):
	members = models.OneToOneField(Members)
	picture = models.ImageField(upload_to='profile_images', blank=True)
	cert_name = models.CharField(max_length=100, default='N/A')
	cert_number = models.CharField(max_length=20, default='N/A')
	date_issue = models.DateField(null=True)
	date_expire = models.DateField(null=True)

	def __unicode__(self):
		return self.members.name

	class Meta:
		verbose_name_plural = "Certificates"

class Dashboard(models.Model):
	members = models.ForeignKey(Members, default=1)
	activity = models.CharField(max_length=100, null=True)
	description = models.CharField(max_length=100, null=True)