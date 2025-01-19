import logging
import requests
import mysql.connector
import time
import os
import CQRS_Pattern.lecture_db as lecture_db
import CQRS_Pattern.command_db as command_db
from prometheus_client import start_http_server, Counter, Gauge

SERVICE_NAME = os.getenv("SERVICE_NAME", "telegram-bot")
NODE_NAME = os.getenv("NODE_NAME", "worker")

# Metrica tipo Counter per contare il numero totale di messaggi inviati tramite il bot Telegram
MESSAGE_SENT_COUNT = Counter(
    'telegram_messages_sent_total',
    'Numero totale di messaggi inviati tramite il bot Telegram',
    ['message_type', 'service', 'node']  
)

# Metrica tipo Counter per contare il numero totale di errori nelle richieste API Telegram
ERROR_COUNT = Counter(
    'telegram_api_errors_total',
    'Numero di errori nelle richieste API Telegram',
    ['error_type', 'service', 'node'] 
)

# Metrica tipo Gauge per monitorare la latenza delle risposte API Telegram in secondi
TELEGRAM_API_RESPONSE_LATENCY = Gauge(
    'telegram_api_response_latency_seconds',
    'Tempo di latenza delle risposte dall\'API Telegram',
    ['service', 'node']
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token = os.getenv("BOT_TOKEN")

def email_exists_for_chat_id(chat_id):
    """Controlla se il chat_id è già associato a un'email nel database."""
    try:
        read_service = lecture_db.ReadService()
        email = read_service.CheckEmail(chat_id)
        return email is not None
    except Exception as e:
        logger.error("Errore durante il controllo dell'email: %s", e)
        ERROR_COUNT.labels(error_type="db_error", service=SERVICE_NAME, node=NODE_NAME).inc()
        return False

def send_telegram_message(message, chat_id):
    """Invia un messaggio tramite Telegram a uno specifico chat_id."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logger.info("Messaggio inviato con successo a chat_id %s.", chat_id)
            MESSAGE_SENT_COUNT.labels(
                message_type="alert",
                service=SERVICE_NAME,
                node=NODE_NAME
            ).inc()
        else:
            ERROR_COUNT.labels(error_type="telegram_api_error", service=SERVICE_NAME, node=NODE_NAME).inc()
            logger.error("Errore nell'invio del messaggio a chat_id %s: %s", chat_id, response.json())
    except Exception as e:
        logger.error("Errore nella connessione con Telegram: %s", e)
        ERROR_COUNT.labels(error_type="telegram_api_error", service=SERVICE_NAME, node=NODE_NAME).inc()

def save_chat_id_to_db(email, chat_id):
    """Aggiorna il campo chat_id nel database per un'email specifica."""
    command = command_db.SaveChatIdCommand(email, chat_id)
    write_service = command_db.WriteService()

    try:
        write_service.handle_save_chatId(command)
    except Exception as e:
        ERROR_COUNT.labels(error_type="db_error", service=SERVICE_NAME, node=NODE_NAME).inc()
        logger.error("messaggio: %s", e)

def get_updates_and_process():
    last_update_id = None  # Per tenere traccia dell'ultimo aggiornamento elaborato
    while True:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        if last_update_id:
            url += f"?offset={last_update_id + 1}"  
        try:
            start_time = time.time()  # Inizio temporizzazione
            response = requests.get(url)
            latency = time.time() - start_time  # Calcola la latenza
            TELEGRAM_API_RESPONSE_LATENCY.labels(service=SERVICE_NAME, node=NODE_NAME).set(latency)

            updates = response.json()
            if updates.get("result"):
                for update in updates["result"]:
                    if 'message' in update and 'text' in update['message']:
                        chat_id = update['message']['chat']['id']
                        message = update['message']['text']
                        last_update_id = update['update_id']

                        # Controlla se il chat_id è già associato a un'email
                        if not email_exists_for_chat_id(chat_id):
                            send_telegram_message("Per favore, invia la tua email per completare la configurazione.", chat_id)
                        else:
                            logger.info("Chat ID %s già associato a un'email.", chat_id)

                        # Salva il chat_id se il messaggio contiene un'email valida
                        if "@" in message:
                            save_chat_id_to_db(message.strip(), chat_id)
        except Exception as e:
            logger.error("Errore durante il recupero degli aggiornamenti Telegram: %s", e)
            ERROR_COUNT.labels(error_type="telegram_api_error", service=SERVICE_NAME, node=NODE_NAME).inc()

        time.sleep(5)

if __name__ == "__main__":
    logger.info("Avvio del bot Telegram per monitorare aggiornamenti...")

    start_http_server(port=50053)
    logger.info("Prometheus metrics server started on port 50053")
    
    get_updates_and_process()
