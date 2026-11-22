"""
Dummy Message Publisher
Generates and publishes sample messages to Pub/Sub
"""

import json
import time
import random
from datetime import datetime
from google.cloud import pubsub_v1
import os

# Configuration
PROJECT_ID = os.environ.get('GCP_PROJECT', 'your-project-id')
TOPIC_NAME = os.environ.get('PUBSUB_TOPIC', 'data-ingestion-topic')

# Initialize publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

# Dummy data generators
USER_IDS = ['user001', 'user002', 'user003', 'user004', 'user005']
EVENT_TYPES = ['page_view', 'button_click', 'form_submit', 'purchase', 'logout']


def generate_dummy_message():
    """Generate a random dummy message"""
    return {
        'user_id': random.choice(USER_IDS),
        'event_type': random.choice(EVENT_TYPES),
        'value': round(random.uniform(0, 100), 2),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def publish_message(message_data):
    """Publish a message to Pub/Sub"""
    try:
        # Convert to JSON bytes
        message_bytes = json.dumps(message_data).encode('utf-8')

        # Publish
        future = publisher.publish(topic_path, message_bytes)
        message_id = future.result()

        print(f"✓ Published message {message_id}: {message_data}")
        return message_id

    except Exception as e:
        print(f"✗ Error publishing message: {e}")
        return None


def main():
    """Main execution - publish dummy messages"""
    print(f"Starting message publisher...")
    print(f"Project: {PROJECT_ID}")
    print(f"Topic: {TOPIC_NAME}")
    print("-" * 60)

    # Get number of messages from environment or default to 10
    num_messages = int(os.environ.get('NUM_MESSAGES', '10'))
    delay = float(os.environ.get('DELAY_SECONDS', '1'))

    for i in range(num_messages):
        message = generate_dummy_message()
        publish_message(message)

        if i < num_messages - 1:  # Don't sleep after last message
            time.sleep(delay)

    print("-" * 60)
    print(f"✓ Published {num_messages} messages successfully!")


if __name__ == '__main__':
    main()
