from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone


@login_required
def index(request):
    return render(request, 'clusters/index.html', {'request': request})

@login_required
def images(request):
    return render(request, 'clusters/images.html', {'request': request})

@login_required
def containers(request):
    return render(request, 'clusters/containers.html', {'request': request})

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
