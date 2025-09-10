from django import forms
from .models import Postulacion

class PostulacionForm(forms.ModelForm):
    class Meta:
        model = Postulacion
        fields = ['cv_pdf']
        widgets = {
            'cv_pdf': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
        }