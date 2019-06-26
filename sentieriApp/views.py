from django.shortcuts import render, get_object_or_404, redirect
from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale, Data
from .forms import CreazioneAccount, InserisciEsperienza
from django.contrib.auth import login, authenticate


def index(request):
    query = "select * from sentiero "
    sentieri = Sentiero.objects.raw(query)
    context = {'sentieri' : sentieri}
    return render(request,'sentieriApp/index.html', context)


def dettagliSentiero(request, idSentiero):
    sentiero = get_object_or_404(Sentiero, pk=idSentiero)
    cic = str(isCiclico(idSentiero))
    return render(request, 'sentieriApp/dettagliSentiero.html',{'sentiero': sentiero,
                                                                'ciclico': cic})


def areaPersonale(request, idUtente):
    utente = get_object_or_404(Utente, pk=idUtente)
    esperienze = EsperienzaPersonale.objects.filter(user_id=idUtente)
    return render(request, 'sentieriApp/areaPersonale.html', {'utente': utente, 'esperienze': esperienze})


def dettagliPuntoGeografico(request, idPtoGeografico):
    ptogeog = get_object_or_404(PuntoGeografico, pk=idPtoGeografico)
    return render(request, 'sentieriApp/puntoGeografico.html', {'punto': ptogeog})


# Form Views


def creazioneAccount(request):
    form = CreazioneAccount(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_pass = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_pass)
            login(request, user)
            return redirect("index")
        else:
            form = CreazioneAccount()
    return render(request, 'registration/creazioneAccount.html', {"form" : form})


def inserisciEsperienza(request):
    form = InserisciEsperienza(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            esp = form.save(commit=False) # Non la mando su db
            esp.user = request.user
            esp.save()
            return redirect("index")
        else:
            form = InserisciEsperienza()
    return render(request, 'sentieriApp/inserisciEsperienza.html', {"form": form})


# Queries

def isCiclico(idSentiero):
    # query = """
    #             select ciclico
    #             from sentiero
    #             where id=%s
    #         """, [idSentiero]
    return Sentiero.objects.filter(id=idSentiero).get().ciclico
    # return Sentiero.objects.raw(query)


def cercaPerTitolo(stringa):
    query = """
                select *
                from sentiero
                where titolo like %s
            """, [stringa]
    return Sentiero.objects.raw(query)