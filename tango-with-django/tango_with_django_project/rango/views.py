from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from rango.bing_search import run_query
from hashlib import sha1
from django.contrib.auth.models import User

# Create your views here.
def index(request):
	#request.session.set_test_cookie()
	#return HttpResponse('<p>Rango says hey there world!</p><a href = "about">Link to about page</a>')
	#context_dict = { 'boldmessage': "I am bold font from the context" }
	

	visits = int(request.COOKIES.get('visits', 1))
	category_list = Category.objects.order_by('-likes')[:5]
	pages_list = Page.objects.order_by('-views')[:5]
	context_dict = { 'categories': category_list, 'pages': pages_list, 'visits':visits }
	template = 'rango/index.html'

	reset_last_visit_time = False
	response = render(request, template, context_dict)
	# Does the cookie last_viist exists?
	if 'last_visit' in request.COOKIES:
		# Yes it does! Get the cookie's value
		last_visit = request.COOKIES['last_visit']
		# Cast the value to a Python date/time object.
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

		# If it's been more than a day since the last visit...
		if (datetime.now() - last_visit_time).seconds > 5:
			visits = visits + 1
			# ...and flag that the cookie last visit needs to be updated
			reset_last_visit_time = True
	else:
		# Cookie last_visit doesn't exist, so flag that it should be set.
		reset_last_visit_time = True
		context_dict['visits'] = visits

		# Obtain our Response object early so we can add cookie information.
		response = render(request, template, context_dict)

	if reset_last_visit_time:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)

	# Return response back to the user, updating any cookies that need changed.
	return response

def about(request):
	#return HttpResponse('<p>Rango says here is the about page</p><a href = "/rango/">Link to main page</a>')
	context_dict = { 'boldmessage': "This is the about page" }
	template = 'rango/about.html'

	# If the visits session variable exists, take it and use it.
	# If it doesn't, we haven't visited the site so set the count to sero
	if request.COOKIES.get('visits'):
		count = request.COOKIES.get('visits')
	else:
		count = 0
	context_dict['visits'] = count

	return render(request, template, context_dict)
def category(request, category_name_slug):
	context_dict = {'slug' : category_name_slug}
	template = 'rango/category.html'
	result_list = []

	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run our Bing function to get the results list!
			result_list = run_query(query)
			context_dict['result_list'] = result_list
	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		# Retrieve all of the associated pages.
		# Note that filter returns >= 1 model instance.
		pages = Page.objects.filter(category=category).order_by('-views')

		# Adds our results list to the  template context under name pages.
		context_dict['pages'] = pages
		# We also add the category object from the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here if we didn't find the specified category.
		# Don't do anything - the template display the "no category" message for us.
		pass

	# Go render the reponse and return it to the client.
	return render(request, template, context_dict)

@login_required
def add_category(request):

	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)

			# Now call the index() view.
			# The user will be shown the homepage
			return index(request)
		else:
			# The supploed form contained errors - just print them to the terminal.
			print form.errors
	elif request.method == 'GET':
		form = CategoryForm()
		if 'add_page' in request.GET and 'add_url' in request.GET:
			add_page = request.GET.get('add_page')
			add_url = request.GET.get('add_url')
			category_name = request.GET.get('category_name')
			category_name = Category.objects.get_or_create(name=category_name)[0]
			page = Page.objects.get_or_create(title=add_page, url=add_url, category=category_name)[0]
			page.save()
			return HttpResponseRedirect('/rango/')
			#return HttpResponsere(add_page)
	else:
		# If the request was not a POST, display the form to enter details.
		form = CategoryForm()
	# Bad form(or form details), no form supplied...
	# Render the form with error message (if any).
	template = 'rango/add_category.html'
	context_dict = {'form': form}
	return render(request, template, context_dict)

@login_required
def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				# probably better to use a redirect here.
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()
	context_dict = {'form': form, 'category': cat}
	template = 'rango/add_page.html'
	return render(request, template, context_dict)

def register(request):
	# if request.session.test_cookie_worked():
	# 	print ">>>>> TEST COOKIE WORKED!"
	# 	request.session.delete_test_cookie()
	# A boolean value for telling the template whether the registration was successful.
	# Set to False initially. Code changes value to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		# Note that we make use of both UserForm and UserProfileForm.
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the two forms are valid...
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database
			user = user_form.save()

			# Now we hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()

			# Now sort out the UserProfile instance.
			# Since we need to set the user attribute ourselves, we set commit=False.
			# This delays saving the model until we're ready to avoid integrity problems.
			profile = profile_form.save(commit = False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Now we save the UserProfile model instance
			profile.save()

			# Update our variable to tell the template registration was successful.
			registered = True

		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They'll also be shown to user.
		else:
			print user_form.errors, profile_form.errors
	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank, ready for user input.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	# Render the template depending on the context.
	template = 'rango/register.html'
	context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered }
	return render( request, template, context_dict )
def user_login(request):
	# If the request is a HTTP POST, try to pull out the relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the login form.
			# We use request.POST.get('<variable>') returns None, if the value does not exist,
			# while the request.POST['<variable>'] will raise key error exception
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Use Django's machinery to attempt to see if the username/password combination is valid - a User objet is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct.
		# If None (Python's way of representing the absence of a value), no user with matching credentials was found.
		if user:
			# Is  the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in.
				# We'll send t he user back to homepage.
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				# An inactive account was used - no logging in!
				return HttpResponse('Your Rango account is disabled.')
		else:
			# Bad login details were provided. So we can't log  the user in.
			print "Invalid login details: {0}, {1}". format(username, password)
			return HttpResponse("Invalid login details supplied.")
	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET.
	else:
		# No context variables to pass to the template system, hence the blank dictionary object...
		template = 'rango/login.html'
		context_dict = {}
		return render(request, template, context_dict)
# def some_view(request):
# 	if not request.user.is_authenticated():
# 		return HttpResponse("You are logged in.")
# 	else:
# 		return HttpResponse('You are not logged in.')
@login_required
def restricted(request):
	# return HttpResponse("Since you're logged in, you can see this text!")
	template = 'rango/restricted.html'
	context_dict = {}
	return render(request, template, context_dict)
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)

	# Take the user back  to the homepage.
	return HttpResponseRedirect('/rango/')
def search(request):
	result_list = []

	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			# Run our Bing function to get the results list!
			result_list = run_query(query)
	template = 'rango/search.html'
	context_dict =  { 'result_list': result_list }
	return render(request, template, context_dict)
def track_url(request, page_id):
	if request.method == 'GET':
		if page_id:
			page = Page.objects.get(id=page_id)
			page.views = page.views + 1
			page.save()
			return HttpResponseRedirect(page.url)
		else:
			return HttpResponseRedirect('/rango/')

@login_required
def register_profile(request):
	# if request.method == 'POST':
	# 	profile_form = UserProfileForm()
	# 	username = request.POST.get('username')
	# 	email = request.POST.get('email')
	# 	password = request.POST.get('password1')
	# 	context_dict = { 'username':username, 'email':email, 'password': password, 'profile_form': profile_form}
	

	if request.method == 'POST':
		user = request.user
		profile_form = UserProfileForm(data=request.POST)
		if profile_form.is_valid():
			profile = profile_form.save(commit = False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			return HttpResponseRedirect('/rango/')
		else:
			print user_form.errors, profile_form.errors
	else:
		profile_form = UserProfileForm()
		context_dict = {'profile_form': profile_form}
		template = 'rango/profile_registration.html'
		return render(request, template, context_dict)

@login_required
def profile(request):
	if request.method == 'POST':
		# return HttpResponse('Dean')
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			username = request.POST.get('username')
			password = request.POST.get('password')
			email = request.POST.get('email')
			website = request.POST.get('website')
			picture =  request.FILES['picture']
			user = request.user
			id = request.user.id
			# return HttpResponse(user)

			userprofile = UserProfile.objects.get(user_id=id)
			userprofile.website = website
			if 'picture' in request.FILES:
				userprofile.picture = picture
			userprofile.save()

			user = User.objects.get(username=user)
			user.username = username
			user.email = email
			user.set_password(password)
			user.save()
			
			
			return HttpResponseRedirect('/rango/')
		else:
			print user_form.errors, profile_form.errors
			# return HttpResponse('Armada')
	else:
		id = request.user.id
		username = request.user.username
		password = request.user.password
		email = request.user.email
		userprofile = UserProfile.objects.get(user_id=id)
		website = userprofile.website
		picture = userprofile.picture
		user_form = UserForm(initial={'username': username, 'password': password, 'email': email })
		profile_form = UserProfileForm(initial={ 'website': website, 'picture': picture })
	template = 'rango/profile.html'
	# return HttpResponse(password)
	context_dict = { 'user_form': user_form, 'profile_form': profile_form}
	return render(request, template, context_dict)
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
	likes = 0
	if cat_id:
		cat = Category.objects.get(id=int(cat_id))
		if cat:
			likes = cat.likes + 1
			cat.likes = likes
			cat.save()
	return HttpResponse(likes)
def get_category_list(max_results=0, starts_with=''):
	# return {'cats': Category.objects.all(), 'act_cat': cat }
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__istartswith=starts_with)
	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]
	return cat_list
def suggest_category(request):
	cat_list = []
	starts_with = ''
	template = 'rango/cats.html'
	if request.method == 'GET':
		starts_with = request.GET['suggestion']
	cat_list = get_category_list(8, starts_with)
	return render(request, template, { 'cats': cat_list })
	# return HttpResponse(starts_with)
@login_required
def auto_add_page(request):
	cat_id = None
	url = None
	title = None
	context_dict = {}
	template = 'rango/page_list.html'
	if request.method == 'GET':
		cat_id = request.GET['category_id']
		url = request.GET['url']
		title = request.GET['title']
		if cat_id:
			category = Category.objects.get(id=int(cat_id))
			p = Page.objects.get_or_create(category=category, title = title, url=url)
			pages = Page.objects.filter(category=category).order_by('-views')

			# Adds our results list to the template context under name pages
			context_dict['pages'] = pages


	return render(request, template, context_dict)
	# return HttpResponse(cat_id+url+title)
@login_required
def auto_delete_page(request):
	cat_id = None
	page_id = None
	context_dict = {}
	template = 'rango/page_list.html'
	if request.method == 'GET':
		page_id = request.GET['page_id']
		cat_id = request.GET['category_id']
		if page_id:
			category = Category.objects.get(id=int(cat_id))
			p = Page.objects.get(id=page_id)
			p.delete()
			pages = Page.objects.filter(category=category).order_by('-views')	

			context_dict['pages'] = pages
	return render(request, template, context_dict)
	# return HttpResponse(cat_id+' '+page_id)