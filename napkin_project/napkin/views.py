from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context_dict = {
    'maintitle': "NAPKIN is a place where you can share content with a closed group of people.",
    'subtitle': "No registration. No signup."
    }

    return render(request, 'napkin/index.html', context_dict)
