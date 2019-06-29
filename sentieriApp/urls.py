from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("<int:idSentiero>/", views.dettagliSentiero, name='dettagliSentiero'),
    path("utente/<int:idUtente>/", views.areaPersonale, name='areaPersonale'),
    path("punto/<int:idPtoGeografico>/", views.dettagliPuntoGeografico, name='dettagliPuntoGeografico'),
    path("creazione/", views.creazioneAccount, name="creazioneNuovoAccount"),
    path("esperienza/", views.inserisciEsperienza, name="inserisciEsperienza"),
    path("selezionaCategorie/", views.selezionaCategorie, name="selezionaCategorie"),
    path("elencoSentieri/", views.elencoSentieri, name="elencoSentieri")
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]