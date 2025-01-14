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

cache = {
    "request_cache": {},
    "update_cache": {},
}

cache_lock = Lock()

identifier = None
SERVICE_NAME = os.getenv("SERVICE_NAME", "data-collector")
NODE_NAME = os.getenv("NODE_NAME", "unknown")

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

# Metrica tipo Gauge per monitorare il numero di connessioni attive al servizio gRPC
ACTIVE_CONNECTIONS = Gauge(
    'grpc_active_connections', 
    'Numero di connessioni attive',
    ['status', 'service', 'node'] 
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

class EchoService(service_pb2_grpc.EchoServiceServicer):
    
    #Read
    def LoginUser(self, request, context):
        "Login Utente"
        # Inizia a misurare la durata
        start_time = time.time()
        read_service=lecture_db.ReadService()
        try:
            
            global identifier
            identifier= request.email
            read_service.login_user(request.email)
            
            response=service_pb2.LoginUserReply(
                success=True, 
                message=f"Ti stiamo reindirizzando alla pagina principale"
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
            if userid in cache["request_cache"]:
                print(f"Risposta in cache per UserID {userid}")
                return cache["request_cache"][userid]
        

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
            
            global identifier
            identifier = request.email

            response = service_pb2.RegisterUserReply(
                success=True, 
                message=f"Utente {request.email} registrato con successo!"
            )

            with cache_lock:
                cache["request_cache"][userid] = response
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
                cache["request_cache"][userid] = response
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

        with cache_lock:
            if requestid in cache["update_cache"]:
                print(f"Risposta in cache per RequestID {requestid}")
                return cache["update_cache"][requestid]

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
                cache["update_cache"][requestid] = response
        
            return response
        except Exception as e:
        # Se c'è stata un'eccezione, significa che c'è un problema di connessione
        # o l'utente esiste già nel DB, o altre cause.
            response = service_pb2.UpdateUserReply(
                success=False,
                message=str(e)
            )
            with cache_lock:
                cache["update_cache"][requestid] = response
        
            return response
        
    #Write
    def DeleteTickerUser(self, request,context):
       
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
        cmd = command_db.DeleteUserCommand(
            email=identifier
           
        )
        write_service = command_db.WriteService()
       
        try:
            write_service.handle_delete_user(cmd)
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
# Funzione per avviare il server
def serve():
    # Avvia il server HTTP per Prometheus sulla porta 8000
    start_http_server(port=8000)
    port = '50052'
    
    # Creazione di un server gRPC
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    session_start_time = time.time()

    service_pb2_grpc.add_EchoServiceServicer_to_server(EchoService(), server)
    ACTIVE_CONNECTIONS.labels(status='open', service=SERVICE_NAME, node=NODE_NAME).inc()
    # Imposta l'indirizzo e la porta dove il server ascolterà
    server.add_insecure_port('[::]:' + port)

    print("Echo Service started, listening on " + port)
    # Aggiungi il contatore per le connessioni attive
    ACTIVE_CONNECTIONS.labels(status='closed', service=SERVICE_NAME, node=NODE_NAME).dec()

    server.start()
     # Quando l'utente termina la sessione
    session_end_time = time.time()
    session_duration = session_end_time - session_start_time
    
    # Imposta la durata della sessione nella metrica
    USER_SESSION_DURATION.labels(service=SERVICE_NAME, node=NODE_NAME).set(session_duration)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
