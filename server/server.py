import os
import grpc
from concurrent import futures
import service_pb2, service_pb2_grpc
import mysql.connector
import mysql.connector.errors
from threading import Lock
from datetime import datetime
import CQRS_Pattern.command_db as command_db
import CQRS_Pattern.lecture_db as lecture_db
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time 
import threading 
import uuid


cache = {
    "request_cache": {},
    "update_cache": {},
}

cache_lock = Lock()

# Tempo di validità di ogni entry (TTL), in secondi
CACHE_TTL_SECONDS = 600  # 10 minuti

# Intervallo di pulizia periodica (in secondi)
CLEAN_INTERVAL = 1800  # 30 minuti

SESSION_STORE = {} 

MAX_TOKEN_AGE_SECONDS = 86400  # 1 giorno

SERVICE_NAME = os.getenv("SERVICE_NAME", "server")
NODE_NAME = os.getenv("NODE_NAME", "worker")

# Metrica tipo Counter per contare il numero totale di richieste gRPC ricevute
REQUEST_COUNT = Counter(
    'grpc_requests_total', 
    'Numero totale di richieste ricevute', 
    ['method', 'success', 'service', 'node']
)

# Metrica tipo Counter per contare il numero totale di errori nelle richieste gRPC
ERROR_COUNT = Counter(
    'grpc_errors_total', 
    'Numero totale di errori', 
    ['method', 'service', 'node'] 
)


# Metrica tipo Gauge per misurare la durata della sessione utente in secondi
USER_SESSION_DURATION = Gauge(
    'grpc_user_session_duration_seconds', 
    'Durata della sessione utente in secondi',
    ['service', 'node'] 
)

# Metrica tipo Histogram per monitorare la durata delle richieste gRPC
REQUEST_DURATION = Histogram(
    'grpc_request_duration_seconds', 
    'Durata delle richieste gRPC in secondi',
    ['method', 'success', 'service', 'node']
)


def clean_up_cache():
    """
    Funzione eseguita dal thread che pulisce periodicamente
    il contenuto della cache rimuovendo le entry scadute.
    """
    while True:
        # Dorme per CLEAN_INTERVAL secondi prima di ricontrollare
        time.sleep(CLEAN_INTERVAL)
        
        now = time.time()
        with cache_lock:
            # Pulisci request_cache
            keys_to_remove = []
            for key, value in cache["request_cache"].items():
                saved_time = value.get("timestamp", 0)
                if now - saved_time > CACHE_TTL_SECONDS:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del cache["request_cache"][key]
            
            # Pulisci update_cache
            keys_to_remove = []
            for key, value in cache["update_cache"].items():
                saved_time = value.get("timestamp", 0)
                if now - saved_time > CACHE_TTL_SECONDS:
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del cache["update_cache"][key]

def start_cleaner_thread():
    """
    Crea e avvia il thread che eseguirà periodicamente 'clean_up_cache()'.
    """
    cleaner_thread = threading.Thread(
        target=clean_up_cache,
        daemon=True  # In modo che si chiuda se il main thread termina
    )
    cleaner_thread.start()

class EchoService(service_pb2_grpc.EchoServiceServicer):
    
    #Read
    def LoginUser(self, request, context):
        "Login Utente"
        # Inizia a misurare la durata
        start_time = time.time()
        read_service=lecture_db.ReadService()
        try:
            
            # Genera session_token univoco
            token = str(uuid.uuid4())
            
            SESSION_STORE[token] = {
            "email": request.email,
            "creation_time": time.time()
            }


            read_service.login_user(request.email)
            
            response=service_pb2.LoginUserReply(
                success=True, 
                message=f"Ti stiamo reindirizzando alla pagina principale",
                session_token=token
            )
            # Incrementa il contatore delle richieste con successo
            REQUEST_COUNT.labels(method='LoginUser', success='true', service=SERVICE_NAME, node=NODE_NAME).inc()

            return response
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.LoginUserReply(
                success=False,
                message=str(e)
            )   
        # Se c'è un errore, incrementa il contatore degli errori
            REQUEST_COUNT.labels(method='LoginUser', success='false', service=SERVICE_NAME, node=NODE_NAME).inc()
            return response
        finally:
             # Misura la durata e la salva nel Histogram
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method='LoginUser', success='true' if response.success else 'false', service=SERVICE_NAME, node=NODE_NAME).observe(duration)

    #Write
    def RegisterUser(self, request, context):
        """Metodo per registrare un utente."""
        start_time = time.time()
        meta = dict(context.invocation_metadata())

        userid = meta.get('userid', 'unknown')

        print(f"Richiesta di registrazione da: UserID: {userid}")

        with cache_lock:
            entry = cache["request_cache"].get(userid)
            if entry:
                print(f"Risposta in cache per UserID {userid}")
                return entry["data"]
        

        cmd = command_db.RegisterUserCommand(
            email=request.email,
            ticker=request.ticker,
            max_value=request.max_value,
            min_value=request.min_value
        )

        write_service = command_db.WriteService()

        try:
            # Tenta di eseguire la logica di scrittura
            write_service.handle_register_user(cmd)
            
            # Genera session_token univoco
            token = str(uuid.uuid4())
            
            SESSION_STORE[token] = {
            "email": request.email,
            "creation_time": time.time()
            }


            response = service_pb2.RegisterUserReply(
                success=True, 
                message=f"Utente {request.email} registrato con successo!",
                session_token=token
            )

            with cache_lock:
                cache["request_cache"][userid] = {
                    "timestamp": time.time(),
                    "data": response  # qui metti la tua gRPC response
                }
              # Incrementa la metrica delle richieste
            REQUEST_COUNT.labels(method='RegisterUser', success='true', service=SERVICE_NAME, node=NODE_NAME).inc()
            return response

        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
           # Incrementa la metrica degli errori per questo metodo
            ERROR_COUNT.labels(method='RegisterUser', service=SERVICE_NAME, node=NODE_NAME).inc()
           
            response = service_pb2.RegisterUserReply(
                success=False,
                message=str(e)
            )
            with cache_lock:
                cache["request_cache"][userid] = {
                    "timestamp": time.time(),
                    "data": response  # qui metti la tua gRPC response
                }
            return response
        finally:
            # Misura la durata della richiesta e la registra nel histogram
            duration = time.time() - start_time
            REQUEST_DURATION.labels(method='RegisterUser', success='true' if response.success else 'false', service=SERVICE_NAME, node=NODE_NAME).observe(duration)
    #Write
    def UpdateUser(self, request, context):
        """Metodo per aggiornare il codice dell'azione dell'utente."""

        meta = dict(context.invocation_metadata())

        requestid = meta.get('requestid', 'unknown')

        print(f"Richiesta di aggionamento con RquestID: {requestid}")

        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        with cache_lock:
            entry = cache["update_cache"].get(requestid)
            if entry:
                print(f"Risposta in cache per RequestID {requestid}")
                return entry["data"]

        cmd = command_db.UpdateUserCommand(
            email=identifier,
            ticker_old=request.ticker_old,
            ticker=request.ticker,
            max_value=request.max_value,
            min_value=request.min_value
        )
        
        write_service = command_db.WriteService()
        try:
            write_service.handle_update_user(cmd)
        
        
            response = service_pb2.UpdateUserReply(
            success=True, 
            message=f"Codice dell'azione aggiornato per l'utente {identifier}!"
            )
            with cache_lock:
                cache["update_cache"][requestid] = {
                    "timestamp": time.time(),
                    "data": response
                }        
            return response
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.UpdateUserReply(
                success=False,
                message=str(e)
            )
            with cache_lock:
                cache["update_cache"][requestid] = {
                    "timestamp": time.time(),
                    "data": response
                }
        
            return response
        
    #Write
    def DeleteTickerUser(self, request,context):

        meta = dict(context.invocation_metadata())

        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]
       
        cmd = command_db.DeleteTickerUserCommand(
            email=identifier,
            ticker=request.ticker,
           
        )
        write_service = command_db.WriteService()
        try:
            # Tenta di eseguire la logica di scrittura
            write_service.handle_delete_ticker_user(cmd)
           
            response = service_pb2.DeleteTickerUserReply(
                success=True, 
                message=f"Ticker {request.ticker} dell'utente : {identifier} eliminato con successo!"
            )
            return response

        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.DeleteTickerUserReply(
                success=False,
                message=str(e)
            )
            return response
    #Write
    def DeleteUser(self,request,context):
        """Metodo per eliminare un utente."""

        meta = dict(context.invocation_metadata())

        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        cmd = command_db.DeleteUserCommand(
            email=identifier
           
        )
        write_service = command_db.WriteService()
       
        try:
            write_service.handle_delete_user(cmd)

            if session_token in SESSION_STORE:
                del SESSION_STORE[session_token]

            response = service_pb2.DeleteUserReply(
            success=True, 
            message=f"Utente {identifier} eliminato con successo!"
            )
            return response
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.DeleteTickerUserReply(
                success=False,
                message=str(e)
            )
            return response
    #Write 
    def AddTickerUtente(self, request, context):

        meta = dict(context.invocation_metadata())
        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        cmd = command_db.AddTickerCommand(
            email=identifier,
            ticker=request.ticker,
            max_value=request.max_value,
            min_value=request.min_value
           
        )
        write_service = command_db.WriteService()
        try:
            # Tenta di eseguire la logica di scrittura
            write_service.handle_addTicker(cmd)

            response = service_pb2.AddTickerUtenteReply(
                success=True, 
                message=f"Ticker {request.ticker} aggiunto all'utente {identifier}!"
        )
            return response
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.AddTickerUtenteReply(
                success=False,
                message=str(e)
            )
            return response


    #Write 
    #metodo per modificare il valore minimo e massimo di un ticker
    def UpdateMinMaxValue(self, request, context):

        meta = dict(context.invocation_metadata())
        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        # Crea il comando per l'aggiornamento
        cmd = command_db.UpdateMinMaxValueCommand(
        email=identifier,
        ticker=request.ticker,
        max_value=request.max_value,
        min_value=request.min_value
        )
        write_service = command_db.WriteService()
        try:
            # Tenta di eseguire la logica di scrittura
            write_service.handle_update_min_max_value(cmd)
            response = service_pb2.UpdateMinMaxValueReply(
            success=True,
            message=f"Valori aggiornati con successo per il ticker {request.ticker}!",
            ticker=request.ticker
        )
            return response
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.UpdateMinMaxValueReply(
                success=False,
                message=str(e),
                ticker=""
            )
            return response
        
    #Read 
    def ShowTickersUser(self, request, context):
        read_service=lecture_db.ReadService()

        meta = dict(context.invocation_metadata())
        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        try:
            tickers_list=read_service.show_ticker_user(identifier)
            response= service_pb2.ShowTickersUserReply(
                success=True,
                message="Ticker recuperati con successo",
                ticker=tickers_list
            )
            return response 
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response= service_pb2.ShowTickersUserReply(
                success=False,
                message=str(e),
                ticker=""
            )
        return response
        
       
        
    #Read
    def GetLatestValue(self, request, context):
        read_service=lecture_db.ReadService()

        meta = dict(context.invocation_metadata())
        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        try:
            stock_value, datetime_str =read_service.get_latest_value(identifier,request.ticker)
            response=service_pb2.GetLatestValueReply(
                success=True, 
                ticker=request.ticker, 
                stock_value=stock_value,
                timestamp=datetime_str
            )
            return response 
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response=service_pb2.GetLatestValueReply(
                success=False,
                ticker="",
                stock_value=0.0,
                timestamp="",
                message=str(e)
            )
        return response
    
    #Read
    def GetAverageValue(self, request, context):
        read_service=lecture_db.ReadService()

        meta = dict(context.invocation_metadata())
        session_token = meta.get('session_token', None)
        if not session_token:
            raise Exception("Manca il token. Fai login.")
        
        session_data = SESSION_STORE.get(session_token)
        if not session_data:
            raise Exception("Token non valido o vecchio e rimosso.")
        
        identifier = session_data["email"]

        try:
            average_stock_value,datetime_str =read_service.get_average_value(identifier,request.ticker,request.num_values)
            response= service_pb2.GetAverageValueReply(
                success=True,
                ticker = request.ticker,
                average_stock_value=average_stock_value, 
                timestamp=datetime_str
            )
            return response 
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response=service_pb2.GetAverageValueReply(
                success=False, 
                ticker=request.ticker,
                message=str(e),
                average_stock_value=0.0,
                timestamp=""
            )
        return response
    
def clean_up_sessions():
    while True:
        time.sleep(3600)  # Ogni ora, per esempio
        now = time.time()
        to_remove = []
        
        for token, session_data in SESSION_STORE.items():
            creation = session_data["creation_time"]
            # Se il token esiste da più di MAX_TOKEN_AGE_SECONDS, lo rimuovi
            if now - creation > MAX_TOKEN_AGE_SECONDS:
                to_remove.append(token)

        for t in to_remove:
            del SESSION_STORE[t]

def start_session_cleaner_thread():
    cleaner_thread = threading.Thread(
        target=clean_up_sessions,
        daemon=True
    )
    cleaner_thread.start()


# Funzione per avviare il server
def serve():
    # Avvia il server HTTP per Prometheus sulla porta 8000
    start_http_server(port=8000)
    port = '50052'
    
    # Creazione di un server gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    session_start_time = time.time()

    service_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    # Imposta l'indirizzo e la porta dove il server ascolterà
    server.add_insecure_port('[::]:' + port)

    print("Echo Service started, listening on " + port)
    # Aggiungi il contatore per le connessioni attive

    server.start()

    try:
        server.wait_for_termination()
    finally:
        session_end_time = time.time()
        session_duration = session_end_time - session_start_time
        USER_SESSION_DURATION.labels(service=SERVICE_NAME, node=NODE_NAME).set(session_duration)

if __name__ == '__main__':

    start_cleaner_thread()

    start_session_cleaner_thread()

    serve()
