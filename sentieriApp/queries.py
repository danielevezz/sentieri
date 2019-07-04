from .models import Sentiero, Utente, PuntoGeografico, EsperienzaPersonale, Commento, Categoria
from django.db import connection

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
                where interesse.user_id = """ + str(idUser)
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
    query = """
                select utente.id, utente.username
                from utente

                join esperienza
                on esperienza.user_id = utente.id

                group by utente.id
                having count(distinct esperienza.id) >""" + str(numEsperienze)
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