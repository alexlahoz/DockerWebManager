from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
import docker
from contextlib import contextmanager

@login_required
def index(request):
  return render(request, 'clusters/index.html', {'request': request})

@login_required
def images(request):
  try:
    with docker_client() as client:
      images = client.images.list()
  except:
    return redirect('docker_not_running')

  return render(request, 'clusters/images.html', {
      'request': request,
      'images': images
    }
  )

@login_required
def pull_image(request):
  with docker_client() as client:
    try:
      client.images.pull(request.POST['image_name'])
    except:
      messages.add_message(request, messages.ERROR, 'Image does not exist')
      return redirect('images')

  messages.add_message(request, messages.SUCCESS, 'Image pulled successfully')

  return redirect('images')

def remove_image(request, image_id):
  with get_image(image_id) as image:
    try:
      image.remove()
    except:
      messages.add_message(request, messages.ERROR, 'Image is in use')
      return redirect('images')

  return redirect('images')

@login_required
def containers(request):
  try:
    with docker_client() as client:
      containers = client.containers.list(all=True)
  except:
    return redirect('docker_not_running')

  return render(request, 'clusters/containers.html', {
      'request': request,
      'containers': containers
    }
  )

@login_required
def container_console(request, container_id):
  with docker_client() as client:
    container = client.containers.get(container_id)

  return render(request, 'terminal.html', {
      'request': request,
      'container': container
    }
  )

@login_required
def start_container(request, container_id):
  with docker_client() as client:
    container = client.containers.get(container_id)
    container.start()

  return redirect('containers')

@login_required
def stop_container(request, container_id):
  with docker_client() as client:
    container = client.containers.get(container_id)
    container.stop()

  return redirect('containers')

def signup(request):
    if request.user.is_authenticated:
      return redirect('index')

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
    if request.user.is_authenticated:
      return redirect('index')

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

@login_required
def docker_not_running(request):
  return render(request, 'clusters/docker_not_running.html', {'request': request})

@contextmanager
def docker_client():
  client = docker.from_env()
  yield client

@contextmanager
def get_image(image_id):
  client = docker.from_env()
  image = client.images.get(image_id)
  yield image


