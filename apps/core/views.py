from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

def test_secure(request):
    return HttpResponse(str(request.is_secure()))