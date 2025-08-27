from django import forms
from .models import Audio, Reunion

class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class ReunionForm(forms.ModelForm):
    class Meta:
        model = Reunion
        fields = ['titre', 'date_r', 'heure_r', 'participants']
        widgets = {
            'date_r': forms.DateInput(attrs={'type': 'date'}),
            'heure_r': forms.TimeInput(attrs={'type': 'time'}),
            'participants': forms.SelectMultiple(attrs={'class': 'select2'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['participants'].queryset = Reunion.objects.exclude(id=user.id)

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = Audio
        fields = ['chemin_fichier']
        widgets = {
            'chemin_fichier': forms.FileInput(attrs={'accept': 'audio/*'}),
        }