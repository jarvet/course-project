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
]
