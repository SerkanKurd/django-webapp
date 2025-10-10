from . import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta, date


def get_pilot_statistics(pilot_id):
    try:
        pilot = models.Pilot.objects.get(id=pilot_id)
    except models.Pilot.DoesNotExist:
        return None

    flights = models.FlightData.objects.filter(pilot=pilot)
    total_flights = flights.count()
    total_duration = flights.aggregate(total=Sum('duration'))[
        'total'] or timedelta(0)
    total_distance = flights.aggregate(total=Sum('distance'))['total'] or 0

    return {
        'pilot': pilot,
        'total_flights': total_flights,
        'total_duration': total_duration,
        'total_distance': total_distance,
    }


def get_general_statistics():
    total_pilots = models.Pilot.objects.count()
    total_flights = models.FlightData.objects.count()
    total_courses = models.Course.objects.count()
    pilots_by_level = list(models.Pilot.objects.values(
        'level').annotate(count=Count('*')).order_by('level'))
    
    print(pilots_by_level)

    return {
        'total_pilots': total_pilots,
        'total_flights': total_flights,
        'total_courses': total_courses,
        'pilots_by_level': pilots_by_level,
    }


def get_flights_per_day(days=30):
    today = timezone.now().date()
    start_date = today - timedelta(days=days - 1)

    # Generate all dates in the range
    all_dates = [start_date + timedelta(days=i) for i in range(days)]

    # Query flights grouped by day
    flights_by_day = (
        models.FlightData.objects.filter(flight_date__gte=start_date)
        .annotate(day=TruncDay("flight_date"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    # Create a dictionary for quick lookup and format the result
    flight_counts = {item["day"].date(): item["count"]
                     for item in flights_by_day}
    result = [{"date": dt.strftime("%b %d"), "count": flight_counts.get(
        dt, 0)} for dt in all_dates]

    return result


if __name__ == "__main__":
    data1 = get_general_statistics()
    data2 = get_flights_per_day()

    print(data1)
    print(data2)
