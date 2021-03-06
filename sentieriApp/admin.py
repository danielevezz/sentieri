from django.contrib import admin
from sentieriApp.models import Sentiero, Categoria, PuntoGeografico, Nazione, Citta, Tappa, Interessi, \
    Difficolta, Luogo, Commento, Utente, TipologiaLuogo, EsperienzaPersonale, Preferito

# Register your models here.
admin.site.register(Sentiero)
admin.site.register(Categoria)
admin.site.register(PuntoGeografico)
admin.site.register(Nazione)
admin.site.register(Citta)
admin.site.register(Tappa)
admin.site.register(Interessi)

admin.site.register(Difficolta)
admin.site.register(Luogo)
admin.site.register(Commento)

admin.site.register(Utente)
admin.site.register(TipologiaLuogo)
admin.site.register(EsperienzaPersonale)
admin.site.register(Preferito)

admin.site.site_header = "Sentieri ";
