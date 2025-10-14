from django.urls import path
from . import views

app_name = "paragliding"

urlpatterns = [
    path("", views.index, name="index"),
    path("pilot/", views.pilot_view, name="pilot"),
    path("pilot/<int:pilot_id>", views.pilot_view, name="pilot_id"),
    path("pilot/flight/<int:pilot_id>",
         views.pilot_flight_view, name="pilot_flight_view"),
    path("course/", views.course_view, name="course"),
    path("course/<int:course_id>", views.course_view, name="course_id"),
    path("apply_course/<int:pilot_id>",
         views.apply_course_view, name="apply_course"),
    path("course_detail/<int:course_id>",
         views.course_detail_view, name="course_detail_id"),
    path("pilot/download_igc/<int:pilot_id>",
         views.pilot_flight_data_download, name="pilot_flight_data_download"),
]
