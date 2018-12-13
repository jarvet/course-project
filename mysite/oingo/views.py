from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from oingo.models import Filter, Tag


@login_required
def hello(request):
    return HttpResponse("Hello world")


def login(request):
    if request.session.get('username', ''):
        return HttpResponseRedirect(reverse('oingo:index'))
        # return HttpResponseRedirect(reverse('oingo:hello'))
    status = ''
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
                        return HttpResponseRedirect(reverse('oingo:index'))
                        # return HttpResponseRedirect(reverse('oingo:hello'))
                    else:
                        status = 'not_active'
                else:
                    status = 'pwd_err'
            else:
                status = 'not_exist'
    content = {'status': status}
    return render(request, 'oingo/login.html', content)

def register(request):
    if request.session.get('username', ''):
        return HttpResponseRedirect(reversed('oingo:index'))
        # return HttpResponseRedirect(reverse('oingo:hello'))
    status = ''
    if request.POST:
        post = request.POST
        if 'register' in post:
            username = post['new_username']
            email = post['new_email']
            password = post['new_password']
            repassword = post['new_repassword']
            if password != repassword:
                status = 're_err'
            else:
                if User.objects.filter(username=username):
                    status = 'user_exist'
                else:
                    new_user = User.objects.create_user(username=username, password=password, email=email)
                    new_user.save()
                    status = 'success'
                    auth.login(request, new_user)
                    request.session['username'] = new_user.username
                    request.session['userid'] = new_user.id
                    return HttpResponseRedirect(reverse('oingo:index'))
    content = {'status': status}
    return render(request, 'oingo/signup.html', content)

@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('oingo:login'))

@login_required
def show_profile(request, user_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    profile_user = User.objects.get(id=user_id)
    content = {
        'username': username,
        'userid': userid,
        'profile_user': profile_user,
        # 'profile_uid': profile_user.id,
        # 'profile_username': profile_user.username,
        # 'profile_email': profile_user.email,
        # 'profile_state': profile_user.profile.state,
        # 'profile_lon': profile_user.profile.last_lon,
        # 'profile_lat': profile_user.profile.last_lat
    }
    return render(request, 'oingo/profile.html', content)

@login_required
def edit_profile(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    post = request.POST
    if post:
        user.profile.state = post.get('new_state', '')
        user.save()
        return HttpResponseRedirect(reverse('oingo:profile', args=(userid,)))

    content = {
        'username': username,
        'userid': userid,
        'profile_user': user,
    }
    return render(request, "oingo/edit_profile.html", content)


def send_friend_request(request, from_user, to_user):
    pass

def receive_friend_request(request, from_user, to_user):
    pass

def show_friends(request, user_id):
    pass

def publish_note(request):
    pass

# show notes
@login_required
def index(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    content = {'username': username, 'userid': userid}
    return render(request, 'oingo/index.html', content)

def post_comment(request):
    pass

def show_comment(request, nid):
    pass

@login_required
def show_filter(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    filters = Filter.objects.filter(user=user)
    content = {
        "username": username,
        "userid": userid,
        "filters": filters,
    }
    return render(request, 'oingo/filter.html', content)

@login_required
def edit_filter(request, filter_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    filter = Filter.objects.get(id=filter_id)
    post = request.POST
    if post:
        tname = post.get('tname', '')
        if tname:
            tag, created = Tag.objects.get_or_create(tname=tname)
            if created:
                tag.save()
        else:
            tag = None

        filter.start_time=_get_empty_to_none(post.get('start_time', ''))
        filter.end_time=_get_empty_to_none(post.get('end_time', ''))
        filter.repetition=_get_empty_to_none(post.get('repetition', ''))
        filter.from_date=_get_empty_to_none(post.get('from_date', ''))
        filter.to_date=_get_empty_to_none(post.get('to_date', ''))
        filter.lname=_get_empty_to_none(post.get('lname', ''))
        filter.lat=_get_empty_to_none(post.get('lat', ''))
        filter.lon=_get_empty_to_none(post.get('lon', ''))
        filter.radius=_get_empty_to_none(post.get('radius', ''))
        filter.state=_get_empty_to_none(post.get('state', ''))
        filter.tag=tag
        filter.save()
        return HttpResponseRedirect(reverse('oingo:show_filter'))
    content = {
        'username': username,
        'userid': userid,
        'filter': filter
    }
    return render(request, 'oingo/edit_filter.html', content)


@login_required
def remove_filter(request, filter_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    filter = Filter.objects.get(id=filter_id)
    filter.delete()
    content = {
        "username": username,
        "userid": userid,
    }
    return HttpResponseRedirect(reverse('oingo:show_filter'))

@login_required
def create_filter(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    post = request.POST
    if post:
        tname = post.get('tname', '')
        if tname:
            tag, created = Tag.objects.get_or_create(tname=tname)
            if created:
                tag.save()
        else:
            tag = None

        new_filter = Filter(
            user=user,
            start_time=_get_empty_to_none(post.get('start_time', '')),
            end_time=_get_empty_to_none(post.get('end_time', '')),
            repetition=_get_empty_to_none(post.get('repetition', '')),
            from_date=_get_empty_to_none(post.get('from_date', '')),
            to_date=_get_empty_to_none(post.get('to_date', '')),
            lname=_get_empty_to_none(post.get('lname', '')),
            lat=_get_empty_to_none(post.get('lat', '')),
            lon=_get_empty_to_none(post.get('lon', '')),
            radius=_get_empty_to_none(post.get('radius', '')),
            state=_get_empty_to_none(post.get('state', '')),
            tag=tag,
        )
        new_filter.save()
        return HttpResponseRedirect(reverse('oingo:show_filter'))
    content = {
        'username': username,
        'userid': userid
    }
    return render(request, 'oingo/create_filter.html', content)

def _get_empty_to_none(val):
    return val if val else None