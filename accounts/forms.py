from django import forms
from .models import StudentProfile

class CanvasFeedForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['canvas_ics_url']
