from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("images/", views.images, name="images"),
    path("containers/", views.containers, name="containers"),
    path("images/pull_image/", views.pull_image, name="pull_image"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.signout, name="logout"),
    path("signin/", views.signin, name="signin")
]
