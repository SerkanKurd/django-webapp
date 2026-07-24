from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from blog import admin
from blog.models import Posts
from . import forms
from paragliding.statistics import get_general_statistics, get_flights_per_day
import json


from django.views.decorators.http import require_POST


def index(request):
    stats = get_general_statistics()
    blog_post_count = Posts.objects.count()
    flights_last_30_days = get_flights_per_day(days=365)

    context = {
        "stats": stats,
        "blog_post_count": blog_post_count,
        "flights_chart_data": flights_last_30_days,
    }
    return render(request, "index.html", context)


@require_POST
def log_out(request):
    logout(request)
    messages.info(request, "Başarıyla çıkış yapıldı.")
    return redirect('homepage:index')


def log_in(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, f"{user.username} kullanıcı adı ile giriş yapıldı!")
                return redirect('homepage:index')
            else:
                form.add_error(None, "Kullanıcı adı veya şifre yanlış.")
    else:
        form = forms.LoginForm()

    context = {
        'form': form,
        'title': 'Giriş Yap',
    }
    return render(request, 'accounts/login.html', context)


def register(request):
    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('user_mail')

            try:
                User.objects.create_user(
                    username=username, password=password, email=email)

                # Send confirmation email
                subject = 'Hesabınız Başarıyla Oluşturuldu'
                body = f'Merhaba {username},\n\nWeb sitemize kaydınız başarıyla tamamlanmıştır. Hoş geldiniz!'
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                messages.success(
                    request, "Hesabınız başarıyla oluşturuldu. Şimdi giriş yapabilirsiniz.")
            except Exception as e:
                messages.error(
                    request, f"Kayıt sırasında bir hata oluştu: {e}")

            return redirect('homepage:index')
    else:
        form = forms.RegisterForm()

    context = {
        'form': form,
        'title': 'Kayıt',
    }
    return render(request, 'accounts/register.html', context)


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
                    settings.DEFAULT_FROM_EMAIL,
                    settings.DEFAULT_ADMIN_EMAILS,
                )

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
