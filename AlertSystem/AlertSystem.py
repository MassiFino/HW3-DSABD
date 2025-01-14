from datetime import datetime
from confluent_kafka import Consumer, Producer, KafkaException
import json
import CQRS_Pattern.lecture_db as lecture_db
import logging
import os
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time

# Configurazione del logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

SERVICE_NAME = os.getenv("SERVICE_NAME", "alert-system")
NODE_NAME = os.getenv("NODE_NAME", "worker")
# Kafka configuration for consumer and producer
consumer_config = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:29092'),
    'group.id': 'group1',  
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest', 
}

producer_config = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:29092'), 
    'acks': 'all',  # Ensure all in-sync replicas acknowledge the message
    'max.in.flight.requests.per.connection': 1,  # Ensure ordering of messages
    'retries': 3  # Number of retries for failed messages
}


# Metrica tipo Counter per il numero di messaggi consumati
MESSAGES_CONSUMED = Counter(
    'messages_consumed_total',
    'Numero totale di messaggi consumati dal topic to-alert-system',
    ['service', 'node']
)

# Metrica tipo Counter per il numero di messaggi prodotti
MESSAGES_PRODUCED = Counter(
    'messages_produced_total',
    'Numero totale di messaggi prodotti sul topic to-notifier',
    ['service', 'node']
)

# Metrica tipo Gauge per il numero di messaggi in attesa
MESSAGES_PENDING = Gauge(
    'messages_pending',
    'Numero di messaggi in attesa di essere prodotti',
    ['service', 'node']
)

# Metrica tipo Histogram per la durata dell'elaborazione dei messaggi
PROCESSING_TIME = Histogram(
    'message_processing_seconds',
    'Tempo impiegato per elaborare un messaggio',
    ['service', 'node']

)

# Metrica tipo Histogram per la latency delle query al database
DB_QUERY_LATENCY = Histogram(
    'db_query_latency_seconds',
    'Tempo impiegato per eseguire una query al database',
    ['service', 'node']
)


consumer = Consumer(consumer_config)
producer = Producer(producer_config)

topic1 = 'to-alert-system'  
topic2 = 'to-notifier'



consumer.subscribe([topic1])


def produce_sync(producer, topic, value):
    try:
        producer.produce(
            topic=topic,
            key="static_key",  # la key
            value=value
        )
        producer.flush()  
        logger.debug(f"Synchronously produced message to {topic}: {value}")
    except Exception as e:
        logger.error(f"Failed to produce message: {e}")


def run() :

    values = []

    try:
        while True:
            # Consuma un messaggio da Kafka
            msg = consumer.poll(300.0)  # Tempo massimo di attesa in secondi

            if msg is None:
                # Nessun messaggio disponibile, riprova
                logger.debug("Nessun messaggio ricevuto. Continuo ad aspettare...")
                continue  

            if msg.error():
                # Gestisce eventuali errori durante il consumo
                if msg.error().code() == KafkaException._PARTITION_EOF:
                    logger.info(f"Fine della partizione raggiunta {msg.topic()} [{msg.partition()}]")
                else:
                    logger.error(f"Errore del consumer: {msg.error()}")
                continue  # Salta al prossimo ciclo

            try:
                # Decodifica il messaggio
                data = json.loads(msg.value().decode('utf-8'))
                logger.info(f"Received: {data}")

                MESSAGES_CONSUMED.labels(service=SERVICE_NAME, node=NODE_NAME).inc()
                # Esegue la query per ottenere i valori da notificare
                read_service = lecture_db.ReadService()

                db_start_time = time.time()

                results = read_service.NotifierValues()

                db_duration = time.time() - db_start_time
                DB_QUERY_LATENCY.labels(service=SERVICE_NAME, node=NODE_NAME).observe(db_duration)
                
                for row in results:
                    email = row[0]
                    chat_id = row[1]
                    ticker = row[2]
                    latest_value = row[3]
                    condition = row[4]

                    messaggio = {
                        "email": email,
                        "chat_id": chat_id,
                        "ticker": ticker,
                        "condition": condition,
                        "latest_value": latest_value,
                    }
                    values.append(messaggio)
                
                logger.debug(f"Values to produce: {values}")
                MESSAGES_PENDING.labels(service=SERVICE_NAME, node=NODE_NAME).set(len(values))

                # Calcola il tempo di elaborazione del messaggio
                processing_start_time = time.time()
                # Produce il messaggio su Kafka
                produce_sync(producer, topic2, json.dumps(values))

                MESSAGES_PRODUCED.labels(service=SERVICE_NAME, node=NODE_NAME).inc()

                processing_duration = time.time() - processing_start_time
                PROCESSING_TIME.labels(service=SERVICE_NAME, node=NODE_NAME).observe(processing_duration)


                # Commit dell'offset
                consumer.commit(asynchronous=False)

                logger.debug(f"Committed offset for message: {msg.offset()}")

                values = []  # Resetta la lista dei messaggi
                MESSAGES_PENDING.labels(service=SERVICE_NAME, node=NODE_NAME).set(len(values))

            except Exception as e:
                # Gestisce eventuali eccezioni durante l'elaborazione
                logger.error(f"Errore durante l'elaborazione del messaggio: {e}")
    except KeyboardInterrupt:
        # Permette l'interruzione manuale con Ctrl+C
        logger.info("\nInterruzione manuale ricevuta. Chiudo il consumer.")

    finally:
        # Chiusura pulita del consumer
        consumer.close()
        logger.info("Consumer chiuso correttamente.")



if __name__ == "__main__":
    # Avvia l'HTTP server su una porta specifica
    start_http_server(port=50054)
    logger.info("Prometheus metrics server started on port 50054")

    run()


