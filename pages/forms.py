from django import forms
from django.contrib.auth.models import User
from .models import Postulacion, Profile

class PostulacionForm(forms.ModelForm):
    class Meta:
        model = Postulacion
        fields = ['cv_pdf']
        widgets = {
            'cv_pdf': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
        }


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]