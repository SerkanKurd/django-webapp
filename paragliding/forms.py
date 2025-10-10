from django import forms
from django.utils.formats import date_format
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML
from . import models
from .get_from_ypforum import get_name


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = ['course_name', 'start_date',
                  'end_date', 'is_completed', 'description']
        labels = {
            'course_name': "Kurs Adı",
            'start_date': "Başlangıç Tarihi",
            'end_date': "Bitiş Tarihi",
            "is_completed": "Kurs Tamamlandı mı?",
            'description': "Açıklama",
        }
        widgets = {
            'start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Kurs Kayıt',
                'course_name',
                'start_date',
                'end_date',
                'is_completed',
                'description',
            ),
            Submit('submit', 'Kaydet', css_class='button white'),
            Submit('submit', 'Sil', css_class='button white'),
            Submit('submit', 'Yeni', css_class='button white'),
        )


class PilotForm(forms.ModelForm):
    class Meta:
        model = models.Pilot
        fields = ['name', 'profile_url', 'level']
        labels = {
            'name': "Pilot Adı",
            'profile_url': "Profil URL (Örn: https://www.ypforum.com/leonardo/pilot/0_6573)",
            'level': "Seviye",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Fieldset(
                '',
                'name',
                'profile_url',
                'level',
            ),
            Submit('submit', 'Kaydet', css_class='button white'),
            Submit('submit', 'Sil', css_class='button white'),
            Submit('submit', 'Yeni', css_class='button white'),
        )

    def clean(self):
        cleaned_data = super().clean()
        profile_url = cleaned_data.get('profile_url')
        name = cleaned_data.get('name')

        if profile_url:
            ypforum_pilot_name = get_name(profile_url)
            if not ypforum_pilot_name:
                self.add_error(
                    'profile_url', "Profil URL'si hatalı veya geçerli bir isim bulunamadı. Örn: https://www.ypforum.com/leonardo/pilot/0_6573")
            elif not name:
                cleaned_data['name'] = ypforum_pilot_name
        return cleaned_data


class PilotCourseAssignmentForm(forms.Form):
    courses = forms.ModelMultipleChoiceField(
        queryset=models.Course.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Atanacak Kursları Seçin",
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        pilot = kwargs.pop('pilot', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['courses'].queryset = models.Course.objects.filter(
                manager=user, is_completed=False)

        if pilot:
            self.fields['courses'].initial = pilot.course.all()

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'courses',
            Submit('submit', 'Kursları Ata', css_class='btn btn-primary')
        )


class AllListForm(forms.Form):
    pilot_name = forms.ChoiceField(
        label="Pilot Adı",
        required=False
    )
    course_name = forms.ChoiceField(
        label="Kurs Adı",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        courses_view = [
            f"{course.course_name} ({date_format(course.start_date)})"
            for course in models.Course.objects.all()]
        courses = [course.id for course in models.Course.objects.all()]
        courses = [""] + courses
        courses_view = ["Tüm Kurslar"] + courses_view
        pilots = [pilot.id for pilot in models.Pilot.objects.all()]
        pilots = [""] + pilots
        pilots_view = [pilot.name for pilot in models.Pilot.objects.all()]
        pilots_view = ["Tüm Pilotlar"] + pilots_view
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['pilot_name'].choices = zip(pilots, pilots_view)
        self.fields['course_name'].choices = zip(courses, courses_view)
        self.helper.form_method = 'get'
        # self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Fieldset(
                'Pilot Listesi Filtreleme',
                'pilot_name',
                'course_name',
            ),
            Submit('submit', 'Filtrele', css_class='btn-primary'),
            HTML("""
                 <a href="{% url 'paragliding:index' %}" class="btn btn-primary">Temizle</a>
                 """)
        )
