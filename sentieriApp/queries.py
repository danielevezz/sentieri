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
                select distinct utente.id, username, sesso, eta, count(distinct esperienza.sentiero_id) as percorsieffettuati, count((NULLIF(commento.testo,''))) as commenti
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


def luoghi_di_un_sentiero(idSentiero):
    query = """select luogo.*
                from tappa
                join luogo
                on luogo.id = tappa.luogo_id
                where tappa.sentiero_id =""" + str(idSentiero)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def sentieri_di_un_luogo(idLuogo):
    query = """select sentiero.*
                from sentiero
                join tappa
                on sentiero.id = tappa.sentiero_id
                where tappa.luogo_id ="""+str(idLuogo)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def informazioni_luogo(idLuogo):
    query = """select luogo.nome as nome_luogo, luogo.descrizione as descrizione_luogo,
                luogo.sito, tipologia_luogo.nome as nome_tipo, tipologia_luogo.descrizione as descrizione_tipo, 
                punto_geografico.id as ptoGeografico_id
                from luogo
                join tipologia_luogo
                on luogo."tipoLuogo_id"= tipologia_luogo.id
                join punto_geografico
                on luogo."ptoGeografico_id" = punto_geografico.id
                where luogo.id =""" + str(idLuogo)
    with connection.cursor() as cursor:
        cursor.execute(query)
        row = cursor.fetchone()
    return row


def utenti_popolari():
    media = """ select avg (numeroEsperienze) 
                    from 
    					    (select count(esperienza.id) as numeroEsperienze
    						from esperienza
    						join utente on utente.id = esperienza.user_id
    						group by utente.id) as foo"""

    query = """
                select utente.id, utente.username, count(distinct esperienza.sentiero_id) as esperienze, count((NULLIF(commento.testo,''))) as commenti
                from utente

                join esperienza
                on esperienza.user_id = utente.id
				
				left join commento
                on commento.esperienza_id = esperienza.id
            
				group by utente.id
                having count(distinct esperienza.id) >= (""" + media + ")"

    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def ordina_utenti_popolari():
    query = """
                 select utente.id, utente.username, count(distinct esperienza.sentiero_id) as esperienze, count((NULLIF(commento.testo,''))) as commenti
                from utente

                join esperienza
                on esperienza.user_id = utente.id
                
                left join commento
                on commento.esperienza_id = esperienza.id
                
				group by utente.id
                order by esperienze desc
               """

    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def ordina_utenti_username():
    query = """
                 select utente.id, utente.username, count(distinct esperienza.sentiero_id) as esperienze, count((NULLIF(commento.testo,''))) as commenti
                from utente

                join esperienza
                on esperienza.user_id = utente.id
				
				 left join commento
                on commento.esperienza_id = esperienza.id
            
				group by utente.id
                order by username
               """

    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def ordina_utenti_commenti():

    query = """
                select utente.id, utente.username, count(distinct esperienza.sentiero_id) as esperienze, count((NULLIF(commento.testo,''))) as commenti
                from utente

                join esperienza
                on esperienza.user_id = utente.id
               
				 left join commento
                on commento.esperienza_id = esperienza.id
            
				group by utente.id
                order by commenti desc
               """

    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
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

def sentieri_piu_percorsi():
    query = """ select * from dati_sentiero order by partecipanti desc limit 5"""
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def sentieri_piu_votati():
    query = """  select *  from dati_sentiero order by mediavoti desc limit 5"""
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table


def sentieri_partenza_pto_geog(idPtoGeog):
    return Sentiero.objects.filter(ptoGeograficoPartenza=idPtoGeog)

def ordina_sentieri_per_voto():
    query = """  select *  from dati_sentiero order by mediavoti desc"""
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def ordina_sentieri_per_percorrenze():
    query = """  select *  from dati_sentiero order by partecipanti desc """
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def ordina_sentieri_per_titolo():
    query = """  select *  from dati_sentiero order by titolo """
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
            from utente

            join esperienza
            on esperienza.user_id = utente.id
               
			left join commento
            on commento.esperienza_id = esperienza.id
				
			left join sentiero
			on sentiero.id = esperienza.sentiero_id
				
			where commento.testo <> '' and utente.id = """ + str(idUser)
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

            where commento.testo <> ''
            and sentiero.id = """ + str(idSentiero)

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


def info_complete_sentieri_id(idSentieri, ordersID):

    query = """select * from dati_sentiero join (
                     select *
                     from unnest(array["""+idSentieri+"""]) with ordinality
                    ) as x (id, ordering) on dati_sentiero.id = x.id
                order by x.ordering"""
    print(query)
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def info_complete_sentieri():

    query = "select * from dati_sentiero"
    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table

def info_complete_sentieri():
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
                ROUND( AVG(esperienza.difficolta),2 ) as difficoltamedia,
                sentiero.lunghezza

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

    with connection.cursor() as cursor:
        cursor.execute(query)
        table = cursor.fetchall()
    return table