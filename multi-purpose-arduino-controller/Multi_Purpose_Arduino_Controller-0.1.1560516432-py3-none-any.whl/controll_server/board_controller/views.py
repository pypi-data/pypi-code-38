from django.shortcuts import render

# Create your views here.
def index(request):
    return  render(request,"board_controller_index.html")