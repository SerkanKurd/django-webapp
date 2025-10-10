from django.shortcuts import render
from django.contrib.auth import logout, login, authenticate
from paragliding.models import Pilot
from blog.models import Posts
from .forms import LoginForm
from paragliding.statistics import get_general_statistics, get_flights_per_day
import json


def index(request):
    stats = get_general_statistics()
    blog_post_count = Posts.objects.count()
    flights_last_30_days = get_flights_per_day(days=30)

    context = {
        "stats": stats,
        "blog_post_count": blog_post_count,
        "flights_chart_data": json.dumps(flights_last_30_days),
    }
    return render(request, "index.html", context)




def log_out(request):
    logout(request)
    return render(request, 'index.html')


def log_in(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, "index.html")
        else:
            return render(request, 'accounts/login.html', {'form': form})
    return render(request, 'accounts/login.html', {'form': form})
