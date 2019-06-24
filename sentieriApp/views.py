from django.shortcuts import render, get_object_or_404

from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale


def index(request):
    query = "select * from sentiero "
    sentieri = Sentiero.objects.raw(query)
    context = {'sentieri' : sentieri}
    return render(request,'sentieriApp/index.html', context)


def dettagliSentiero(request, idSentiero):
    sentiero = get_object_or_404(Sentiero, pk=idSentiero)
    return render(request, 'sentieriApp/dettagliSentiero.html',{'sentiero': sentiero})


def areaPersonale(request, idUtente):
    utente = get_object_or_404(Utente, pk=idUtente)
    esperienze = EsperienzaPersonale.objects.filter(user_id=idUtente)
    return render(request, 'sentieriApp/areaPersonale.html', {'utente': utente, 'esperienze': esperienze})


def dettagliPuntoGeografico(request, idPtoGeografico):
    ptogeog = get_object_or_404(PuntoGeografico, pk=idPtoGeografico)
    return render(request, 'sentieriApp/puntoGeografico.html', {'punto': ptogeog})

def nuovoAccount(request):
    return render(request, 'sentieriApp/creazioneAccount.html')



# Queries

def isCiclico(idSentiero):
    query = """
                select ciclico
                from sentiero
                where id=%s 
            """, [idSentiero]
    return Sentiero.objects.raw(query)


def cercaPerTitolo(stringa):
    query = """
                select *
                from sentiero
                where titolo like %s
            """, [stringa]
    return Sentiero.objects.raw(query)