import os
import logging
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from datetime import datetime

# Setup logging - industry standard for observability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mock in-memory "database" for tracking processed messages (replace with real DB in prod)
processed_data = {}

def process_message(message_value):
    """
    Process a JSON message: parse, calculate total, and store result.
    Simulates a real-world data pipeline (e.g., order processing or telemetry).
    """
    try:
        # Assume message is a JSON string (e.g., {"order_id": 123, "items": [{"price": 10.5}, {"price": 20.3}]})
        data = json.loads(message_value)
        
        # Extract relevant fields (e.g., order items)
        items = data.get("items", [])
        if not items:
            raise ValueError("No items found in message")

        # Calculate total price (business logic)
        total_price = sum(item.get("price", 0) for item in items)
        order_id = data.get("order_id", "unknown")

        # Simulate additional processing (e.g., tax calculation - 8% tax)
        tax_rate = 0.08
        tax_amount = total_price * tax_rate
        final_amount = total_price + tax_amount

        # Store result in mock DB with timestamp
        processed_data[order_id] = {
            "total_price": total_price,
            "tax_amount": tax_amount,
            "final_amount": final_amount,
            "processed_at": datetime.utcnow().isoformat()
        }

        logger.info(f"Processed order {order_id}: Total=${total_price:.2f}, Tax=${tax_amount:.2f}, Final=${final_amount:.2f}")
        return True

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e} - Message: {message_value}")
        return False
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return False

def main():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka-cluster-kafka-bootstrap.scaling-demo.svc.cluster.local:9092')
    topic = os.getenv('KAFKA_TOPIC', 'test-topic')
    group_id = os.getenv('KAFKA_GROUP_ID', 'keda-consumer-group')

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: x.decode('utf-8'),
        max_poll_records=100,  # Batch processing for efficiency
        session_timeout_ms=30000,
        heartbeat_interval_ms=10000
    )

    logger.info(f"Starting consumer for topic: {topic} at {datetime.utcnow().isoformat()}")

    try:
        for message in consumer:
            logger.info(f"Received message: {message.value} (partition: {message.partition}, offset: {message.offset})")
            success = process_message(message.value)
            if success:
                consumer.commit()  # Commit offset only on successful processing
            # Add a small delay to simulate workload (adjustable)
            import time; time.sleep(0.1)

    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        consumer.close()
        logger.info("Consumer shutdown. Processed data summary: %s", processed_data)

if __name__ == "__main__":
    main()
