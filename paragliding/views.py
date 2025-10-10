from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from django.db.models import Sum
from . import models
from django.core.cache import cache
from . import forms
from myweb.tasks import get_pilot_flights_data


@login_required
def index(request):
    form = forms.AllListForm(request.GET)
    pilots = models.Pilot.objects.filter(
        manager=request.user
    )
    courses = models.Course.objects.filter(manager=request.user)
    # courses_pilots = pilots.filter(pilots__in=courses)

    if request.GET and form.is_valid():
        pilot_name = form.cleaned_data.get('pilot_name')
        course_name = form.cleaned_data.get('course_name')

        if pilot_name:
            pilots = pilots.filter(id=pilot_name)
        if course_name:
            pilots = pilots.filter(id=course_name)

    context = {
        'form': form,
        'pilots': pilots,
        'courses': courses,
        # 'courses_pilots': courses_pilots,
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
            return redirect('paragliding:course_id', course_id=course.id)
    else:
        form = forms.CourseForm(instance=instance)
    context = {"form": form, "title": "Kurs Ekle/Sil"}
    return render(request, 'paragliding/data_enter.html', context)


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
        form = forms.PilotForm(request.POST, instance=instance)
        submit_value = request.POST.get('submit')

        if submit_value == 'Sil' and instance:
            pilot_name = instance.name
            instance.delete()
            messages.success(
                request, f'"{pilot_name}" isimli pilot başarıyla silindi.')
            return redirect('paragliding:index')

        if submit_value == 'Yeni':
            return redirect('paragliding:pilot')

        if form.is_valid():
            try:
                pilot = form.save(commit=False)
                if not instance:
                    # Set manager for new pilot
                    pilot.manager = request.user
                pilot.save()

                if not instance:
                    messages.success(
                        request,
                        f'"{pilot.name}" isimli pilot başarıyla oluşturuldu!'
                    )
                else:
                    messages.success(
                        request,
                        f'"{pilot.name}" isimli pilot başarıyla güncellendi.'
                    )
                return redirect('paragliding:pilot_id', pilot_id=pilot.id)
            except Exception:
                messages.error(
                    request, "Bu profil URL'si bu yönetici için zaten kayıtlı.")
                # Stay on the same page (creation or update) by re-rendering with the form
                return render(request, 'paragliding/data_enter.html', {'form': form, "title": "Pilot Ekle/Sil"})
    else:
        form = forms.PilotForm(instance=instance)

    context = {"form": form, "title": "Pilot Ekle/Sil"}
    return render(request, 'paragliding/data_enter.html', context)


@login_required
def apply_course_view(request, pilot_id=None):
    pilot = models.Pilot.objects.filter(
        id=pilot_id, manager=request.user).first()
    if not pilot:
        messages.error(
            request, "Pilot bulunamadı veya bu pilota erişim yetkiniz yok.")
        return redirect('paragliding:index')

    if request.method == 'POST':
        form = forms.PilotCourseAssignmentForm(
            request.POST, user=request.user, pilot=pilot)
        if form.is_valid():
            selected_courses = form.cleaned_data['courses']
            pilot.course.set(selected_courses)

            messages.success(
                request, f"'{pilot.name}' için kurs atamaları güncellendi.")
            return redirect('paragliding:index')
    else:
        form = forms.PilotCourseAssignmentForm(user=request.user, pilot=pilot)

    context = {
        'form': form,
        'title': f"'{pilot.name}' için Kurs Ata"
    }
    return render(request, 'paragliding/data_enter.html', context)


@login_required
def course_detail_view(request, course_id=None):
    try:
        # Use prefetch_related to efficiently fetch pilots associated with the course
        course = models.Course.objects.get(id=course_id, manager=request.user)
    except models.Course.DoesNotExist:
        messages.error(
            request, "Kurs bulunamadı veya bu kursa erişim yetkiniz yok.")
        return redirect('paragliding:index')

    # Get all pilots for the course, ordered by name
    pilots_in_course = course.pilot_set.all().order_by('name')

    # Get all relevant flights for these pilots within the course date range
    flight_data = models.FlightData.objects.filter(
        pilot__in=pilots_in_course,
        flight_date__gte=course.start_date,
        flight_date__lte=course.end_date
    ).order_by('flight_date')

    # Process flight data and attach statistics to each pilot object
    for pilot in pilots_in_course:
        pilot_flight_data = flight_data.filter(pilot=pilot)
        pilot.total_flights = pilot_flight_data.count()

        # Aggregate total duration and distance correctly
        stats = pilot_flight_data.aggregate(total_duration=Sum(
            'duration'), total_distance=Sum('distance'))
        pilot.total_duration = stats.get('total_duration') or timedelta(0)
        pilot.total_distance = stats.get('total_distance') or 0
        pilot.flights_in_course = pilot_flight_data

    context = {
        'course': course,
        'pilots': pilots_in_course,
        'title': f"Kurs Detayı: {course.course_name}"
    }
    return render(request, 'paragliding/course_detail.html', context)


@login_required
def pilot_flight_view(request, pilot_id):
    try:
        pilot = models.Pilot.objects.get(
            id=pilot_id,
            manager=request.user
        )
    except models.Pilot.DoesNotExist:
        messages.error(
            request, "Pilot bulunamadı veya bu pilota erişim yetkiniz yok.")
        return redirect('paragliding:index')

    if request.method == 'POST':
        if request.POST.get('submit') == "Get_Flights":
            cache_key = f"flight_update_lock_{pilot.id}"
            if cache.get(cache_key):
                messages.info(
                    request, "Bu pilot için veri çekme işlemi zaten yeni başlatıldı. Lütfen bir dakika sonra tekrar deneyin.")
            elif not pilot.profile_url:
                messages.error(
                    request, f"{pilot.name} için bir profil URL'si tanımlanmamış.")
            else:
                cache.set(cache_key, True, timeout=600)
                get_pilot_flights_data.apply_async(
                    args=[pilot.profile_url, pilot.id],
                    countdown=5
                )  # pyright: ignore[reportCallIssue]
                messages.success(
                    request, f"{pilot.name} pilotu için uçuş verileri güncelleniyor. Bu işlem biraz zaman alabilir.")
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
