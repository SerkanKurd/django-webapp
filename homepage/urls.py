from django.urls import path
from . import views

app_name = "homepage"

urlpatterns = [
    path("", views.index, name="index"),
    path("logout/", views.log_out, name="logout"),
    path("login/", views.log_in, name="login"),
    path("accounts/login/", views.log_in, name="login"),
    path("contact/", views.contact_form, name="contact"),
]
