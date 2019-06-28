from django.shortcuts import render, get_object_or_404, redirect
from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale
from .forms import CreazioneAccount, InserisciEsperienza
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


def dettagliSentiero(request, idSentiero):
    query = "select * from dati_sentiero where id = " + str(idSentiero)
    with connection.cursor() as cursor:
        cursor.execute(query)
        sentiero = cursor.fetchone()
    if sentiero.__len__() == 0:
        raise Http404
    return render(request, 'sentieriApp/dettagliSentiero.html', {'sentiero': sentiero})


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
            """
    return Sentiero.objects.raw(query, [stringa])

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
            select distinct sentiero.id, sentiero.titolo, commento.id, commento.testo
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
            select distinct sentiero.id, sentiero.titolo, commento.id, commento.testo, utente.username
            from esperienza

            join commento
            on commento.esperienza_id = commento.id

            join sentiero
            on sentiero.id = esperienza.sentiero_id
            
            join utente
            on utente.id = esperienza.user_id

            where sentiero.id = """ + str(idSentiero)
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
                
                where arrivo.provincia_id = %s Or partenza.provincia_id = """ + str(idProvincia)
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
                                                            where e1.sentiero_id = e2.sentiero_id and """ + str(idProvincia) + """ <> u2.residenza_id
                                                            )
                                            )
                
                """
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