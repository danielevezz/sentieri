from django.shortcuts import render, get_object_or_404, redirect
from .models import Sentiero , PuntoGeografico, Commento, Categoria
from .forms import CreazioneAccount, InserisciEsperienza, Filtro
from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale, Commento, Categoria, Interessi, Preferito,\
    Difficolta
from .forms import CreazioneAccount, InserisciEsperienza, SentieroPreferito, ModificaAccount
from django.contrib.auth import login, authenticate
from django.http import HttpResponseNotFound, Http404
from django.db import connection
from .queries import *

# Una view in postgres
# create view as ...
# alter view nome owner postg_djang
def index(request):
    query = "select * from sentiero "
    sentieri = Sentiero.objects.raw(query)
    context = {'sentieri' : sentieri}
    return render(request,'sentieriApp/index.html', context)


# Le categorie sono passate come parametro GET nell'URL
# in questo modo:
# http://127.0.0.1:8000/sentieri/elencoSentieri/?categorie=Escursionismo,Camminata
# Se non c'è nulla come valore prendo tutte le categorie
# La query è:
# SELECT * from sentiero WHERE sentiero.categoria_id IN (elenco categorie)
# Ho usato il coso di django perchè non riuscivo con il raw per problemi di apici e stavo smattando
def elencoSentieri(request):

    filtro = Filtro(request.POST)
    if request.method == 'POST':
        if filtro.is_valid():

            dati = filtro.cleaned_data
            categorieR = dati.get('categoria')
            durataMax = dati.get("durataMax")
            dislivelloMax = dati.get("dislivelloMax")
            ciclico = dati.get("ciclico")
            difficolta = dati.get("difficolta")
            media_alta = dati.get("media_alta")

            print(difficolta)

            # TODO costruire stringa mie Categorie

            if categorieR == "Tutte le categorie":
                categorie = Categoria.objects.all()
                categorie = [c.nome for c in categorie]
            else:
                categorie = [categorieR]

            if difficolta == "ALL":
                diff = Difficolta.objects.all()
                diff = [c.nome for c in diff]
            else:
                diff = [difficolta]

            sentieri = Sentiero.objects.filter(categoria__in=categorie)

            sentieri = sentieri.filter(durata__lte=durataMax)

            sentieri = sentieri.filter(dislivello__lte=dislivelloMax)

            sentieri = sentieri.filter(ciclico=ciclico)

            sentieri = sentieri.filter(difficolta__in=diff)

            # if media_alta:
            #     sentieri_voti= sentieri_media_voti_piu_alta_di(str(media_alta))
            #     sentieri_voti_ids=[]
            #     for item in sentieri_voti:
            #         sentieri_voti_ids.append(str(item[0][1]))
            #
            #     sentieri= sentieri.filter(id__in=sentieri_voti_ids)

            print(sentieri.query)

            return render(request, 'sentieriApp/elencoSentieri.html',
                      {'sentieri': sentieri, 'form': filtro})

    else:
        filtro = Filtro(initial={'difficolta': "ALL",
                                 'categoria': "Escursionismo",
                                 'durataMax': 50,
                                 'dislivelloMax': 50000,
                                 'ciclico': False})

    sentieri = Sentiero.objects.all()
    print("mlem")
    return render(request, 'sentieriApp/elencoSentieri.html', {'sentieri': sentieri, 'form': filtro,
                                                               'errors': filtro.errors})


def elencoUtenti(request):
    pass



def elencoSentieriDiUtente(request, idUtente):
    return render(request, 'sentieriApp/elencoSentieriDiUtente.html', {'sentieri' : sentieri_effettuati(idUtente)})

def commentiDiUtente(request, idUtente):
    return render(request, 'sentieriApp/commentiDiUtente.html', {'commenti' : commenti_di_un_utente(idUtente)})



# def selezionaCategorie(request):
#
#
#     categorie = Categoria.objects.all()
#     categorie = [c.nome for c in categorie]
#     #
#     if request.user.is_authenticated:
#         mieCategorie = mie_categorie(request.user.id)
#         mieCategorie = [i[0] for i in mieCategorie]
#         mieCategorie = ",".join(mieCategorie)
#     else:
#         mieCategorie = []
#
#     return render(request,'sentieriApp/selezionaCategorie.html', {'categorie' : categorie, 'mieCategorie' : mieCategorie})
#     # return render(request, 'sentieriApp/selezionaCategorie.html')


def dettagliSentiero(request, idSentiero):
    query = "select * from dati_sentiero where id = " + str(idSentiero)
    with connection.cursor() as cursor:
        cursor.execute(query)
        sentiero = cursor.fetchone()
    luoghi = luoghi_di_un_sentiero(idSentiero)

    if sentiero.__len__() == 0:
        raise Http404

    form = SentieroPreferito(request.POST or None)

    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                if "add_preferito" in request.POST:
                    preferito = Preferito(user=request.user, sentiero=Sentiero.objects.get(id=idSentiero))
                    preferito.save()
                    res = False
                if "remove_preferito" in request.POST:
                    res = True
                    preferito = Preferito.objects.get(user=request.user, sentiero=Sentiero.objects.get(id=idSentiero))
                    preferito.delete()

                return redirect("dettagliSentiero", idSentiero=idSentiero)

        else:
            if Preferito.objects.filter(user=request.user, sentiero=Sentiero.objects.get(id=idSentiero)):
                res = True
            else:
                res = False
    else:
        res = False

    return render(request, 'sentieriApp/dettagliSentiero.html', {'sentiero': sentiero,
                                                                 "commenti": commenti_di_un_sentiero(idSentiero),
                                                                 'preferito': res, 'form': form, 'luoghi': luoghi})



def dettagliUtente(request, idUtente):
    if request.user.is_authenticated:
        if request.user.id == idUtente:
            utente = get_object_or_404(Utente, pk=idUtente)
            esperienze = EsperienzaPersonale.objects.filter(user_id=idUtente).select_related()
            interessi = Interessi.objects.filter(user_id=idUtente).select_related()
            return render(request, 'sentieriApp/dettagliUtente.html', {'utente': utente, 'esperienze': esperienze,
                                                                       'personale': True, 'interessi': interessi})

    return render(request, 'sentieriApp/dettagliUtente.html', {"utente": utentePubblico(idUtente)})

def dettagliLuogo(request, idLuogo):
    luogo = informazioni_luogo(idLuogo)
    return render(request, 'sentieriApp/dettagliLuogo.html', {'luogo':luogo})



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
            cat = form.cleaned_data.get('categorie')
            for c in cat:
                interessi = Interessi(categoria=c, user=request.user)
                interessi.save()
            return redirect("index")
    else:
        form = CreazioneAccount()

    return render(request, 'registration/creazioneAccount.html', {"form" : form})

def modificaAccount(request):
    form = ModificaAccount(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            interessi = Interessi.objects.filter(user=request.user)
            interessi.delete()

            utente = Utente.objects.filter(id=request.user.id)
            utente.update(first_name=form.cleaned_data.get('first_name'))
            utente.update(last_name=form.cleaned_data.get('last_name'))
            utente.update(sesso=form.cleaned_data.get('sesso'))
            utente.update(eta=form.cleaned_data.get('eta'))
            utente.update(residenza=form.cleaned_data.get('residenza'))

            cat = form.cleaned_data.get('categorie')
            for c in cat:
                interessi = Interessi(categoria=c, user=request.user)
                interessi.save()

            return redirect("index")
    else:
        user = Utente.objects.get(id= request.user.id)
        form = ModificaAccount(initial={'first_name': str(user.first_name),
                                        'last_name': str(user.last_name),
                                        'sesso': user.sesso,
                                        'eta': user.eta,
                                        'residenza': user.residenza
                                        })
    return render(request, 'sentieriApp/modificaAccount.html', {"form" : form})


def inserisciEsperienza(request):
    form = InserisciEsperienza(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            dati = form.cleaned_data
            esp = form.save(commit=False) # Non la mando su db
            esp.user = request.user
            esp.save()
            testoCommento = dati.get("commento")
            commento = Commento(esperienza_id=esp.id, testo=testoCommento)
            commento.save()
            return redirect("index")
        else:
            form = InserisciEsperienza()
    return render(request, 'sentieriApp/inserisciEsperienza.html', {"form": form})

