from django.db import models
from django.db.models import permalink

# Create your models here.
class Blog(models.Model):
	title = models.CharField(max_length=100, unique=True)
	author = models.ForeignKey('myblog.Author')
	slug = models.SlugField(max_length=100, unique=True)
	body = models.TextField()
	posted = models.DateField(db_index=True, auto_now_add=True)
	category=models.ForeignKey('myblog.Category') # Defined as a foreign key in Category table

	def __unicode__(self):
		return '%s' % self.title
	@permalink
	def get_absolute_url(self):
		return('view_blog_post', None, {'slug': self.slug})

class Category(models.Model):
	title = models.CharField(max_length=100, db_index=True)
	slug = models.SlugField(max_length=100, db_index=True)

	def __unicode__(self): # Sets the text reference for each record
		return '%s' % self.title

	@permalink # Returns the URL
	def get_absolute_url(self):
		return ('view_blog_category', None, {'slug': self.slug})

class Author(models.Model):
	name = models.CharField(max_length=100, db_index=True)
	slug = models.SlugField(max_length=100, db_index=True)

	def __unicode__(self): # Sets the text reference for each record
		return '%s' % self.name

	@permalink # Returns the URL
	def get_absolute_url(self):
		return ('view_blog_author', None, {'slug': self.slug})

