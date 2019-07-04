from django import forms
from django.forms import ModelForm, Form
from django.contrib.auth.forms import UserCreationForm
from .models import Utente, OPZIONI_SESSO, Citta, Sentiero, EsperienzaPersonale, DIFFICOLTA_CAI, Categoria
from .queries import mie_categorie

import datetime


class CreazioneAccount(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    sesso = forms.CharField(max_length=1, widget=forms.Select(choices=OPZIONI_SESSO))
    eta = forms.IntegerField(min_value=1, max_value=150)
    residenza = forms.ModelChoiceField(queryset=Citta.objects.all())
    categorie = forms.ModelMultipleChoiceField(required=False, queryset=Categoria.objects.all())

    class Meta:
        model = Utente
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'sesso', 'eta', 'residenza', 'categorie')

class ModificaAccount(ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    sesso = forms.CharField(max_length=1, widget=forms.Select(choices=OPZIONI_SESSO))
    eta = forms.IntegerField(min_value=1, max_value=150)
    residenza = forms.ModelChoiceField(queryset=Citta.objects.all())
    categorie = forms.ModelMultipleChoiceField(required=False, queryset=Categoria.objects.all())

    class Meta:
        model = Utente
        fields = ('first_name', 'last_name', 'sesso', 'eta', 'residenza', 'categorie')


class InserisciEsperienza(ModelForm):

    voto = forms.IntegerField(min_value=1, max_value=10)
    difficolta = forms.IntegerField(min_value=1, max_value=10)
    sentiero = forms.ModelChoiceField(queryset=Sentiero.objects.all())
    data = forms.DateTimeField(widget=forms.SelectDateWidget(years=range(1990,datetime.date.today().year + 1)))

    commento = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = EsperienzaPersonale
        fields = ('sentiero', 'voto', 'difficolta', 'data', "commento")


class Filtro(Form):


    CATEG = Categoria.objects.all()
    CATEG = [c.nome for c in CATEG]
    CATEG += ["Mie categorie"]

    SCELTE_CATEGORIA = tuple(zip(CATEG, CATEG))

    categoria = forms.CharField(max_length=3, widget=forms.Select(choices=SCELTE_CATEGORIA))
    durataMax = forms.IntegerField(min_value=0, max_value=50, label="Durata massima", required=False) #Ore
    dislivelloMax = forms.IntegerField(min_value=0, max_value=50000, label="Dislivello Massimo", required=False) #Metri
    ciclico = forms.BooleanField(required=False)
    difficolta = forms.CharField(max_length=3, widget=forms.Select(\
        choices=DIFFICOLTA_CAI + (("ALL", "Tutte le difficoltà"),)), required=False)




class SentieroPreferito(ModelForm):
    preferito = forms.BooleanField(required=False)

    class Meta:
        model = Preferito
        fields = ('preferito',)
