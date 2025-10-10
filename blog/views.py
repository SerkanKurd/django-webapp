from django.shortcuts import render
from .models import Posts


def index(request):
    posts = Posts.objects.all()
    context = {"posts": posts}
    return render(request, "blog/index.html", context)
