from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from oingo.models import Filter, Tag, Schedule, Location, Note, Friendship, Comment


@login_required
def hello(request):
    return HttpResponse("Hello world")


def login(request):
    if request.session.get('username', ''):
        return HttpResponseRedirect(reverse('oingo:index'))
    status = ''
    if request.POST:
        post = request.POST
        if 'login' in post:
            username = post['username']
            password = post['password']
            unchecked_user = User.objects.filter(username=username)
            if unchecked_user:
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        auth.login(request, user)
                        request.session['username'] = user.username
                        request.session['userid'] = user.id
                        return HttpResponseRedirect(reverse('oingo:index'))
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

@login_required
def accept_friend_request(request, friend_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    friend = User.objects.get(id=friend_id)
    friendship = Friendship.objects.get(user=friend_id, friend=userid)
    friendship.is_request = False
    friendship.save()
    reverse_friendship = Friendship(
            user=user,
            friend=friend,
            is_request=False
        )
    reverse_friendship.save()
    return HttpResponseRedirect(reverse('oingo:show_friends'))

@login_required
def reject_friend_request(request, friend_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    friend = User.objects.get(id=friend_id)
    Friendship.objects.get(user=friend, friend=user).delete()
    return HttpResponseRedirect(reverse('oingo:show_friends'))

@login_required
def remove_friend(request, friend_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    friend = User.objects.get(id=friend_id)
    Friendship.objects.get(user=user, friend=friend).delete()
    Friendship.objects.get(user=friend, friend=user).delete()
    return HttpResponseRedirect(reverse('oingo:show_friends'))


@login_required
def show_friends(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    friendships = Friendship.objects.filter(user=user, is_request=False).distinct()
    requests = Friendship.objects.filter(friend=user, is_request=True).distinct()
    friends = [ fs.friend for fs in friendships]
    request_users = [rq.user for rq in requests]
    content = {
    'username': username,
    'userid': userid,
    'friends': friends,
    'request_users': request_users,
    }
    post = request.POST
    status = ''
    if post:
        friend_name = post.get('friend_name')
        try:
            friend = User.objects.get(username=friend_name)
        except User.DoesNotExist:
            friend = None
            status = 'user_not_exist'
        else:
            if friend in friends:
                status = 'already_friends'
            elif friend in Friendship.objects.filter(user=user, is_request=True):
                status = 'already_requested'
            else:
                new_friendship = Friendship(
                        user=user,
                        friend=friend
                    )
                new_friendship.save()
                status = 'success'
        content['status'] = status
        # return HttpResponseRedirect(request.path_info)
        return render(request, 'oingo/friend.html', content)

    return render(request, 'oingo/friend.html', content)

@login_required
def create_note(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    post = request.POST
    if post and 'save' in post:
        tnames = post.get('tags', '')
        tags = set()
        for tname in tnames.split(';'):
            tag, created = Tag.objects.get_or_create(tname=tname)
            if created:
                tag.save()
            tags.add(tag)
        schedule = Schedule(
                start_time=post.get('start_time'),
                end_time=post.get('end_time'),
                repetition=post.get('repetition'),
                from_date=post.get('from_date'),
                to_date=post.get('to_date')
            )
        schedule.save()
        location, _ = Location.objects.get_or_create(
                lname=post.get('lname'),
                lat=post.get('lat'),
                lon=post.get('lon')
            )
        location.save()
        note = Note(
                note_content=post.get('note_content'),
                visiable_group=post.get('visiable_group'),
                allow_comment=True if post.get('allow_comment')=='allow' else False,
                schedule=schedule,
                author=user,
                location=location,
                visiable_radius=post.get('visiable_radius')            )
        note.save()
        note.tags.set(tags)
        note.save()
        return HttpResponseRedirect(reverse('oingo:index'))
    content = {
        'username': username,
        'userid': userid
    }
    return render(request, "oingo/create_note.html", content)

# show notes
@login_required
def index(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    content = {'username': username, 'userid': userid}
    notes = Note.objects.all()
    content = {
        'username': username,
        'userid': userid,
        'notes': notes
    }
    return render(request, 'oingo/index.html', content)

@login_required
def add_comment(request, note_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    note = Note.objects.get(id=note_id)
    post = request.POST
    if post:
        comment_content = post.get('new_comment')
        new_comment = Comment(
                user=user,
                note=note,
                content=comment_content
            )
        new_comment.save()
        note.save()
        # return HttpResponseRedirect(reverse('oingo:add_comment', args=(note_id,)))
        # return render
    content = {
        'username': username,
        'userid': userid,
        'note': note
    }
    return render(request, 'oingo/note_detail.html', content)

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
    if post and 'save' in post:
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

#get radius between 2 points
def _get_distance(lon1, lat1, lon2, lat2):
    R = 6373.0#radius of earth in km
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance