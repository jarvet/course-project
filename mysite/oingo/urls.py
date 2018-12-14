from django.urls import path

from . import views

app_name = 'oingo'
urlpatterns = [
    path('hello', views.hello, name='hello'),
    path('', views.login, name='login'),
    path('register', views.register, name='register'),
    path('index', views.index, name='index'),
    path('logout', views.logout, name='logout'),
    path('profile/<int:user_id>', views.show_profile, name='profile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('show_filter', views.show_filter, name="show_filter"),
    path('create_filter', views.create_filter, name="create_filter"),
    path('edit_filter/<int:filter_id>', views.edit_filter, name="edit_filter"),
    path('remove_filter/<int:filter_id>', views.remove_filter, name="remove_filter"),
    path('create_note', views.create_note, name="create_note"),
    path('show_friends', views.show_friends, name="show_friends"),
    path('accept_friend_request/<int:friend_id>', views.accept_friend_request, name="accept_friend_request"),
    path('reject_friend_request/<int:friend_id>',views.reject_friend_request, name="reject_friend_request"),
    path('remove_friend/<int:friend_id>', views.remove_friend, name="remove_friend"),
    path('add_comment/<int:note_id>', views.add_comment, name="add_comment")

]
