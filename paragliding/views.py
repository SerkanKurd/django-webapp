from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db import transaction
from datetime import timedelta
import io
import zipfile
from . import models
from django.core.cache import cache
from . import forms
from myweb.tasks import get_pilot_flights_data, download_igc_file_task


@login_required
def index(request):
    form = forms.AllListForm(request.GET, user=request.user)
    pilots = models.Pilot.objects.filter(
        manager=request.user
    )
    courses = models.Course.objects.filter(manager=request.user)

    if request.GET and form.is_valid():
        pilot_name = form.cleaned_data.get('pilot_name')
        course_name = form.cleaned_data.get('course_name')

        if pilot_name:
            pilots = pilots.filter(id=pilot_name)
        if course_name:
            courses = courses.filter(id=course_name)

    for pilot in pilots:
        pilot.flight_count = models.FlightData.objects.filter(
            pilot=pilot).count()
        pilot.total_duration = models.FlightData.objects.filter(
            pilot=pilot).aggregate(total=Sum('duration'))['total']
        pilot.total_distance = models.FlightData.objects.filter(
            pilot=pilot).aggregate(total=Sum('distance'))['total']

    context = {
        'form': form,
        'pilots': pilots,
        'courses': courses,
    }
    return render(request, 'paragliding/index.html', context)


@login_required
def course_view(request, course_id=None):
    instance = None
    if course_id:
        instance = models.Course.objects.filter(
            id=course_id,
            manager=request.user
        ).first()
        if not instance:
            messages.error(
                request,
                "Kurs bulunamadı veya bu kursa erişim yetkiniz yok."
            )
            return redirect('paragliding:index')

    if request.method == 'POST':
        form = forms.CourseForm(request.POST, instance=instance)
        submit_value = request.POST.get('submit')

        if submit_value == 'Sil' and instance:
            course_name = instance.course_name
            instance.delete()
            messages.success(
                request,
                f'"{course_name}" isimli kurs başarıyla silindi.'
            )
            return redirect('paragliding:index')

        if submit_value == 'Yeni':
            return redirect('paragliding:course')

        if form.is_valid():
            course = form.save(commit=False)
            course.manager = request.user
            course.save()
            if not instance:
                messages.success(
                    request,
                    f'"{course.course_name}" isimli kurs başarıyla oluşturuldu!'
                )
            else:
                messages.success(
                    request,
                    f'"{course.course_name}" isimli kurs başarıyla güncellendi.'
                )
            return redirect('paragliding:index')
    else:
        form = forms.CourseForm(instance=instance)

    context = {
        "form": form,
        "title": "Kurs Ekle/Sil",
        "links": [{'url': 'paragliding:index', 'name': 'Genel Liste'}]
    }
    return render(request, 'form.html', context)


@login_required
def pilot_view(request, pilot_id=None):
    instance = None
    if pilot_id:
        instance = models.Pilot.objects.filter(
            id=pilot_id,
            manager=request.user
        ).first()
        if not instance:
            messages.error(
                request,
                "Pilot bulunamadı veya bu pilota erişim yetkiniz yok."
            )
            return redirect('paragliding:index')

    if request.method == 'POST':
        form = forms.PilotForm(
            request.POST, instance=instance, request=request)
        submit_value = request.POST.get('submit')

        if submit_value == 'Sil' and instance:
            pilot_name = instance.name
            # Instead of deleting the pilot, just remove the current manager.
            instance.manager.remove(request.user)
            messages.success(
                request, f'"{pilot_name}" isimli pilot listenizden kaldırıldı.')
            return redirect('paragliding:index')

        if submit_value == 'Yeni':
            return redirect('paragliding:pilot')

        if form.is_valid():
            profile_url = form.cleaned_data.get('profile_url')

            try:
                with transaction.atomic():
                    # Check if a pilot with this profile_url already exists.
                    pilot, created = models.Pilot.objects.get_or_create(
                        profile_url=profile_url,
                        defaults={'name': form.cleaned_data.get(
                            'name'), 'level': form.cleaned_data.get('level')}
                    )

                    # Add the current user as a manager to the existing or new pilot.
                    pilot.manager.add(request.user)

                    # If the pilot was newly created, update other fields from the form.
                    if not created:
                        pilot.name = form.cleaned_data.get('name', pilot.name)
                        pilot.level = form.cleaned_data.get(
                            'level', pilot.level)
                        pilot.save()

                    # Asynchronously fetch flight data
                    if pilot.profile_url:
                        get_pilot_flights_data.apply_async(
                            args=[pilot.profile_url, pilot.id],
                            countdown=5
                        )  # pyright: ignore[reportCallIssue]
                        messages.info(
                            request, f"{pilot.name} için uçuş verileri arka planda güncelleniyor.")

                    messages.success(
                        request, f'"{pilot.name}" isimli pilot başarıyla kaydedildi.')
                    return redirect('paragliding:index')
            except Exception as e:
                messages.error(request, f"Bir hata oluştu: {e}")
                return render(request, 'form.html', {'form': form, "title": "Pilot Ekle/Sil"})
    else:
        form = forms.PilotForm(instance=instance, request=request)

    context = {
        "form": form,
        "title": "Pilot Ekle/Sil",
        "links": [{'url': 'paragliding:index', 'name': 'Genel Liste'}],
    }
    return render(request, 'form.html', context)


@login_required
def apply_course_view(request, pilot_id):
    try:
        pilot = models.Pilot.objects.get(id=pilot_id, manager=request.user)
    except models.Pilot.DoesNotExist:
        messages.error(
            request, "Pilot bulunamadı veya bu pilota erişim yetkiniz yok.")
        return redirect('paragliding:index')

    courses_all = models.Course.objects.filter(manager=request.user)
    if request.method == 'POST':
        form = forms.PilotCourseAssignmentForm(
            request.POST, user=request.user, pilot=pilot)
        if form.is_valid():
            selected_courses = form.cleaned_data['courses']
            for course in courses_all:
                if course in selected_courses:
                    pilot.course.add(course)
                else:
                    pilot.course.remove(course)

            messages.success(
                request, f"'{pilot.name}' için kurs atamaları güncellendi.")
            return redirect('paragliding:index')
    else:
        form = forms.PilotCourseAssignmentForm(user=request.user, pilot=pilot)

    context = {
        'form': form,
        'title': f"'{pilot.name}' için Kurs Ata"
    }
    return render(request, 'form.html', context)


@login_required
def course_detail_view(request, course_id=None):
    try:
        course = models.Course.objects.get(id=course_id, manager=request.user)
    except models.Course.DoesNotExist:
        messages.error(
            request, "Kurs bulunamadı veya bu kursa erişim yetkiniz yok.")
        return redirect('paragliding:index')

    pilots_in_course = course.pilot_set.all().order_by('name')

    flight_data = models.FlightData.objects.filter(
        flight_date__gte=course.start_date,
        flight_date__lte=course.end_date
    ).order_by('flight_date')

    for pilot in pilots_in_course:
        pilot.flight_data = flight_data.filter(pilot=pilot)

        stats = pilot.flight_data.aggregate(total_duration=Sum(
            'duration'), total_distance=Sum('distance'))
        pilot.total_duration = stats.get('total_duration') or timedelta(0)
        pilot.total_distance = stats.get('total_distance') or 0

    context = {
        'course': course,
        'pilots': pilots_in_course,
    }
    return render(request, 'paragliding/course_detail.html', context)


@login_required
def pilot_flight_view(request, pilot_id: int):
    try:
        pilot = models.Pilot.objects.get(id=pilot_id, manager=request.user)
    except models.Pilot.DoesNotExist:
        messages.error(
            request, "Pilot bulunamadı veya bu pilota erişim yetkiniz yok.")
        return redirect('paragliding:index')

    if request.method == 'POST':
        submit_action = request.POST.get('submit')
        if submit_action == "flightdata_get":
            cache_key = f"flightdata_get_lock_{pilot_id}"
            if cache.get(cache_key):
                messages.info(
                    request, "Bu pilot için veri çekme işlemi zaten yeni başlatıldı. Lütfen bir dakika sonra tekrar deneyin.")
            else:
                cache.set(cache_key, True, timeout=600)
                get_pilot_flights_data.apply_async(
                    args=[pilot.profile_url, pilot.id],
                    countdown=5
                )  # pyright: ignore[reportCallIssue]
                messages.success(
                    request, f"{pilot.name} pilotu için uçuş verileri güncelleniyor. Bu işlem biraz zaman alabilir.")

        elif submit_action == "flightdata_get_igc":
            cache_key = f"flightdata_get_igc_lock_{pilot_id}"
            if cache.get(cache_key):
                messages.warning(
                    request, "Bu pilot için IGC indirme işlemi zaten yeni başlatıldı. Lütfen birkaç dakika sonra tekrar deneyin.")

            # Find flights for this pilot that don't have the IGC file content
            flights_to_download = models.FlightData.objects.filter(
                pilot=pilot
            )

            if not flights_to_download.exists():
                messages.info(
                    request, f"{pilot.name} için tüm IGC dosyaları zaten indirilmiş.")
                return redirect('paragliding:pilot_flight_view', pilot_id=pilot.id)

            counter = 0
            for flight in flights_to_download:
                if not flight.file_content:
                    counter += 1
                    download_igc_file_task.apply_async(
                        args=[flight.flight_url], countdown=counter*5
                    ) # type: ignore

            # Set a lock to prevent re-triggering for 10 minutes
            cache.set(cache_key, True, timeout=3600)
            messages.success(
                request, f"{pilot.name} için {counter} adet IGC dosyası indirme işlemi arka planda başlatıldı.")

        elif submit_action == "flightdata_download":
            flights_with_igc = models.FlightData.objects.filter(
                pilot=pilot,
                file_content__isnull=False
            ).exclude(file_name__exact='')

            if not flights_with_igc.exists():
                messages.info(
                    request, f"{pilot.name} için indirilecek IGC dosyası bulunamadı.")
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for flight in flights_with_igc:
                        flight_id = flight.flight_url.split("/")[-1]
                        zip_file.writestr(
                            f"{flight_id}_{flight.file_name}", flight.file_content)

                response = HttpResponse(
                    zip_buffer.getvalue(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{pilot.name}_flights.zip"'
                return response

        return redirect('paragliding:pilot_flight_view', pilot_id=pilot.id)

    flights = models.FlightData.objects.filter(
        pilot=pilot
    ).order_by('-flight_date')

    context = {
        'pilot': pilot,
        'flights': flights,
        'title': f"{pilot.name} - Uçuş Kayıtları"
    }
    return render(request, 'paragliding/pilot_flight_view.html', context)
