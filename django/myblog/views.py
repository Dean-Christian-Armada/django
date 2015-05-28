from django.shortcuts import render_to_response, get_object_or_404 # to display our template
from .models import Blog, Category, Author
import csv

# Create your views here.
def index(request):
	return render_to_response('index.html', { # sets the template file that we are going to be using
		'categories': Category.objects.all(), # queries the database for categories
		'authors': Author.objects.all(),
		'posts': Blog.objects.all()[:5] # queries the database for posts
	})
def view_post(request, slug):
	return render_to_response('view_post.html', {
		'post': get_object_or_404(Blog, slug=slug) # This queries the database trying to match where slug=slug, the first slug being the field in the model, the second slug being the input into the function call, more on this in a second when we define the URLS.
	})
def view_category(request, slug):
	category = get_object_or_404(Category, slug=slug)
	return render_to_response('view_category.html', {
		'categories': Category.objects.all(), # queries the database for categories
		'authors': Author.objects.all(),
		'category': category,
		'posts': Blog.objects.filter(category=category)[:5]
	})
def view_author(request, slug):
	author = get_object_or_404(Author, slug=slug)
	return render_to_response('view_author.html', {
		'categories': Category.objects.all(), # queries the database for categories
		'authors': Author.objects.all(),
		'author': author,
		'posts': Blog.objects.filter(author=author)[:5]
	})
# def 