from django.contrib.auth import login, logout
from .decorator import authenticate_user, logout_user


@authenticate_user
def login_view(request, user=None):
    login(request, user)


@logout_user
def logout_view(request):
    logout(request)
