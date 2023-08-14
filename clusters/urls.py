from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("images/", views.images, name="images"),
    path("images/pull_image/", views.pull_image, name="pull_image"),
    path("images/<str:image_id>/remove/", views.remove_image, name="remove_image"),
    path("containers/", views.containers, name="containers"),
    path("docker_not_running/", views.docker_not_running, name="docker_not_running"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.signout, name="logout"),
    path("signin/", views.signin, name="signin")
]
