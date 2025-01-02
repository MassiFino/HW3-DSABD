import os
from datetime import datetime
import mysql.connector
import yfinance as yf
import time
from circuit import CircuitBreaker, CircuitBreakerOpenException
from confluent_kafka import Producer
import json
import CQRS_Pattern.lecture_db as lecture_db
import CQRS_Pattern.command_db as command_db
import logging

# Configurazione di base del logging
logging.basicConfig(
    level=logging.DEBUG,  # Imposta il livello minimo di log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',  # Formato dei log
    datefmt='%Y-%m-%d %H:%M:%S'  # Formato della data
)

# Creazione di un logger specifico per questo modulo
logger = logging.getLogger(__name__)

# Configurazione del Circuit Breaker
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)

producer_config = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:29092'),
    'acks': 'all',
    'max.in.flight.requests.per.connection': 1,
    'retries': 3
}

producer = Producer(producer_config)
topic = os.getenv('KAFKA_TOPIC', 'to-alert-system')

def get_tickers():
    """
    Recupera ticker associati dal database.
    :return: Lista di tuple (ticker).
    """
    read_service = lecture_db.ReadService()

    try:
        tickers = read_service.ShowTicker()
        return tickers
    except Exception as e:
        logger.error(f"Recupero ticker fallito: {e}")
        return []

def save_ticker_data(ticker, value, timestamp):
    """
    Salva i dati dei ticker recuperati nel database.
    :param ticker: Codice del titolo azionario.
    :param value: Valore del titolo.
    :param timestamp: Timestamp corrente.
    """
    command = command_db.SaveTickerDataCommand(ticker, value, timestamp)

    write_service = command_db.WriteService()

    try:
        write_service.handle_ticker_data(command)
    except Exception as e:
        logger.error(f"Salvataggio dati fallito: {e}")

# Funzione per Processare i Ticker con il Circuit Breaker

def get_stock_price(ticker):
    """
    Recupera l'ultimo valore disponibile per il titolo azionario specificato.
    :param ticker: Codice del titolo azionario.
    :return: Ultimo prezzo disponibile come float.
    """
    try:
        # Chiamata al metodo `history()` di yfinance protetta dal Circuit Breaker
        stock_data = yf.Ticker(ticker)
  
        history = circuit_breaker.call(stock_data.history, period="1d")
        if history.empty:
            logger.warning(f"Nessun dato disponibile per il ticker: {ticker}")
            return None

        # Ottieni il prezzo di chiusura più recente
        last_price = history['Close'].iloc[-1]
        return float(last_price)
    except CircuitBreakerOpenException:
        logger.error(f"Circuit breaker aperto. Operazione saltata per {ticker}.")
    except Exception as e:
        logger.error(f"Recupero prezzo per {ticker} fallito: {e}")
        raise Exception(f"Recupero prezzo per {ticker} fallito: {e}")

def process_ticker(ticker):
    """
    Processa un singolo ticker per un utente.
    :param ticker: Codice del titolo azionario.
    """
    try:
        stock_price = get_stock_price(ticker)
        timestamp = datetime.now()
        save_ticker_data(ticker, stock_price, timestamp)
        logger.debug(f"Dati salvati per {ticker}: {stock_price} @ {timestamp}")
    except Exception as e:
        logger.error(f"Elaborazione fallita per {ticker}: {e}")

def delivery_report(err, msg):
    """Callback to report the result of message delivery."""
    if err:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def produce_async(producer, topic):
    timestamp = datetime.now().isoformat() 
    message = {'timestamp': timestamp, 'msg': 'aggiornamento valori completato'} 
    try:
        serialized_message = json.dumps(message).encode('utf-8')
        logger.debug(f"Serialized message: {serialized_message}")

        # Aggiungo la key, ad esempio "static_key". Puoi usare anche ticker, timestamp, ecc.
        producer.produce(
            topic=topic,
            key="static_key",  # la key
            value=serialized_message,
            callback=delivery_report
        )
        producer.flush()
        logger.debug(f"Produced: {message}")
    except Exception as e:
        logger.error(f"Failed to produce message: {e}")


def run():
    """
    Processo principale:
    - Recupera utenti e ticker dal database.
    - Per ogni ticker, scarica i dati.
    - Salva i dati nel database.
    """
    try:
        tickers = get_tickers()
        if not tickers:
            logger.info("Nessun dato da processare.")
            return

        for ticker in tickers:
            process_ticker(ticker)

        logger.info("Aggiornamento completato.")

    except Exception as e:
        logger.error(f"Errore generale durante l'esecuzione: {e}")

    produce_async(producer, topic)

if __name__ == "__main__":
    logger.info("Avvio del programma per l'aggiornamento dei ticker ogni 5 minuti.")
    while True:
        run()
        logger.info("Attesa di 5 minuti prima del prossimo aggiornamento.")
        time.sleep(300)
