from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from geoposition.fields import GeopositionField
from django.db import models
from geoposition.fields import GeopositionField




class PointOfInterest(models.Model):
    name = models.CharField(max_length=100)
    position = GeopositionField()


class Sentiero(models.Model):
    ptoGeograficoPartenza = models.ForeignKey('PuntoGeografico', on_delete=models.CASCADE, related_name="partenza")
    ptoGeograficoArrivo = models.ForeignKey('PuntoGeografico', on_delete=models.CASCADE, related_name="arrivo")
    difficolta = models.ForeignKey('Difficolta', on_delete=models.CASCADE, default='E')
    titolo = models.CharField(max_length=50)
    durata = models.IntegerField(blank=True, default=0)
    descrizione = models.TextField()
    dislivello = models.IntegerField(blank=True, default=0)
    salita = models.IntegerField(blank=True, default=0)                      # Metri in salita del percorso
    discesa = models.IntegerField(blank=True, default=0)                     # Metri in discesa del percorso
    altitudineMax = models.IntegerField(blank=True, default=0)
    altitudineMin = models.IntegerField(blank=True, default=0)
    ciclico = models.BooleanField(default=False)        # Se il sentiero è ciclico o meno
    linkMappa = models.URLField(blank=True, default="")             # Link alla mappa del percorso (opzionale)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, related_name="categoria", default="Camminata")
    lunghezza = models.FloatField(blank=True, default=0.)


    # L'id viene generato automaticamente da Django se non imposto altra chiave primaria

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name = 'Sentiero'
        verbose_name_plural = 'Sentieri'
        db_table = 'sentiero'

    def media_voti(self):
        media_voti = EsperienzaPersonale.objects.filter(user_id=self.id).get().voto.avg()
        return media_voti




class Categoria(models.Model):
    nome = models.CharField(max_length=30, primary_key=True)
    descrizione = models.TextField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorie'
        db_table = 'categoria'


class PuntoGeografico(models.Model):
    latitudine = models.CharField(max_length=15, blank=True)
    longitudine = models.CharField(max_length=15, blank=True)
    altitudine = models.IntegerField()
    nome = models.CharField(max_length=30)
    descrizione = models.TextField(blank=True, default="")
    provincia = models.ForeignKey('Citta', on_delete=models.CASCADE)
    posizione = GeopositionField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Punto Geografico'
        verbose_name_plural = 'Punti Geografici'
        db_table = 'punto_geografico'


class Nazione(models.Model):
    nome = models.CharField(max_length=30, primary_key=True);

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Nazione'
        verbose_name_plural = 'Nazioni'
        db_table = "nazione"


# Django non permette una chiave primaria di 2 attributi quindi la key è id
# ma nome e nazione fanno coppie che devono essere uniche
class Citta(models.Model):
    nome = models.CharField(max_length=30);
    nazione = models.ForeignKey(Nazione, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    class Meta:
        unique_together = (("nome", "nazione"),)
        verbose_name = 'Città'
        verbose_name_plural = 'Città'
        db_table = "citta"


OPZIONI_SESSO = (("M", "Uomo"), ("F", "Donna"), ("A", "Altro"))


# Utente definisce solo i campi aggiuntivi
# AbstractUser definisce i campi principali come username, password, nome, ...
class Utente(AbstractUser):
    residenza = models.ForeignKey(Citta, on_delete=models.SET_DEFAULT, default=1, blank=True)
    sesso = models.CharField(max_length=1, choices=OPZIONI_SESSO, default="A", blank=True)
    eta = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Utente'
        verbose_name_plural = 'Utenti'
        db_table = "utente"


class Interessi(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.categoria.nome)+" - "+str(self.user)

    class Meta:
        unique_together = (('categoria','user'),)
        verbose_name = 'Interesse'
        verbose_name_plural = 'Interessi'
        db_table = "interesse"


class Tappa(models.Model):
    luogo = models.ForeignKey("Luogo", on_delete=models.CASCADE)
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.luogo.nome)+" - "+str(self.sentiero.titolo)

    class Meta:
        unique_together = (("luogo", 'sentiero'),)
        verbose_name = 'Tappa'
        verbose_name_plural = 'Tappe'
        db_table = "tappa"



class TipologiaLuogo(models.Model):
    nome = models.CharField(max_length=30)
    descrizione = models.TextField()

    def __str__(self):
        return str(self.nome)

    class Meta:
        verbose_name = 'Tipologia luogo'
        verbose_name_plural = 'Tipologie luogo'
        db_table = "tipologia_luogo"


class Luogo(models.Model):
    tipoLuogo = models.ForeignKey(TipologiaLuogo, on_delete=models.CASCADE)
    nome = models.CharField(max_length=30)
    descrizione = models.TextField()
    sito = models.URLField(blank=True, default="")
    ptoGeografico = models.ForeignKey(PuntoGeografico, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.nome)

    class Meta:
        verbose_name = 'Luogo'
        verbose_name_plural = 'Luoghi'
        db_table = "luogo"


class Commento(models.Model):
    esperienza = models.ForeignKey("EsperienzaPersonale", on_delete=models.CASCADE)
    testo = models.TextField();

    def __str__(self):
        return self.testo

    class Meta:
        verbose_name = 'Commento'
        verbose_name_plural = 'Commenti'
        db_table = "commento"


DIFFICOLTA_CAI = (("T", "Turistico"), ("E", "Escursionistico"), ("EE", "Escursionisti esperti"), ("EEA", "Escursionisti esperti con attrezzatura"))


class Difficolta(models.Model):
    nome = models.CharField(max_length=3, choices=DIFFICOLTA_CAI, default="E", primary_key=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Difficoltà'
        verbose_name_plural = 'Difficoltà'
        db_table = "difficolta"


class EsperienzaPersonale(models.Model):
    voto = models.IntegerField() #tra 1 e 10
    difficolta = models.IntegerField(blank=True, default=5) #tra 1 e 10
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_esperienza = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user) + " - " + str(self.sentiero)

    class Meta:
        unique_together = (('sentiero', 'user', 'data_esperienza'),)
        verbose_name = 'Esperienza personale'
        verbose_name_plural = 'Esperienze personali'
        db_table = "esperienza"


class Preferito(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.sentiero.titolo)+" - "+str(self.user)

    class Meta:
        unique_together = (('user', 'sentiero'),)
        verbose_name = 'Preferito'
        verbose_name_plural = 'Preferiti'
        db_table = "preferito"
