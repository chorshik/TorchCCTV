from django.shortcuts import render


def index(request):
    # return HttpResponse("Index page")
    return render(request, 'index.html')
