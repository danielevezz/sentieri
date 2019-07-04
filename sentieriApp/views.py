from django.shortcuts import render, get_object_or_404, redirect
from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale, Commento, Categoria, Interessi, Preferito
from .forms import CreazioneAccount, InserisciEsperienza, SentieroPreferito
from django.contrib.auth import login, authenticate
from django.http import HttpResponseNotFound, Http404
from django.db import connection

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

    categorieR = request.GET.get('categorie')
    filtro = request.GET.get('filtro')

    if not categorieR:
        categorie = Categoria.objects.all()
        categorie = [c.nome for c in categorie]
    else:
        categorie = categorieR.split(",")

    sentieri = Sentiero.objects.filter(categoria__in=categorie)

    if filtro:
        print("filtro")
        filtro = filtro.split(",")
        print(filtro)
        sentieri = sentieri.filter(id = filtro[0])
        sentieri = sentieri.filter(titolo__contains=filtro[1])
    else:
        #sentieri = sentieri.filter(id = 1)
        print("no filtro")

    return render(request, 'sentieriApp/elencoSentieri.html', {'sentieri' : sentieri, 'categorie' : categorieR})

def elencoSentieriDiUtente(request, idUtente):
    return render(request, 'sentieriApp/elencoSentieriDiUtente.html', {'sentieri' : sentieri_effettuati(idUtente)})

def commentiDiUtente(request, idUtente):
    return render(request, 'sentieriApp/commentiDiUtente.html', {'commenti' : commenti_di_un_utente(idUtente)})



def selezionaCategorie(request):

    categorie = Categoria.objects.all()
    categorie = [c.nome for c in categorie]
    #
    if request.user.is_authenticated:
        mieCategorie = mie_categorie(request.user.id)
        mieCategorie = [i[0] for i in mieCategorie]
        mieCategorie = ",".join(mieCategorie)
    else:
        mieCategorie = []

    return render(request,'sentieriApp/selezionaCategorie.html', {'categorie' : categorie, 'mieCategorie' : mieCategorie})
    # return render(request, 'sentieriApp/selezionaCategorie.html')


def dettagliSentiero(request, idSentiero):
    query = "select * from dati_sentiero where id = " + str(idSentiero)
    with connection.cursor() as cursor:
        cursor.execute(query)
        sentiero = cursor.fetchone()
    if sentiero.__len__() == 0:
        raise Http404
    form = SentieroPreferito(request.GET or None)
    if request.method == "GET":
        if form.is_valid():
            check = form.cleaned_data.get('preferito')
            if check:
                preferito = Preferito(user=request.user, sentiero=Sentiero.objects.get(id=idSentiero))
                preferito.save()
            else:
                preferito = Preferito.objects.get(user=request.user, sentiero=Sentiero.objects.get(id=idSentiero))
                preferito.delete()

            return redirect("index")
        else:
            if Preferito.objects.filter(user=request.user, sentiero=Sentiero.objects.get(id=idSentiero)):
                form = SentieroPreferito(initial={'preferito': True})
            else:
                form = SentieroPreferito(initial={'preferito': False})
    return render(request, 'sentieriApp/dettagliSentiero.html', {'sentiero': sentiero, "commenti": commenti_di_un_sentiero(idSentiero), 'form': form})


def dettagliUtente(request, idUtente):
    if request.user.is_authenticated:
        if request.user.id == idUtente:
            utente = get_object_or_404(Utente, pk=idUtente)
            esperienze = EsperienzaPersonale.objects.filter(user_id=idUtente).select_related()
            return render(request, 'sentieriApp/dettagliUtente.html', {'utente': utente, 'esperienze': esperienze,
                                                                       'personale': True})

    return render(request, 'sentieriApp/dettagliUtente.html', {"utente": utentePubblico(idUtente)})


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
            """
    return Sentiero.objects.raw(query, [stringa])

def mie_categorie(idUser):
    query = """
                select categoria.nome
                from categoria
                join interesse
                on categoria.nome = interesse.categoria_id
                where interesse.user_id = """+str(idUser)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def utentePubblico(idUtente):
    query = """
                select distinct utente.id, username, sesso, eta, count(distinct esperienza.id) as percorsieffettuati, count (distinct commento.id) as commentifatti
                from utente

                left join esperienza
                on utente.id = esperienza.user_id

                left join commento
                on commento.esperienza_id = esperienza.id

                where utente.id = """ + str(idUtente) + """

                group by (utente.id, username, sesso, eta)"""

    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    return row


def utenti_popolari(numEsperienze):
    media = """ select avg (numeroEsperienze) 
                    from 
    					    (select count(esperienza.id) as numeroEsperienze
    						from esperienza
    						join utente on utente.id = esperienza.user_id
    						group by utente.id) as foo"""

    query = """
                select utente.id, utente.username
                from utente

                join esperienza
                on esperienza.user_id = utente.id

                group by utente.id
                having count(distinct esperienza.id) > (""" + media +")"


    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchone()
    return table


def sentieri_media_voti_piu_alta():
    media = """     select avg(mediavoti)
                    from dati_sentiero
                    group by dati_sentiero.id """
    query = """ select dati_sentiero
                from dati_sentiero
                group by dati_sentiero
                having avg(mediavoti) >= all ( """ + media + ")"
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def sentieri_media_voti_piu_alta_di(media):
    media = str(media)
    query = """ select dati_sentiero.id
                from dati_sentiero
                group by dati_sentiero.id
                having avg(mediavoti) >=  (""" + media + ")"
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def sentieri_effettuati(idUser):
    query = """
                select distinct sentiero.id, sentiero.titolo
                from sentiero

                join esperienza 
                on sentiero.id = esperienza.sentiero_id

                join utente
                on utente.id = esperienza.user_id

                where utente.id = """ + str(idUser)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
        return table


def commenti_di_un_utente(idUser):
    query = """
            select distinct sentiero.id, sentiero.titolo, commento.id, commento.testo, esperienza.voto
            from esperienza

            join commento
            on commento.esperienza_id = commento.id

            join sentiero
            on sentiero.id = esperienza.sentiero_id

            where esperienza.user_id = """ + str(idUser)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def commenti_di_un_sentiero(idSentiero):
    query = """
            select distinct sentiero.id, sentiero.titolo, commento.id, commento.testo, utente.username, utente.id
            from esperienza
            
            join commento
            on commento.esperienza_id = esperienza.id
            
            join sentiero
            on sentiero.id = esperienza.sentiero_id

            join utente
            on utente.id = esperienza.user_id
            
            where sentiero.id =""" + str(idSentiero)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
        return table


def sentieri_della_mia_citta(idProvincia):
    query = """
                select distinct sentiero.*
                from sentiero

                join punto_geografico as partenza
                on partenza.id = sentiero."ptoGeograficoPartenza_id"

                join punto_geografico as arrivo
                on arrivo.id = sentiero."ptoGeograficoArrivo_id"

                where arrivo.provincia_id = """ + str(idProvincia) + """ Or partenza.provincia_id = """ + str(
        idProvincia)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def sentieri_percorsi_solo_da_utenti_della_mia_citta(idProvincia):
    query = """
                select distinct sentiero.*
                from sentiero

                where sentiero.id not in ( select sentiero_id
                                            from esperienza e1
                                            join utente u1
                                            on u1.id = e1.user_id
                                            where exists (
                                                            select *
                                                            from esperienza e2
                                                            join utente u2
                                                            on u2.id = e2.user_id
                                                            where e1.sentiero_id = e2.sentiero_id and """ + str(
        idProvincia) + """ <> u2.residenza_id
                                                            )
                                            )

                """
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def quanti_commenti_fatti(idUser):
    query = """
               select count(*)

                from esperienza as e

                where e.user_id = """ + str(idUser) + """and exists(
                            select *
                            from commento
                            where commento.esperienza_id = e.id)"""
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    return row


def tutti_sentieri():
    query = """
                select sentiero.*
                from sentiero
                """
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def sentieri_di_una_categoria(categoriaID):
    query = """
                select sentiero.*
                from sentiero
                where sentiero.categoria_id like '""" + str(categoriaID) + "'"
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def sentieri_di_categorie_preferite(idUser):
    query = """
                select sentiero.*
                from sentiero
                where sentiero.categoria_id in (
                                                    select interesse.categoria_id
                                                    from interesse
                                                    where interesse.user_id = """ + str(idUser) + ")"
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def dati_sentiero():
    query = """
                Select Distinct 
                sentiero.id,
                sentiero.titolo,
                sentiero.durata,
                sentiero.descrizione,
                sentiero.dislivello,
                sentiero.salita,
                sentiero.discesa,
                sentiero."altitudineMax",
                sentiero."altitudineMin",
                sentiero.ciclico,
                sentiero."linkMappa",
                sentiero.difficolta_id,
                sentiero."ptoGeograficoArrivo_id",
                sentiero."ptoGeograficoPartenza_id",
                categoria.nome as categoria, 
                partenza.nome as partenza, 
                arrivo.nome as arrivo, 
                count(esperienza.id) as partecipanti, 
                count(distinct commento.id) as numeroCommenti, 
                round(avg(esperienza.voto),2) as mediavoti, 
                ROUND( AVG(esperienza.difficolta),2 ) as difficoltamedia

                from sentiero 

                left join punto_geografico as partenza
                on partenza.id = sentiero."ptoGeograficoPartenza_id"

                left join punto_geografico as arrivo
                on arrivo.id = sentiero."ptoGeograficoArrivo_id"

                left join categoria
                on sentiero.categoria_id = categoria.nome

                left join esperienza
                on sentiero.id = esperienza.sentiero_id

                left join commento
                on commento.esperienza_id = esperienza.id

                group by (sentiero.id, categoria.nome, partenza.nome, arrivo.nome )"""
    return Sentiero.objects.raw(query)