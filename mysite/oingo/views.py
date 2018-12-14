from math import sin, cos, sqrt, atan2

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, F, ExpressionWrapper, DurationField, FloatField
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
# Create your views here.
from django.urls import reverse

from oingo.models import Filter, Tag, Schedule, Location, Note, Friendship, Comment


@login_required
def hello(request):
    return HttpResponse("Hello world")


@login_required
def set_loc_time(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    post = request.POST
    if post:
        user.profile.last_lat = post.get('lat')
        user.profile.last_lon = post.get('lon')
        user.profile.last_timestamp = post.get('current_time')
        user.save()
        return HttpResponseRedirect(reverse('oingo:index'))
    content = {
        'username': username,
        'userid': userid
    }
    return render(request, 'oingo/set_loc_time.html', content)


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
    friends = [fs.friend for fs in friendships]
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
            allow_comment=True if post.get('allow_comment') == 'allow' else False,
            schedule=schedule,
            author=user,
            location=location,
            visiable_radius=post.get('visiable_radius'))
        note.save()
        note.tags.set(tags)
        note.save()
        return HttpResponseRedirect(reverse('oingo:index'))
    content = {
        'username': username,
        'userid': userid
    }
    return render(request, "oingo/create_note.html", content)

@login_required
def own_notes(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)
    notes = Note.objects.filter(author=user)
    post = request.POST
    content = {
        'username': username,
        'userid': userid,
        'notes': notes
    }
    if post:
        keyword = post.get('keyword', '')
        search_notes = Note.objects.filter(note_content__icontains=keyword)
        content['notes'] = search_notes.intersection(notes)
    return render(request, 'oingo/index.html', content)

@login_required
def edit_note(request, note_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    note = Note.objects.get(id=note_id)
    post = request.POST
    if post:
        tnames = post.get('tags', '')
        tags = set()
        for tname in tnames.split(';'):
            tag, created = Tag.objects.get_or_create(tname=tname)
            if created:
                tag.save()
            tags.add(tag)

        note.schedule.start_time = post.get('start_time')
        note.schedule.end_time = post.get('end_time')
        note.schedule.from_date = post.get('from_date')
        note.schedule.to_date = post.get('to_date')
        note.schedule.repetition = post.get('repetition')
        note.schedule.save()

        note.location.lname=post.get('lname')
        note.location.lat=post.get('lat')
        note.location.lon=post.get('lon')
        note.location.save()

        note.note_content=post.get('note_content')
        note.visiable_group=post.get('visiable_group')
        note.allow_comment=True if post.get('allow_comment') == 'allow' else False
        note.visiable_radius=post.get('visiable_radius')
        note.save()
        note.tags.set(tags)
        note.save()
        return HttpResponseRedirect(reverse('oingo:add_comment', args=(note_id,)))
    content = {
        'username': username,
        'userid': userid,
        'note': note
    }
    return render(request, "oingo/edit_note.html", content)

@login_required
def remove_note(request, note_id):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    note = Note.objects.get(id=note_id)
    note.delete()
    content = {
        "username": username,
        "userid": userid,
    }
    return HttpResponseRedirect(reverse('oingo:index'))

# show notes
# @login_required
# def index(request):
#     username = request.session.get('username', '')
#     userid = request.session.get('userid', '')
#     content = {'username': username, 'userid': userid}
#     notes = Note.objects.all()
#     content = {
#         'username': username,
#         'userid': userid,
#         'notes': notes
#     }
#     return render(request, 'oingo/index.html', content)


@login_required
def index(request):
    username = request.session.get('username', '')
    userid = request.session.get('userid', '')
    user = User.objects.get(id=userid)

    state = user.profile.state
    cur_lat = user.profile.last_lat
    cur_lon = user.profile.last_lon
    cur_time = user.profile.last_timestamp
    friendships = Friendship.objects.filter(friend=user, is_request=False)
    friends = set([fs.user for fs in friendships])

    notes = Note.objects.filter(Q(author=user) | Q(visiable_group=2) | Q(visiable_group=1, author__in=friends))
    notes = notes.filter(schedule__start_time__lte=cur_time.time(), schedule__end_time__gte=cur_time.time())

    # date_set_notes = Note.objects.annotate(diff=ExpressionWrapper((F('schedule__to_date')-F('schedule__from_date'))%F('schedule__repetition'), output_field=DurationField())).filter(diff=0)
    date_note_id_set = set()
    for note in notes.all():
        if cur_time.date() <= note.schedule.to_date and (cur_time.date() - note.schedule.from_date).days % note.schedule.repetition == 0:
            date_note_id_set.add(note.id)
    date_notes = Note.objects.filter(id__in=date_note_id_set)
    notes = notes.intersection(date_notes)
    # distance_notes = Note.objects.annotate(dis=ExpressionWrapper(F('visiable_radius')-_get_distance(F('location__lon'), F('location__lat'), cur_lon, cur_lat), output_field=FloatField())).filter(dis__gte=0)
    distance_note_id_set = set()
    for note in notes.all():
        if (note.visiable_radius is None or note.location.lon is None or note.location.lat is None) \
                or (note.visiable_radius >= _get_distance(note.location.lon, note.location.lat, cur_lon, cur_lat)):
            distance_note_id_set.add(note.id)
    distance_notes = Note.objects.filter(id__in=distance_note_id_set)
    matching_notes = notes.intersection(distance_notes)

    # tags = set([tag for note in matching_notes for tag in note.tags])
    filters = Filter.objects.filter(Q(user=user)).filter(Q(state=state) | Q(state__isnull=True) | Q(state__exact=''))

    # filters = filters.filter(Q(start_time__lte=cur_time.time()) | Q(start_time__isnull=True))

    filters = filters.filter(Q(start_time__lte=cur_time.time()) | Q(start_time__isnull=True) )\
        .filter(Q(end_time__gte=cur_time.time())| Q(end_time__isnull=True))

    # date_set_filter = Filter.objects.annotate(diff=ExpressionWrapper((F('to_date')-F('from_date'))%F('repetition'), output_field=DurationField())).filter(diff=0)
    date_filter_id_set = set()
    for filter in filters.all():
        if (filter.from_date is None or filter.to_date is None) or (cur_time.date() < filter.to_date and (cur_time.date() - filter.from_date).days % filter.repetition == 0):
            date_filter_id_set.add(filter.id)
    date_filters = Filter.objects.filter(id__in=date_filter_id_set)

    filters = filters.intersection(date_filters)

    # distance_filters = Filter.objects.annotate(dis=ExpressionWrapper(F('visiable_radius')-_get_distance(F('lon'), F('lat'), cur_lon, cur_lat), output_field=FloatField())).filter(dis__gte=0)
    distance_filter_id_set = set()
    for filter in filters.all():
        if (filter.radius is None or filter.lon is None or filter.lat is None) \
                or (filter.radius >= _get_distance(filter.lon, filter.lat, cur_lon, cur_lat)):
            distance_filter_id_set.add(filter.id)
    distance_filters = Filter.objects.filter(id__in=distance_filter_id_set)

    matching_filters = filters.intersection(distance_filters)

    tnames = set([f.tag.tname if f.tag else None for f in matching_filters])
    if not tnames or None in tnames or '' in tnames:
        result_notes = matching_notes
    else:
        result_notes = matching_notes.filter(tags__tname__in=tnames)
    content = {
        'username': username,
        'userid': userid,
        'notes': result_notes
    }

    post = request.POST
    if post:
        keyword = post.get('keyword', '')
        search_notes = Note.objects.filter(note_content__icontains=keyword)
        content['notes'] = search_notes.intersection(result_notes)
    print(content['notes'])
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
        filter.fname = post.get('fname')
        filter.start_time = _get_empty_to_none(post.get('start_time', ''))
        filter.end_time = _get_empty_to_none(post.get('end_time', ''))
        filter.repetition = _get_empty_to_none(post.get('repetition', ''))
        filter.from_date = _get_empty_to_none(post.get('from_date', ''))
        filter.to_date = _get_empty_to_none(post.get('to_date', ''))
        filter.lname = post.get('lname', '')
        filter.lat = _get_empty_to_none(post.get('lat', ''))
        filter.lon = _get_empty_to_none(post.get('lon', ''))
        filter.radius = _get_empty_to_none(post.get('radius', ''))
        filter.state = post.get('state', '')
        filter.tag = tag
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
            fname=post.get('fname'),
            start_time=_get_empty_to_none(post.get('start_time', '')),
            end_time=_get_empty_to_none(post.get('end_time', '')),
            repetition=_get_empty_to_none(post.get('repetition', '')),
            from_date=_get_empty_to_none(post.get('from_date', '')),
            to_date=_get_empty_to_none(post.get('to_date', '')),
            lname=post.get('lname', ''),
            lat=_get_empty_to_none(post.get('lat', '')),
            lon=_get_empty_to_none(post.get('lon', '')),
            radius=_get_empty_to_none(post.get('radius', '')),
            state=post.get('state', ''),
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
    # return val

# get radius between 2 points
def _get_distance(lon1, lat1, lon2, lat2):
    R = 6373.0  # radius of earth in km
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


