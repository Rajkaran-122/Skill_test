"""
Event Simulation Script for the Purplle Tech Challenge.

Reads the raw CCTV pipeline output (`sample_eventsbe42122.jsonl`) 
and streams it to the API endpoint to simulate real-time ingestion.

Usage:
    python scripts/simulate_video.py --file ../problem_statement/sample_eventsbe42122.jsonl
"""

import argparse
import asyncio
import json
import time
import requests
import uuid
import sys

def map_event(raw_event: dict) -> dict:
    """Map raw output to the strictly required nested schema."""
    ts_field = 'event_timestamp'
    if 'event_time' in raw_event:
        ts_field = 'event_time'
    elif 'queue_join_ts' in raw_event:
        ts_field = 'queue_join_ts'

    ts = raw_event.get(ts_field, "2026-03-08T18:10:05.120000")
    if not ts.endswith("Z"):
        ts += "Z" # Ensure UTC format
        
    store_id = raw_event.get("store_code") or raw_event.get("store_id", "ST1076")
    visitor_id = raw_event.get("id_token") or str(raw_event.get("track_id", "Unknown"))
    
    ev_type_map = {
        "entry": "ENTRY",
        "exit": "EXIT",
        "zone_entered": "ZONE_ENTER",
        "zone_exited": "ZONE_EXIT",
        "queue_completed": "BILLING_QUEUE_JOIN", 
        "queue_abandoned": "BILLING_QUEUE_ABANDON"
    }
    event_type = ev_type_map.get(raw_event.get("event_type"), "ZONE_DWELL")

    return {
        "event_id": str(uuid.uuid4()),
        "store_id": store_id.replace("store_", "ST"),
        "camera_id": raw_event.get("camera_id", "CAM_01"),
        "visitor_id": visitor_id,
        "event_type": event_type,
        "timestamp": ts,
        "zone_id": raw_event.get("zone_id"),
        "dwell_ms": raw_event.get("wait_seconds", 0) * 1000 if "wait_seconds" in raw_event else 0,
        "is_staff": raw_event.get("is_staff", False),
        "confidence": 0.95,
        "metadata": {
            "queue_depth": raw_event.get("queue_position_at_join"),
            "sku_zone": raw_event.get("zone_name"),
            "session_seq": 1
        }
    }

async def simulate(file_path: str, target_url: str):
    print(f"Reading events from {file_path}")
    print(f"Streaming to API: {target_url}")
    batch = []
    
    try:
        with open(file_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                raw_event = json.loads(line)
                mapped_event = map_event(raw_event)
                batch.append(mapped_event)
                
                # Stream in batches of 50
                if len(batch) >= 50:
                    await send_batch(batch, target_url)
                    batch = []
                    await asyncio.sleep(0.5)

        if batch:
            await send_batch(batch, target_url)
            
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)

async def send_batch(batch: list, url: str):
    try:
        # We use sync requests here for simplicity in the simulation script
        resp = requests.post(url, json=batch)
        if resp.status_code == 200:
            print(f"Sent batch of {len(batch)} events successfully.")
        else:
            print(f"Failed to send batch: {resp.status_code} - {resp.text}", file=sys.stderr)
    except Exception as e:
        print(f"Connection error: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="SIP Event Simulator")
    parser.add_argument("--file", type=str, required=True, help="Path to sample_events.jsonl")
    parser.add_argument("--url", type=str, default="http://localhost:8000/events/ingest", help="API Ingest URL")
    args = parser.parse_args()

    asyncio.run(simulate(args.file, args.url))

if __name__ == "__main__":
    main()
