from django import http

def home(request):
    return http.HttpResponse('Hello World! The First AppEngine made by Dean Christian Armada!')
