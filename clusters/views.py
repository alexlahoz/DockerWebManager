from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib import messages
from contextlib import contextmanager
import docker
import threading

@login_required
def index(request):
  try:
    with docker_client() as client:
        info = client.info()
        data = {
          'containers': info['Containers'],
          'images': info['Images'],
          'architecture': info['Architecture'],
          'ncpu': info['NCPU']
        }
  except Exception as e:
      return redirect('docker_not_running')

  return render(request, 'clusters/index.html', {
      'request': request,
      'data': data
    }
  )

@login_required
def images(request):
  try:
    with docker_client() as client:
      # images = client.images.list(filters={'dangling': False})
      images = client.images.list()
  except:
    return redirect('docker_not_running')

  return render(request, 'clusters/images.html', {
      'request': request,
      'images': images
    }
  )

def image_detail(request, image_id):
  try:
    with docker_client() as client:
      images = client.images.list(filters={'dangling': False})
  except:
    return redirect('docker_not_running')

  with get_image(image_id) as image_data:
    return render(request, 'clusters/image_detail.html', {
        'request': request,
        'images': images,
        'image_data': image_data,
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
      all_containers = client.containers.list(all=True)
  except Exception as e:
    return redirect('docker_not_running')

  containers_with_network = []
  containers = []

  for container in all_containers:
    add_last_started_method(container)
    network = next(iter(container.attrs['NetworkSettings']['Networks']))
    if network == 'github-runner_default':
      containers_with_network.append(container)
    else:
      containers.append(container)

  return render(request, 'clusters/containers.html', {
    'request': request,
    'containers_with_network': containers_with_network,
    'containers': containers
  })

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
def new_container(request):
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

def create_container(request):
  try:
    with docker_client() as client:
      client.containers.run(request.POST['image_name'], request.POST['command'], detach=True)
      # client.containers.run(request.POST['image_name'], request.POST['command'], request.POST['kwargs'])
  except:
    messages.add_message(request, messages.ERROR, 'The request could not be processed')
    return redirect('containers')

  messages.add_message(request, messages.SUCCESS, 'Container successfully created')
  return redirect('containers')

@login_required
def stop_container(request, container_id):
  with docker_client() as client:
    container = client.containers.get(container_id)
    t = threading.Thread(target=container.stop)
    t.start()

  return redirect('containers')

@login_required
def remove_container(request, container_id):
  with get_container(container_id) as container:
    try:
      container.remove()
    except:
      messages.add_message(request, messages.ERROR, 'container is in use')
      return redirect('containers')

  return redirect('containers')

def container_detail(request, container_id):
  try:
    with docker_client() as client:
      all_containers = client.containers.list(all=True)
  except:
    return redirect('docker_not_running')

  containers_with_network = []
  containers = []

  for container in all_containers:
    network = next(iter(container.attrs['NetworkSettings']['Networks']))
    if network == 'github-runner_default':
        containers_with_network.append(container)
    else:
        containers.append(container)

  with get_container(container_id) as container_data:
    finished_at_date = container_data.attrs['State']['FinishedAt'][:10]
    finished_at_time = container_data.attrs['State']['FinishedAt'][11:19]
    finished_at = calculate_time_difference(finished_at_date, finished_at_time)

    return render(request, 'clusters/container_detail.html', {
        'request': request,
        'containers_with_network': containers_with_network,
        'containers': containers,
        'container_data': container_data,
        'finished_at': finished_at,
        'networks': container_data.attrs['NetworkSettings']['Networks'],
        'primary_network': next(iter(container_data.attrs['NetworkSettings']['Networks']))
      }
    )

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
  try:
    with docker_client() as client:
      client.ping()
      return redirect('index')
  except:
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

@contextmanager
def get_container(container_id):
  client = docker.from_env()
  container = client.containers.get(container_id)
  yield container

from datetime import datetime

def add_last_started_method(container):
  def last_started():
    finished_at_date = container.attrs['State']['FinishedAt'][:10]
    finished_at_time = container.attrs['State']['FinishedAt'][11:19]
    try:
      finished_at_datetime = calculate_time_difference(finished_at_date, finished_at_time)
    except ValueError:
      finished_at_datetime = None
    return finished_at_datetime
  container.last_started = last_started


def calculate_time_difference(date, time):
    # Convert the date and time string to a datetime object
    datetime_input = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')

    # Get the current date and time
    now = datetime.now()

    # Calculate the time difference
    time_difference = now - datetime_input

    # Calculate days, hours, and minutes
    days = time_difference.days
    hours, seconds = divmod(time_difference.seconds, 3600)
    minutes, _ = divmod(seconds, 60)

    # Determine how to display the time difference
    if days > 0:
        result = f'{days} days ago'
    elif hours > 0:
        result = f'{hours} hours ago'
    else:
        result = f'{minutes} minutes ago'

    return result

