from django import forms
from django.utils.formats import date_format
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML

import manage
from . import models
from .extentions.get_ypforum import get_name


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
        self.request = kwargs.pop('request', None)
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

            # Mevcut yöneticinin bu profili zaten ekleyip eklemediğini kontrol et
            if self.request and self.request.user.is_authenticated:
                # Düzenleme modunda, mevcut pilot hariç diğerlerini kontrol et
                existing_pilots = models.Pilot.objects.filter(
                    manager=self.request.user, profile_url=profile_url)
                if self.instance and self.instance.pk:
                    existing_pilots = existing_pilots.exclude(pk=self.instance.pk)
                
                if existing_pilots.exists():
                    self.add_error('profile_url', "Bu pilot zaten listenizde mevcut.")
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        pilots_qs = models.Pilot.objects.filter(manager=user) if user else models.Pilot.objects.none()
        courses_qs = models.Course.objects.filter(manager=user) if user else models.Course.objects.none()

        pilot_choices = [("", "Tüm Pilotlar")] + [(p.id, p.name) for p in pilots_qs]
        course_choices = [("", "Tüm Kurslar")] + [(c.id, f"{c.course_name} ({date_format(c.start_date)})") for c in courses_qs]

        self.fields['pilot_name'].choices = pilot_choices
        self.fields['course_name'].choices = course_choices

        self.helper = FormHelper()
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
