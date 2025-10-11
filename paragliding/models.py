from django.db import models
from django.conf import settings
from django.utils.formats import date_format


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course_name} - {date_format(self.start_date)}"


class Pilot(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    profile_url = models.URLField(max_length=255, null=True, blank=True)
    level = models.CharField(
        max_length=2,
        choices=(
            ("P2", "P2"), ("P3", "P3"), ("P4", "P4"), ("P5", "P5")
        ),
        blank=True, null=True
    )
    course = models.ManyToManyField(Course)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile_url', 'manager')

    def __str__(self):
        return self.name or f"Pilot: {self.name} - {self.manager}"


class FlightData(models.Model):
    pilot_name = models.CharField(max_length=250, blank=True, null=True)
    profil_url = models.CharField(max_length=250, blank=True, null=True)
    flight_date = models.DateTimeField(blank=True, null=True)
    takeoff_name = models.CharField(max_length=50, blank=True, null=True)
    landing_name = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    flight_type = models.CharField(max_length=50, blank=True, null=True)
    paraglider = models.CharField(max_length=50, blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    distance = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    distance_olc = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    points_olc = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    distance_max = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    distance_from_takeoff = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    altitude_takeoff = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    altitude_max = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    altitude_landing = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    flight_url = models.URLField(
        max_length=255, unique=True, null=True, blank=True)
    file_name = models.CharField(max_length=200, blank=True, null=True)
    file_content = models.BinaryField(null=True, blank=True)
    isupdate = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pilot_name} - {self.flight_date} - {self.file_name}"
