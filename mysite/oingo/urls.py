from django.urls import path

from . import views

app_name = 'oingo'
urlpatterns = [
    path('hello', views.hello, name='hello'),
]
