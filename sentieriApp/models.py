from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager



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



    # Mancano le chiavi esterne

    # L'id viene generato automaticamente da Django se non imposto altra chiave primaria

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name = 'Sentiero'
        verbose_name_plural = 'Sentieri'
        db_table = 'sentiero'


# class Tag(models.Model):
#     sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
#     categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
#
#     def __str__(self):
#         return self.sentiero.titolo + " - " + self.categoria.nome
#
#     class Meta:
#         verbose_name = "Tag"
#         verbose_name_plural = "Tags"
#         db_table = "tag"


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
    latitudine = models.CharField(max_length=15)
    longitudine = models.CharField(max_length=15)
    altitudine = models.IntegerField()
    nome = models.CharField(max_length=30)
    descrizione = models.TextField(blank=True, default="")
    meteo = models.URLField(blank=True, default="")
    provincia = models.ForeignKey('Citta', on_delete=models.CASCADE)

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

    class Meta:
        verbose_name = 'Interesse'
        verbose_name_plural = 'Interessi'
        db_table = "interesse"


class Tappa(models.Model):
    luogo = models.ForeignKey("Luogo", on_delete=models.CASCADE)
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Tappa'
        verbose_name_plural = 'Tappe'
        db_table = "tappa"


# class Effettuato(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
#     data = models.DateField(auto_now=True);
#
#     class Meta:
#         verbose_name = 'Effettuato'
#         verbose_name_plural = 'Effettuati'
#         db_table = "effettuato"
#
#
# class Voto(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
#     valore = models.IntegerField()
#
#     def __str__(self):
#         return str(self.valore)
#
#     class Meta:
#         verbose_name = 'Voto'
#         verbose_name_plural = 'Voti'
#         db_table = "voto"
#
#
# class Difficolta(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
#     valore = models.IntegerField()
#
#     def __str__(self):
#         return str(self.valore)
#
#     class Meta:
#         verbose_name = 'Difficoltà'
#         verbose_name_plural = 'Difficoltà'
#         db_table = "difficolta"


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


class Difficolta(models.Model):
    diffs = (("T", "Turistico"), ("E", "Escursionistico"), ("EE", "Escursionisti esperti"), ("EEA", "Escursionisti esperti con attrezzatura"))
    nome = models.CharField(max_length=3, choices=diffs, default="E", primary_key=True)

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
        verbose_name = 'Esperienza personale'
        verbose_name_plural = 'Esperienze personali'
        db_table = "esperienza"


class Preferito(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Preferito'
        verbose_name_plural = 'Preferiti'
        db_table = "preferito"
