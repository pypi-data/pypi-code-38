from django.shortcuts import render


def index(request):
    return render(request, 'blender_basico/base.pug', {})
