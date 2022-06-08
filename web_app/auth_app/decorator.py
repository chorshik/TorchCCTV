from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .forms import LoginForm
from django.contrib import messages


def authenticate_user(login_func):
    def wrapper(request, user=None):
        if request.user.is_authenticated:
            return redirect('video_server:cameras')
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                cd = login_form.cleaned_data
                user = authenticate(username=cd['username'], password=cd['password'])
                # if user is not None:
                if user is not None:
                    if user.is_active:
                        login_func(request, user)
                        return redirect('video_server:cameras')
                    else:
                        messages.error(request, 'User is disabled')
                else:
                    messages.error(request, 'User does not exit')
            else:
                messages.error(request, 'Invalid username of passoword')
        else:
            login_form = LoginForm()
        return render(request, 'auth_app/index.html', {'login_form': login_form})

    return wrapper


def logout_user(logout_func):
    def wrapper(request):
        if request.user.is_authenticated:
            logout_func(request)
            return redirect('auth_app:login')
        else:
            return redirect('auth_app:login')
    return wrapper
