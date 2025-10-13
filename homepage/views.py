from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from blog.models import Posts
from . import forms
from paragliding.statistics import get_general_statistics, get_flights_per_day
import json


def index(request):
    stats = get_general_statistics()
    blog_post_count = Posts.objects.count()
    flights_last_30_days = get_flights_per_day(days=365)

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
    form = forms.LoginForm(request.POST)
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


def contact_form(request):
    if request.method == "POST":
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = f"İletişim Formu - {name}"
            body = f"Gönderen: {name}\nE-posta: {email}\n\nMesaj:\n{message}"

            try:
                send_mail(
                    subject,
                    body,
                    "serkankurd@gmail.com",
                    [email],
                    fail_silently=False,
                )
                # send_mail(
                #     subject,
                #     body,
                #     settings.DEFAULT_FROM_EMAIL,
                #     [admin[1] for admin in settings.ADMINS]
                # )

                # Send a notification to all registered Telegram chats

                messages.success(
                    request, "Mesajınız başarıyla gönderildi. Teşekkür ederiz!")
                return redirect('homepage:index')
            except Exception as e:
                messages.error(
                    request, f"Mesaj gönderilirken bir hata oluştu: {e}")
    else:
        form = forms.ContactForm()

    context = {
        'form': form,
        'title': 'İletişim Formu',
    }
    return render(request, 'form.html', context)
