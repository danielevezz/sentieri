from django.contrib import admin
from sentieriApp.models import Sentiero, Categoria, PuntoGeografico, Tag, Nazione, Citta, Tappa, Interessi, \
    Effettuato, Voto, Difficolta, Luogo, Commento

# Register your models here.
admin.site.register(Sentiero)
admin.site.register(Categoria)
admin.site.register(PuntoGeografico)
admin.site.register(Nazione)
admin.site.register(Citta)
admin.site.register(Tappa)
admin.site.register(Interessi)
admin.site.register(Effettuato)
admin.site.register(Voto)
admin.site.register(Difficolta)
admin.site.register(Luogo)
admin.site.register(Commento)
