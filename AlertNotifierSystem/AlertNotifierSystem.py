import logging
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import smtplib
from email.mime.text import MIMEText
import requests
from prometheus_client import start_http_server, Counter, Gauge
import os
import time

bot_token = "7587852566:AAH0pXlB_VHM-UW1BZwhed5A9WzQnvLd5y8"  # Token del bot
chat_id = "324775130"  # chat_id qui 
app_password = 'tfcf qupn tqay lbuq'

SERVICE_NAME = os.getenv("SERVICE_NAME", "alert-notifier")
NODE_NAME = os.getenv("NODE_NAME", "worker")

# Metriche

# Metrica tipo Counter per il numero totale di email inviate con successo
EMAIL_SENT = Counter(
    'email_sent_total',
    'Numero totale di email inviate con successo',
    ['message_type', 'service', 'node']  
)
# Metrica tipo Counter per il numero totale di messaggi Telegram inviati con successo
TELEGRAM_MESSAGE_SENT = Counter(
    'telegram_messages_sent_total',
    'Numero totale di messaggi Telegram inviati con successo',
    ['message_type', 'service', 'node']  
)

# Metrica tipo Counter per il numero totale di errori durante l'invio dell'email
EMAIL_SEND_ERRORS = Counter(
    'email_send_errors_total', 
    'Numero totale di errori durante l\'invio di email',
    ['service', 'node']  
)

# Metrica tipo Counter per il numero totale di errori durante l'invio di messaggi Telegram
TELEGRAM_SEND_ERRORS = Counter(
    'telegram_send_errors_total', 
    'Numero totale di errori durante l\'invio di messaggi Telegram',
    ['service', 'node']  # Le etichette per il servizio e il nodo
)

# Metrica tipo Gauge per la latenza dell'invio dell'email (tempo impiegato per inviarla)
EMAIL_SEND_LATENCY = Gauge(
    'email_send_latency_seconds',
    'Latenza dell\'invio dell\'email',
    ['service', 'node', 'message_type']
)

# Metrica tipo Gauge per la latenza dell'invio del messaggio Telegram (tempo impiegato per inviarlo)
TELEGRAM_SEND_LATENCY = Gauge(
    'telegram_send_latency_seconds',
    'Latenza dell\'invio del messaggio Telegram',
    ['service', 'node', 'message_type']
)

consumer_config = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:29092'),
    'group.id': 'group2',  
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest',  
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer = Consumer(consumer_config)  # Inizializza il Kafka consumer
topic_to_consume = 'to-notifier'  # Topic da cui leggere messaggi
# Funzione per inviare notifiche tramite Telegram

def send_telegram_message(message, chat_id):
    """Invia un messaggio tramite Telegram"""
    start_time = time.time()

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logger.info("Messaggio Telegram inviato con successo!")
         # Incrementa la metrica per il messaggio Telegram inviato
            TELEGRAM_MESSAGE_SENT.labels(message_type="alert", service=SERVICE_NAME, node=NODE_NAME).inc()
            end_time = time.time()
            latency = end_time - start_time
            TELEGRAM_SEND_LATENCY.labels(service=SERVICE_NAME, node=NODE_NAME, message_type="alert").set(latency)        
        else:
            logger.error("Errore nell'invio del messaggio Telegram: %s", response.json())
            TELEGRAM_SEND_ERRORS.labels(service=SERVICE_NAME, node=NODE_NAME).inc()  # Incrementa gli errori
    except Exception as e:
        logger.error("Errore nella connessione con Telegram: %s", e)
        TELEGRAM_SEND_ERRORS.labels(service=SERVICE_NAME, node=NODE_NAME).inc()  # Incrementa gli errori

        
# Funzione per inviare email tramite Gmail SMTP
def send_email(to_email, subject, body):
    start_time = time.time()

    try:
        # Crea il messaggio email
        msg = MIMEText(body)  # Imposta il corpo dell'email
        msg['Subject'] = subject  # Imposta l'oggetto
        msg['From'] = 'hwdsbd@gmail.com'  # Sostituisci con il tuo indirizzo Gmail
        msg['To'] = to_email  # Imposta il destinatario

        # Configura il server SMTP di Gmail
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Avvia la connessione TLS
            server.login('hwdsbd@gmail.com', app_password)  # Login con Gmail App Password
            server.send_message(msg)  # Invia il messaggio
            logger.info("Email inviata con successo a: %s", to_email)
            EMAIL_SENT.labels(message_type="alert_email", service=SERVICE_NAME, node=NODE_NAME).inc()
            # Variabili di stato per memorizzare messaggi ricevuti
            # Sottoscrivi il consumer al topic desiderato
            end_time = time.time()
            latency = end_time - start_time
            EMAIL_SEND_LATENCY.labels(service=SERVICE_NAME, node=NODE_NAME, message_type="alert_email").set(latency)
    except Exception as e:
        logger.error("Errore nell'invio dell'email a %s: %s", to_email, e)
              # Incrementa la metrica per il numero di errori durante l'invio dell'email
        EMAIL_SEND_ERRORS.labels(service=SERVICE_NAME, node=NODE_NAME).inc()
  

consumer.subscribe([topic_to_consume])

def run():

    received_messages = []  # Buffer per memorizzare i messaggi in arrivo

    try:
        while True:
            # Poll per un nuovo messaggio dal topic Kafka
            msg = consumer.poll(300.0)  # Aspetta fino a 5 minutinper un messaggio
            if msg is None:
                # Nessun messaggio ricevuto entro il tempo di polling
                continue
            if msg.error():
                # Gestione di errori durante il consumo
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info("Fine della partizione raggiunta: %s [%s]",
                                msg.topic(), msg.partition())
                else:
                    logger.error("Errore del consumer: %s", msg.error())
                continue

            # Decodifica il messaggio ricevuto (assunto JSON)
            data = json.loads(msg.value().decode('utf-8'))

            received_messages.append(data)  # Add the parsed message to the buffer

            # Commette l'offset manualmente per garantire che il messaggio venga processato solo una volta
            consumer.commit(asynchronous=False)
            logger.info("Offset commesso per il messaggio: %s", msg.offset())

            # Verifica che il messaggio sia una lista di dizionari
            if isinstance(received_messages, list):
                for item in data:
                    # Verifica che l'elemento contenga le informazioni necessarie
                    if 'email' in item and 'ticker' in item and 'condition' in item and 'latest_value' in item:
                        # Prepara l'email per l'utente
                        subject = f"Alert per {item['ticker']}"
                        body = (
                            f"Salve,\n\n"
                            f"Il ticker '{item['ticker']}' ha attivato la seguente condizione:\n"
                            f"{item['condition']}\n"
                            f"Valore più recente: {item['latest_value']}\n\n"
                            f"Distinti saluti,\nSistema di Notifiche Alert"
                        )
                        # Invia l'email
                        send_email(item['email'], subject, body)

                        # Prepara e invia la notifica Telegram (se chat_id è presente)
                        if 'chat_id' in item and item['chat_id']:
                            telegram_message = (
                                f"🚀 Alert: Il ticker '{item['ticker']}' ha attivato la seguente condizione:\n"
                                f"{item['condition']}\n"
                                f"Valore più recente: {item['latest_value']}"
                            )
                            send_telegram_message(telegram_message, item['chat_id'])

                        received_messages = []
                    else:
                        logger.warning("Elemento incompleto ricevuto: %s", item)
            else:
                logger.warning("Messaggio ricevuto non è una lista. Ignorato.")

    except KeyboardInterrupt:
        # Interruzione pulita del consumer
        logger.info("Consumer interrotto dall'utente.")
    finally:
        # Chiudi il consumer quando l'app termina
        consumer.close()
        logger.info("Consumer di Kafka chiuso.")


if __name__ == "__main__":
    # Avvia l'HTTP server su una porta specifica (es. 8000)
    start_http_server(port=50056)
    logger.info("Prometheus metrics server started on port 50056")

    run()

