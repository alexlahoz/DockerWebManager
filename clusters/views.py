from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import docker
from contextlib import contextmanager

@login_required
def index(request):
    return render(request, 'clusters/index.html', {'request': request})

@login_required
def images(request):
    with docker_client() as client:
        images = client.images.list()

    return render(request, 'clusters/images.html', {
        'request': request,
        'images': images
      }
    )

@login_required
def containers(request):
    with docker_client() as client:
        containers = client.containers.list()

    return render(request, 'clusters/containers.html', {
        'request': request,
        'containers': containers
      }
    )

@login_required
def pull_image(request):
    with docker_client() as client:
      try:
        client.images.pull(request.POST['image_name'])
      except docker.errors.APIError:
        return render(request, 'clusters/images.html', {
            'request': request,
            'error': 'Image does not exist'
          }
        )

    return redirect('images')

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html',
            {'form': UserCreationForm}
        )
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1']
                )

                user.save()
                login(request, user)
                return redirect('index')
            except IntegrityError:
                return render(request, 'signup.html',
                    {
                        'form': UserCreationForm,
                        'error': 'Username already exists'
                    }
                )
        return render(request, 'signup.html',
                    {
                        'form': UserCreationForm,
                        'error': 'Password does not match'
                    }
                )

@login_required
def signout(request):
    logout(request)
    return redirect('index')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password did not match'
            })
        else:
            login(request, user)
            return redirect('index')

@contextmanager
def docker_client():
    client = docker.from_env()
    yield client
