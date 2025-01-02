from datetime import datetime
from confluent_kafka import Consumer, Producer, KafkaException
import json
import CQRS_Pattern.lecture_db as lecture_db
import logging
import os

# Configurazione del logging
logging.basicConfig(
    level=logging.DEBUG,  # Puoi modificare il livello secondo necessità
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Kafka configuration for consumer and producer
consumer_config = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:29092'),
    'group.id': 'group1',  # Cambia il group.id per differenziare i consumatori se necessario
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest',  # Parte dal primo messaggio se non c'è offset salvato
}

producer_config = {
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:29092'),  # Usa lo stesso broker
    'acks': 'all',  # Ensure all in-sync replicas acknowledge the message
    'max.in.flight.requests.per.connection': 1,  # Ensure ordering of messages
    'retries': 3  # Number of retries for failed messages
}


values = []


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

            # Esegue la query per ottenere i valori da notificare
            read_service = lecture_db.ReadService()

            results = read_service.NotifierValues()
            
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

            # Produce il messaggio su Kafka
            produce_sync(producer, topic2, json.dumps(values))

            # Commit dell'offset
            consumer.commit(asynchronous=False)
            logger.debug(f"Committed offset for message: {msg.offset()}")

            values = []  # Resetta la lista dei messaggi

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


