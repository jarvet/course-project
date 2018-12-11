from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

# def hello(request):
#     return HttpResponse("Hello world")


def login_and_register(request):
    pass

def show_profile(request, uid):
    pass

def edit_profile(request, uid):
    pass

def send_friend_request(request, from_user, to_user):
    pass

def receive_friend_request(request, from_user, to_user):
    pass

def publish_note(request):
    pass

def index(request):
    pass