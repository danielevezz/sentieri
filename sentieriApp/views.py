from django.shortcuts import render, get_object_or_404, redirect
from .models import Sentiero , PuntoGeografico, Commento, Categoria
from .forms import CreazioneAccount, InserisciEsperienza, Filtro
from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale, Commento, Categoria, Interessi, Preferito,\
    Difficolta, Citta
from .forms import CreazioneAccount, InserisciEsperienza, SentieroPreferito, ModificaAccount, FiltroUtenti, FiltroNoLogin
from django.contrib.auth import login, authenticate
from django.http import HttpResponseNotFound, Http404
from django.db import connection
from .queries import *
from django.db.models import Q
from . import views
from django.db.models import Case, When

# Una view in postgres
# create view as ...
# alter view nome owner postg_djang
def index(request):
    query = "select * from sentiero "
    sentieri = Sentiero.objects.raw(query)
    context = {'sentieri' : sentieri, "sentieriPopolari": sentieri_piu_percorsi(), "sentieriVotati": sentieri_piu_votati()}
    return render(request,'sentieriApp/index.html', context)


# Le categorie sono passate come parametro GET nell'URL
# in questo modo:
# http://127.0.0.1:8000/sentieri/elencoSentieri/?categorie=Escursionismo,Camminata
# Se non c'è nulla come valore prendo tutte le categorie
# La query è:
# SELECT * from sentiero WHERE sentiero.categoria_id IN (elenco categorie)
# Ho usato il coso di django perchè non riuscivo con il raw per problemi di apici e stavo smattando
def elencoSentieri(request):

    if request.user.is_authenticated:
        filtro = Filtro(request.POST)
        if request.method == 'POST':
            if filtro.is_valid():

                dati = filtro.cleaned_data
                categorieR = dati.get('categoria')
                durataMax = dati.get("durataMax")
                dislivelloMax = dati.get("dislivelloMax")
                lunghezzaMax = dati.get("lunghezzaMax")
                ciclico = dati.get("ciclico")
                difficolta = dati.get("difficolta")
                media_alta = dati.get("media_alta")
                titolo = dati.get("titolo")
                preferiti = dati.get("preferiti")
                ordine = dati.get("ordine")
                miaCitta = dati.get("miaCitta")
                utentiMiaCitta = dati.get("utentiMiaCitta")
                citta = dati.get("citta")
                tipiLuoghi = dati.get("tipiLuoghi")

                sentieri = Sentiero.objects.all()
                sentieri = sentieri.all()

                if ordine == "Voto":
                    print("Voto")
                    sentieri_ordinati = ordina_sentieri_per_voto()
                    sentieri_ids = []
                    for item in sentieri_ordinati:
                        id = item[0]
                        sentieri_ids.append(id)
                    print(sentieri_ids)
                    clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sentieri_ids)])
                    ordering = 'CASE %s END' % clauses
                    sentieri = sentieri.filter(pk__in=sentieri_ids).extra(
                        select={'ordering': ordering}, order_by=('ordering',))

                elif ordine == "Partecipanti":
                    print("Partecipanti")
                    sentieri_ordinati = ordina_sentieri_per_percorrenze()
                    sentieri_ids = []
                    for item in sentieri_ordinati:
                        id = item[0]
                        sentieri_ids.append(id)
                    print(sentieri_ids)
                    clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sentieri_ids)])
                    ordering = 'CASE %s END' % clauses
                    sentieri = sentieri.filter(pk__in=sentieri_ids).extra(
                        select={'ordering': ordering}, order_by=('ordering',))
                else:
                    print("Titolo")
                    sentieri_ordinati = ordina_sentieri_per_titolo()
                    sentieri_ids = []
                    for item in sentieri_ordinati:
                        id = item[0]
                        sentieri_ids.append(id)
                    print(sentieri_ids)
                    clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sentieri_ids)])
                    ordering = 'CASE %s END' % clauses
                    print(ordering)
                    sentieri = sentieri.filter(pk__in=sentieri_ids).extra(
                        select={'ordering': ordering}, order_by=('ordering',))

                print(sentieri)

                if categorieR == "Tutte le categorie":
                    categorie = Categoria.objects.all()
                    categorie = [c.nome for c in categorie]
                elif categorieR == "Categorie di mio interesse":
                    categorie = mie_categorie(request.user.id)
                    categorie = [c[0] for c in categorie]
                else:
                    categorie = [categorieR]

                if difficolta == "ALL":
                    diff = Difficolta.objects.all()
                    diff = [c.nome for c in diff]
                else:
                    diff = [difficolta]

                sentieri = sentieri.filter(categoria__in=categorie)

                print("categorie")
                print(sentieri)

                if durataMax == None:
                    durataMax = 50
                sentieri = sentieri.filter(durata__lte=durataMax)
                print("durata")
                print(sentieri)


                if dislivelloMax == None:
                    dislivelloMax = 50000
                sentieri = sentieri.filter(dislivello__lte=dislivelloMax)
                print("dislivello")
                print(sentieri)


                sentieri = sentieri.filter(ciclico=ciclico)
                print("ciclico")
                print(sentieri)


                sentieri = sentieri.filter(difficolta__in=diff)
                print("difficoltà")
                print(sentieri)


                sentieri = sentieri.filter(titolo__icontains=titolo)
                print("titolo")
                print(sentieri)


                if tipiLuoghi:
                    for tipo in tipiLuoghi:
                        sent = sentieri_con_un_luogo(tipo)
                        ids = [i[0] for i in sent]
                        sentieri = sentieri.filter(id__in=ids)
                print("luoghi")
                print(sentieri)


                if citta != None:
                    sent = sentieri_della_mia_citta(citta.id)
                    ids = [i[0] for i in sent]
                    sentieri = sentieri.filter(id__in=ids)
                    print("città")
                    print(sentieri)

                if lunghezzaMax == None:
                    lunghezzaMax = 200
                sentieri = sentieri.filter(lunghezza__lte=lunghezzaMax)
                print("lunghezza")
                print(sentieri)


                if preferiti:
                    sent = sentieri_preferiti(request.user.id)
                    ids = [i[0] for i in sent]
                    sentieri = sentieri.filter(id__in=ids)
                print("preferiti")
                print(sentieri)


                if miaCitta:
                    residenza = Utente.objects.filter(id=request.user.id).select_related("residenza").get().residenza
                    sent = sentieri_della_mia_citta(residenza.id)
                    print(sent)

                    ids = [i[0] for i in sent]

                    sentieri = sentieri.filter(id__in=ids)
                print("mia città")
                print(sentieri)


                if utentiMiaCitta:
                    residenza = Utente.objects.filter(id=request.user.id).select_related("residenza").get().residenza
                    sent = sentieri_percorsi_solo_da_utenti_della_mia_citta(residenza.id)
                    print(sent)

                    ids = [i[0] for i in sent]

                    sentieri = sentieri.filter(id__in=ids)
                print("utenti città")
                print(sentieri)




                if media_alta != None:
                    sentieri_voti= sentieri_media_voti_piu_alta_di(str(media_alta))
                    sentieri_voti_ids=[]
                    for item in sentieri_voti:
                        id = item[0]
                        sentieri_voti_ids.append(id)

                    sentieri= sentieri.filter(id__in=sentieri_voti_ids)
                print("media")
                print(sentieri)




            ids = []
            orderIds =""
            i=0
            for s in sentieri:
                ids.append(s.id)
                i = i+1
                orderIds += ", "+str(s.id)+","+str(i)


            if ids:
                ids = ','.join(map(str, ids))
                dati_sentieri = info_complete_sentieri_id(ids, orderIds)
            else:
                dati_sentieri = []

            return render(request, 'sentieriApp/elencoSentieri.html',
                      {'sentieri': dati_sentieri, 'form': filtro})

        else:
            filtro = Filtro(initial={'difficolta': "ALL",
                                     'categoria': "Tutte le categorie",
                                     'durataMax': 50,
                                     'dislivelloMax': 50000,
                                     'ciclico': False})

    else:
        print("no autenticato")
        filtroNoLogin = FiltroNoLogin(request.POST)
        if request.method == 'POST':
            if filtroNoLogin.is_valid():

                dati = filtroNoLogin.cleaned_data
                categorieR = dati.get('categoria')
                durataMax = dati.get("durataMax")
                dislivelloMax = dati.get("dislivelloMax")
                lunghezzaMax = dati.get("lunghezzaMax")
                ciclico = dati.get("ciclico")
                difficolta = dati.get("difficolta")
                media_alta = dati.get("media_alta")
                titolo = dati.get("titolo")
                ordine = dati.get("ordine")
                citta = dati.get("citta")

                sentieri = Sentiero.objects.all()

                if ordine == "Voto":
                    print("Voto")
                    sentieri_ordinati = ordina_sentieri_per_voto()
                    sentieri_ids = []
                    for item in sentieri_ordinati:
                        id = item[0]
                        sentieri_ids.append(id)
                    print(sentieri_ids)
                    clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sentieri_ids)])
                    ordering = 'CASE %s END' % clauses
                    sentieri = sentieri.filter(pk__in=sentieri_ids).extra(
                        select={'ordering': ordering}, order_by=('ordering',))

                elif ordine == "Partecipanti":
                    print("Partecipanti")
                    sentieri_ordinati = ordina_sentieri_per_percorrenze()
                    sentieri_ids = []
                    for item in sentieri_ordinati:
                        id = item[0]
                        sentieri_ids.append(id)
                    print(sentieri_ids)
                    clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sentieri_ids)])
                    ordering = 'CASE %s END' % clauses
                    sentieri = sentieri.filter(pk__in=sentieri_ids).extra(
                        select={'ordering': ordering}, order_by=('ordering',))
                else:
                    print("Titolo")
                    sentieri_ordinati = ordina_sentieri_per_titolo()
                    sentieri_ids = []
                    for item in sentieri_ordinati:
                        id = item[0]
                        sentieri_ids.append(id)
                    print(sentieri_ids)
                    clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(sentieri_ids)])
                    ordering = 'CASE %s END' % clauses
                    print(ordering)
                    sentieri = sentieri.filter(pk__in=sentieri_ids).extra(
                        select={'ordering': ordering}, order_by=('ordering',))


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

                sentieri = sentieri.filter(categoria__in=categorie)

                if durataMax == None:
                    durataMax = 50
                sentieri = sentieri.filter(durata__lte=durataMax)

                if dislivelloMax == None:
                    dislivelloMax = 50000
                sentieri = sentieri.filter(dislivello__lte=dislivelloMax)

                if citta != None:
                    sent = sentieri_della_mia_citta(citta.id)
                    ids = [i[0] for i in sent]
                    sentieri = sentieri.filter(id__in=ids)

                sentieri = sentieri.filter(ciclico=ciclico)

                sentieri = sentieri.filter(difficolta__in=diff)

                sentieri = sentieri.filter(titolo__icontains=titolo)

                if lunghezzaMax == None:
                    lunghezzaMax = 200
                sentieri = sentieri.filter(lunghezza__lte=lunghezzaMax)

                if media_alta:
                    sentieri_voti = sentieri_media_voti_piu_alta_di(str(media_alta))
                    sentieri_voti_ids = []
                    for item in sentieri_voti:
                        id = item[0]
                        sentieri_voti_ids.append(id)
                    sentieri = sentieri.filter(id__in=sentieri_voti_ids)
                    print(sentieri)



            ids = []
            orderIds = ""
            i = 0
            for s in sentieri:
                ids.append(s.id)
                i = i + 1
                orderIds += ", " + str(s.id) + "," + str(i)

            if ids:
                ids = ','.join(map(str, ids))
                dati_sentieri = info_complete_sentieri_id(ids, orderIds)
            else:
                dati_sentieri = []

            return render(request, 'sentieriApp/elencoSentieri.html',
                          {'sentieri': dati_sentieri, 'form': filtroNoLogin})

        else:
            filtro = FiltroNoLogin(initial={'difficolta': "ALL",
                                     'categoria': "Tutte le categorie",
                                     'durataMax': 50,
                                     'dislivelloMax': 50000,
                                     'ciclico': False})

    dati_sentieri = info_complete_sentieri()
    return render(request, 'sentieriApp/elencoSentieri.html', {'sentieri': dati_sentieri, 'form': filtro,
                                                               'errors': filtro.errors})


def elencoUtenti(request):
    filtro = FiltroUtenti(request.POST)
    if request.method == 'POST':
        if filtro.is_valid():

            dati = filtro.cleaned_data
            popolari = dati.get('utentiPopolari')
            ordina = dati.get("ordina")
            commenti = Commento.objects.filter(esperienza__user_id=1).exclude(testo="").count()

            if ordina=="Nome":
                utenti = ordina_utenti_username()
            if ordina=="Commenti":
                utenti = ordina_utenti_commenti()
            if ordina=="Esperienze":
                utenti = ordina_utenti_popolari()

            if popolari:
                utentiP= utenti_popolari()
                print(utentiP)

                utenti= list(set(utenti) & set(utentiP))

            return render(request, 'sentieriApp/elencoUtenti.html',
                          {'utenti': utenti, 'form': filtro})

    else:
        filtro = FiltroUtenti()

    utenti = ordina_utenti_username()
    return render(request, 'sentieriApp/elencoUtenti.html', {'utenti': utenti, 'form': filtro})



def elencoSentieriDiUtente(request, idUtente):
    return render(request, 'sentieriApp/elencoSentieriDiUtente.html', {'sentieri' : sentieri_effettuati(idUtente)})

def elencoSentieriDiUnLuogo(request, idLuogo):
    return render(request, 'sentieriApp/elencoSentieriDiUnLuogo.html', {'sentieri' : sentieri_di_un_luogo(idLuogo)})

def commentiDiUtente(request, idUtente):
    return render(request, 'sentieriApp/commentiDiUtente.html', {'commenti' : commenti_di_un_utente(idUtente)})




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

    return render(request, 'sentieriApp/dettagliUtente.html', {"utente": utentePubblico(idUtente),
                                                               "sentieri_effettuati": sentieri_effettuati(idUtente),
                                                               "commenti": commenti_di_un_utente(idUtente)})

def dettagliLuogo(request, idLuogo):
    luogo = informazioni_luogo(idLuogo)
    ptogeog = PuntoGeografico.objects.get(luogo__id=idLuogo)
    print(ptogeog.posizione)
    coordinate = str(ptogeog.posizione).replace(',', ', ')
    print(coordinate)
    return render(request, 'sentieriApp/dettagliLuogo.html', {'coordinate': coordinate, 'luogo':luogo, 'sentieri':sentieri_di_un_luogo(idLuogo)})



def dettagliPuntoGeografico(request, idPtoGeografico):
    ptogeog = get_object_or_404(PuntoGeografico, pk=idPtoGeografico)
    coordinate = str(ptogeog.posizione).replace(',', ', ')
    print(coordinate)
    return render(request, 'sentieriApp/puntoGeografico.html', {'coordinate': coordinate, 'punto': ptogeog, "sentieri": sentieri_partenza_pto_geog(idPtoGeografico)})




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

