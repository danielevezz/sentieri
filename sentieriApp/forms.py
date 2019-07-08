from django import forms
from django.forms import ModelForm, Form
from django.contrib.auth.forms import UserCreationForm
from .models import Utente, OPZIONI_SESSO, Citta, Sentiero, EsperienzaPersonale, DIFFICOLTA_CAI, Categoria, Preferito

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

class FiltroUtenti(Form):
    utentiPopolari = forms.BooleanField(required=False)
    ordina = forms.CharField(required=False, widget=forms.Select(choices=[("Nome","Nome"), ("Esperienze", "Esperienza"), ("Commenti", "Commenti")]))




class Filtro(Form):

    CATEG = Categoria.objects.all()
    CATEG = [c.nome for c in CATEG]
    CATEG += ["Tutte le categorie"]

    SCELTE_CATEGORIA = tuple(zip(CATEG, CATEG))

    categoria = forms.CharField(max_length=max([x.__len__() for x in CATEG]), widget=forms.Select(choices=SCELTE_CATEGORIA), required=False)
    durataMax = forms.IntegerField(min_value=0, max_value=50, label="Durata massima (Ore)", required=False) #Ore
    dislivelloMax = forms.IntegerField(min_value=0, max_value=50000, label="Dislivello Massimo (m)", required=False) #Metri
    ciclico = forms.BooleanField(required=False)
    media_alta = forms.CharField(required=False, label="Media voti più alta di")
    difficolta = forms.CharField(max_length=3, widget=forms.Select(\
        choices=DIFFICOLTA_CAI + (("ALL", "Tutte le difficoltà"),)), required=False)
    titolo = forms.CharField(required=False, label="Ricerca per parola chiave")
    lunghezzaMax = forms.IntegerField(min_value=0, max_value=200, required=False, label="Lunghezza massima (Km)")
    preferiti = forms.BooleanField(required=False, label="Solo i miei percorsi preferiti")
    ordine = forms.CharField(required=False, label="Ordina per", widget=forms.Select(choices=[("Titolo","Titolo"), ("Voto", "Voto"), ("Partecipanti", "Partecipanti")]))
    miaCitta = forms.BooleanField(required=False, label="Solo percorsi della mia città")
    utentiMiaCitta = forms.BooleanField(required=False, label="Solo percorsi effettuati da utenti della mia città")




    def crea_categ(self, str):
        CATEG = Categoria.objects.all()
        CATEG = [c.nome for c in CATEG]
        CATEG += [str]
        return CATEG


class SentieroPreferito(ModelForm):
    preferito = forms.BooleanField(required=False)

    class Meta:
        model = Preferito
        fields = ('preferito',)
