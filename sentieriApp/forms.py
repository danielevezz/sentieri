from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Utente, OPZIONI_SESSO, Citta, Sentiero, EsperienzaPersonale, Data


class CreazioneAccount(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    sesso = forms.CharField(max_length=1, widget=forms.Select(choices=OPZIONI_SESSO))
    eta = forms.IntegerField(min_value=1, max_value=150)
    residenza = forms.ModelChoiceField(queryset=Citta.objects.all())

    class Meta:
        model = Utente
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'sesso', 'eta', 'residenza')


class InserisciEsperienza(ModelForm):

    voto = forms.IntegerField(min_value=1, max_value=10)
    difficolta = forms.IntegerField(min_value=1, max_value=10)
    sentiero = forms.ModelChoiceField(queryset=Sentiero.objects.all())
    data = forms.ModelChoiceField(queryset=Data.objects.all())


    class Meta:
        model = EsperienzaPersonale
        fields = ('sentiero', 'voto', 'difficolta', 'data')