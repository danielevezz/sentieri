from django.db import models

# Create your models here.


class Sentiero(models.Model):
    titolo = models.CharField(max_length=30)
    descrizione = models.TextField()
    lunghezza = models.FloatField()
    salita = models.IntegerField()                      # Metri in salita del percorso
    discesa = models.IntegerField()                     # Metri in discesa del percorso
    altitudineMax = models.IntegerField()
    altitudineMin = models.IntegerField()
    visite = models.IntegerField(default=0)             # Non ho ben capito
    ciclico = models.BooleanField(default=False)        # Se il sentiero è ciclico o meno
    linkMappa = models.URLField(blank=True, default="")             # Link alla mappa del percorso (opzionale)

    # Mancano le chiavi esterne

    # L'id viene generato automaticamente da Django se non imposto altra chiave primaria

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name = 'Sentiero'
        verbose_name_plural = 'Sentieri'
        db_table = 'sentiero'

        # Manca da definire il nome della tabella nel db


class Tag(models.Model):
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        db_table = "tag"


class Categoria(models.Model):
    nome = models.CharField(max_length=30, primary_key=True)
    descrizione = models.TextField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorie'
        db_table = 'categoria'

        # Manca da definire il nome della tabella nel db


class PuntoGeografico(models.Model):
    latitudine = models.CharField(max_length=10)
    longitudine = models.CharField(max_length=10)
    altitudine = models.IntegerField()
    nome = models.CharField(max_length=30)
    descrizione = models.TextField()
    meteo = models.URLField(blank=True, default="")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Punto Geografico'
        verbose_name_plural = 'Punti Geografici'
        db_table = 'punto_geografico'

        # Manca da definire il nome della tabella nel db


class Nazione(models.Model):
    nome = models.CharField(max_length=30);

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Nazione'
        verbose_name_plural = 'Nazioni'
        db_table = "nazione"


class Citta(models.Model):
    nome = models.CharField(max_length=30);
    id_nazione = models.ForeignKey(Nazione, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Nazione'
        verbose_name_plural = 'Nazioni'
        db_table = "citta"


class Tappa(models.Model):
    punto_geografico = models.ForeignKey(PuntoGeografico, on_delete=models.CASCADE)
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)



    class Meta:
        verbose_name = 'Tappa'
        verbose_name_plural = 'Tappe'
        db_table = "tappa"


class Interessi(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    # id Persona ma usiamo le cose di django in modo che l'auth sia automatica

    class Meta:
        verbose_name = 'Interesse'
        verbose_name_plural = 'Interessi'
        db_table = "interesse"


class Effettuato(models.Model):
    # id persona
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
    data = models.DateField(auto_now=True);

    class Meta:
        verbose_name = 'Effettuato'
        verbose_name_plural = 'Effettuati'
        db_table = "effettuato"


class Voto(models.Model):
    # id persona
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
    valore = models.IntegerField()

    def __str__(self):
        return str(self.valore)

    class Meta:
        verbose_name = 'Voto'
        verbose_name_plural = 'Voti'
        db_table = "voto"


class Difficolta(models.Model):
    # id persona
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
    valore = models.IntegerField()

    def __str__(self):
        return str(self.valore)

    class Meta:
        verbose_name = 'Difficoltà'
        verbose_name_plural = 'Difficoltà'
        db_table = "difficolta"


class Luogo(models.Model):
    # localita = models.ForeignKey(localita,on_delete=models.CASCADE)
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Luogo'
        verbose_name_plural = 'Luoghi'
        db_table = "luogo"


class Commento(models.Model):
    # id persona
    sentiero = models.ForeignKey(Sentiero, on_delete=models.CASCADE)
    data = models.DateField(auto_now=True);
    testo = models.TextField();

    def __str__(self):
        return self.testo

    class Meta:
        verbose_name = 'Commento'
        verbose_name_plural = 'Commenti'
        db_table = "commento"
