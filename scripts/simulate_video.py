"""
Event Simulation Script.

Generates synthetic store events for development and testing
without requiring a real CCTV feed or the CV pipeline.

Usage:
    python scripts/simulate_video.py --events 1000 --store STORE001
"""

import argparse
import asyncio
import json
import random
import time
from datetime import datetime, timezone
from uuid import uuid4


ZONES = ["ENTRANCE", "SKINCARE", "ELECTRONICS", "GROCERIES", "CHECKOUT", "EXIT"]
CAMERAS = ["CAM01", "CAM02", "CAM03", "CAM04", "CAM05"]
EVENT_TYPES = [
    "VISITOR_ENTER", "VISITOR_EXIT", "ZONE_ENTER", "ZONE_EXIT",
    "QUEUE_JOIN", "QUEUE_LEAVE", "QUEUE_ABANDON",
]


def generate_event(store_id: str, visitor_pool: list[str]) -> dict:
    """Generate a single random event."""
    event_type = random.choice(EVENT_TYPES)
    visitor_id = random.choice(visitor_pool)

    event = {
        "event_id": str(uuid4()),
        "store_id": store_id,
        "camera_id": random.choice(CAMERAS),
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "confidence": round(random.uniform(0.7, 0.99), 3),
        "metadata": {},
    }

    if event_type in ("ZONE_ENTER", "ZONE_EXIT"):
        event["zone_id"] = random.choice(ZONES)

    if event_type in ("QUEUE_JOIN", "QUEUE_LEAVE", "QUEUE_ABANDON"):
        event["zone_id"] = "CHECKOUT"

    if event_type == "QUEUE_ABANDON":
        event["metadata"]["wait_seconds"] = round(random.uniform(30, 300), 1)

    return event


async def simulate(store_id: str, num_events: int, kafka_url: str | None = None):
    """Run the simulation."""
    print(f"\n{'='*60}")
    print(f"  SIP Event Simulator")
    print(f"  Store: {store_id}")
    print(f"  Events: {num_events}")
    print(f"  Target: {'Kafka' if kafka_url else 'stdout'}")
    print(f"{'='*60}\n")

    # Create a pool of visitor IDs
    num_visitors = max(10, num_events // 10)
    visitor_pool = [f"VIS_{i:06d}" for i in range(1, num_visitors + 1)]

    producer = None
    if kafka_url:
        from aiokafka import AIOKafkaProducer
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_url,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8"),
        )
        await producer.start()

    topic_map = {
        "VISITOR_ENTER": "visitor-events",
        "VISITOR_EXIT": "visitor-events",
        "ZONE_ENTER": "zone-events",
        "ZONE_EXIT": "zone-events",
        "QUEUE_JOIN": "queue-events",
        "QUEUE_LEAVE": "queue-events",
        "QUEUE_ABANDON": "queue-events",
    }

    start = time.time()
    for i in range(num_events):
        event = generate_event(store_id, visitor_pool)

        if producer:
            topic = topic_map.get(event["event_type"], "visitor-events")
            await producer.send(topic, key=store_id, value=event)
        else:
            print(json.dumps(event, indent=2))

        if (i + 1) % 100 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed
            print(f"  [{i+1}/{num_events}] {rate:.0f} events/sec")

        # Simulate real-time pacing
        await asyncio.sleep(random.uniform(0.001, 0.01))

    elapsed = time.time() - start
    print(f"\n  ✓ Complete: {num_events} events in {elapsed:.1f}s ({num_events/elapsed:.0f} events/sec)")

    if producer:
        await producer.stop()


def main():
    parser = argparse.ArgumentParser(description="SIP Event Simulator")
    parser.add_argument("--events", type=int, default=100, help="Number of events to generate")
    parser.add_argument("--store", type=str, default="STORE001", help="Store ID")
    parser.add_argument("--kafka", type=str, default=None, help="Kafka bootstrap servers (e.g., localhost:9094)")
    args = parser.parse_args()

    asyncio.run(simulate(args.store, args.events, args.kafka))


if __name__ == "__main__":
    main()
