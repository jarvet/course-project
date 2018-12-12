from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse


@login_required
def hello(request):
    return HttpResponse("Hello world")


def login(request):
    if request.session.get('username', ''):
        # return HttpResponseRedirect(reversed('oingo:index'))
        return HttpResponseRedirect(reverse('oingo:hello'))
    status = ''
    email = ''
    if request.POST:
        post = request.POST
        if 'login' in post:
            email = post['email']
            password = post['password']
            unchecked_user = User.objects.get(email=email)
            if unchecked_user:
                user = auth.authenticate(username=unchecked_user.username, password=password)
                if user is not None:
                    if user.is_active:
                        auth.login(request, user)
                        request.session['username'] = user.username
                        request.session['userid'] = user.id
                        # return HttpResponseRedirect(reverse('oingo:index'))
                        return HttpResponseRedirect(reverse('oingo:hello'))
                    else:
                        status = 'not_active'
                else:
                    status = 'pwd_err'
            else:
                status = 'not_exist'
    content = {'status': status}
    return render(request, 'oingo/login.html', content)

def register(request):
    pass

def logout(request):
    pass

def show_profile(request, uid):
    pass

def edit_profile(request, uid):
    pass

def send_friend_request(request, from_user, to_user):
    pass

def receive_friend_request(request, from_user, to_user):
    pass

def show_friends(request, uid):
    pass

def publish_note(request):
    pass

# show notes
def index(request):
    pass

def post_comment(request):
    pass

def show_comment(request, nid):
    pass

def show_filter(request):
    pass

def edit_filter(request):
    pass

def create_filters(request):
    pass

