from venv import logger
import requests
import mysql.connector
import time
import os
import CQRS_Pattern.lecture_db as lecture_db
import CQRS_Pattern.command_db as command_db
from prometheus_client import start_http_server, Counter, Gauge

node_name = os.getenv("NODE_NAME", "default_node")  # Utilizza una variabile di ambiente per il nome del nodo, valore di default se non esiste
SERVICE_NAME = os.getenv("SERVICE_NAME", "data-collector")
NODE_NAME = os.getenv("NODE_NAME", "unknown")

ERROR_COUNT = Counter(
    'telegram_api_errors_total',
    'Numero di errori nelle richieste API Telegram',
    ['error_type', 'service_name', 'node_name']  # Aggiunta label error_type per distinguere i tipi di errore
)
# Metriche di tipo Gauge
CHAT_ID_COUNT = Gauge(
    'telegram_chat_id_count',
    'Numero di chat_id associati a un\'email, suddivisi per stato dell\'utente',
    ['user_status', 'service_name', 'node_name']  # Aggiunta label user_status e node_name
)
MESSAGE_SENT_COUNT = Counter(
    'telegram_messages_sent_total',
    'Numero totale di messaggi inviati tramite il bot Telegram',
    ['message_type', 'service_name', 'node_name']  # Aggiunta label message_type per distinguere i tipi di messaggio
)
bot_token = os.getenv("BOT_TOKEN")

def email_exists_for_chat_id(chat_id):
    """Controlla se il chat_id è già associato a un'email nel database."""
    try:
        read_service = lecture_db.ReadService()
        email = read_service.CheckEmail(chat_id)
        if email:
            CHAT_ID_COUNT.labels(user_status="email_validata", service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label user_status per stato email validata
        else:
            CHAT_ID_COUNT.labels(user_status="email_non_valida", service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label user_status per stato email non valida
        return email is not None
    except Exception as e:
        print(f"Errore durante il controllo dell'email: {e}")
        ERROR_COUNT.labels(error_type="db_error",service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label error_type per errori nel DB
        return False

def send_telegram_message(message, chat_id):
    """Invia un messaggio tramite Telegram a uno specifico chat_id."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"Messaggio inviato con successo a chat_id {chat_id}.")
            ERROR_COUNT.labels(error_type="telegram_api_error", service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label error_type per errore API Telegram

        else:
            ERROR_COUNT.labels(error_type="telegram_api_error", service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label error_type per errore API Telegram
            print(f"Errore nell'invio del messaggio a chat_id {chat_id}: {response.json()}")
    except Exception as e:
        print(f"Errore nella connessione con Telegram: {e}")
        ERROR_COUNT.labels(error_type="telegram_api_error", service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label error_type per errore API Telegram

def save_chat_id_to_db(email, chat_id):
    """Aggiorna il campo chat_id nel database per un'email specifica."""

    command = command_db.SaveChatIdCommand(email, chat_id)
    write_service = command_db.WriteService()

    try:
        write_service.handle_save_chatId(command)

    except Exception as e:
        ERROR_COUNT.labels(error_type="db_error",service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label error_type per errore nel DB
        print(f"messaggio: {e}")
   

def get_updates_and_process():
    """Ascolta continuamente gli aggiornamenti dal bot Telegram."""
    last_update_id = None  # Per tenere traccia dell'ultimo aggiornamento elaborato
    while True:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        if last_update_id:
            url += f"?offset={last_update_id + 1}"  # Prendi solo i nuovi aggiornamenti
        try:
            response = requests.get(url)
            updates = response.json()
            if updates.get("result"):
                for update in updates["result"]:
                    if 'message' in update and 'text' in update['message']:
                        chat_id = update['message']['chat']['id']
                        message = update['message']['text']
                        last_update_id = update['update_id']  # Aggiorna l'ultimo ID elaborato

                        # Controlla se il chat_id è già associato a un'email
                        if not email_exists_for_chat_id(chat_id):
                            send_telegram_message("Per favore, invia la tua email per completare la configurazione.", chat_id)
                        else:
                            print(f"Chat ID {chat_id} già associato a un'email.")

                        # Salva il chat_id se il messaggio contiene un'email valida
                        if "@" in message:
                            save_chat_id_to_db(message.strip(), chat_id)
        except Exception as e:
            print(f"Errore durante il recupero degli aggiornamenti Telegram: {e}")
            ERROR_COUNT.labels(error_type="telegram_api_error", service_name=SERVICE_NAME, node_name=NODE_NAME).inc()  # Aggiungi label error_type per errore API Telegram

        time.sleep(5)  # Evita di sovraccaricare le richieste all'API Telegram

if __name__ == "__main__":
    print("Avvio del bot Telegram per monitorare aggiornamenti...")

    start_http_server(port=50053)
    logger.info("Prometheus metrics server started on port 50054")
    
    get_updates_and_process()
