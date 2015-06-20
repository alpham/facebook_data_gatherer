from django.shortcuts import render


def home(request):
    render(request, 'frontend/index.html', {})
