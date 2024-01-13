from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("images/", views.images, name="images"),
    path("images/pull_image/", views.pull_image, name="pull_image"),
    path("images/detail/<str:image_id>", views.image_detail, name="image_detail"),
    path("images/remove/<str:image_id>/", views.remove_image, name="remove_image"),
    path("containers/", views.containers, name="containers"),
    path("containers/create/", views.create_container, name="create_container"),
    path("containers/start_container/<str:container_id>", views.start_container, name="start_container"),
    path("containers/stop_container/<str:container_id>", views.stop_container, name="stop_container"),
    path("containers/remove/<str:container_id>/", views.remove_container, name="remove_container"),
    path("containers/console/<str:container_id>", views.container_console, name="container_console"),
    path("containers/detail/<str:container_id>", views.container_detail, name="container_detail"),
    path("docker_not_running/", views.docker_not_running, name="docker_not_running"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.signout, name="logout"),
    path("signin/", views.signin, name="signin")
]
