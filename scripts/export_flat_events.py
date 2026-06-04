"""
Export Events to Flat JSONL

This script maps the internal nested `StoreEvent` schema (used by Kafka and the API)
back into the flat JSONL format required by the HackerEarth evaluation harness.

Usage:
    python scripts/export_flat_events.py --input raw_nested_events.jsonl --output events.jsonl
"""

import argparse
import json
import sys

def map_to_flat_schema(store_event: dict) -> dict:
    """Map a nested StoreEvent back to the HackerEarth flat schema."""
    event_type = store_event.get("event_type", "")
    metadata = store_event.get("metadata", {})
    
    # Common demographics (mocked if not present)
    demographics = {
        "gender_pred": metadata.get("gender_pred", "F"),
        "age_pred": metadata.get("age_pred", 28),
        "age_bucket": metadata.get("age_bucket", "25-34"),
        "is_face_hidden": metadata.get("is_face_hidden", False),
    }

    if event_type == "VISITOR_ENTER":
        return {
            "event_type": "entry",
            "id_token": store_event.get("visitor_id"),
            "store_code": store_event.get("store_id", "").replace("ST", "store_"),
            "camera_id": store_event.get("camera_id"),
            "event_timestamp": store_event.get("timestamp"),
            "is_staff": metadata.get("is_staff", False),
            "group_id": metadata.get("group_id", None),
            "group_size": metadata.get("group_size", None),
            **demographics
        }
    
    elif event_type == "VISITOR_EXIT":
        return {
            "event_type": "exit",
            "id_token": store_event.get("visitor_id"),
            "store_code": store_event.get("store_id", "").replace("ST", "store_"),
            "camera_id": store_event.get("camera_id"),
            "event_timestamp": store_event.get("timestamp"),
            "is_staff": metadata.get("is_staff", False),
            "group_id": metadata.get("group_id", None),
            "group_size": metadata.get("group_size", None),
            **demographics
        }

    elif event_type == "ZONE_ENTER":
        return {
            "event_type": "zone_entered",
            "track_id": metadata.get("track_id", 0),
            "store_id": store_event.get("store_id"),
            "camera_id": store_event.get("camera_id"),
            "zone_id": store_event.get("zone_id"),
            "zone_name": metadata.get("zone_name", "Unknown Zone"),
            "zone_type": metadata.get("zone_type", "SHELF"),
            "is_revenue_zone": metadata.get("is_revenue_zone", "Yes"),
            "event_time": store_event.get("timestamp"),
            "zone_hotspot_x": metadata.get("bbox", {}).get("x1", 0.0),
            "zone_hotspot_y": metadata.get("bbox", {}).get("y1", 0.0),
            "gender": demographics["gender_pred"],
            "age": demographics["age_pred"],
            "age_bucket": demographics["age_bucket"]
        }

    elif event_type == "ZONE_EXIT":
        return {
            "event_type": "zone_exited",
            "track_id": metadata.get("track_id", 0),
            "store_id": store_event.get("store_id"),
            "camera_id": store_event.get("camera_id"),
            "zone_id": store_event.get("zone_id", metadata.get("from_zone")),
            "zone_name": metadata.get("zone_name", "Unknown Zone"),
            "zone_type": metadata.get("zone_type", "SHELF"),
            "is_revenue_zone": metadata.get("is_revenue_zone", "Yes"),
            "event_time": store_event.get("timestamp"),
            "zone_hotspot_x": metadata.get("bbox", {}).get("x1", 0.0),
            "zone_hotspot_y": metadata.get("bbox", {}).get("y1", 0.0),
            "gender": demographics["gender_pred"],
            "age": demographics["age_pred"],
            "age_bucket": demographics["age_bucket"]
        }

    elif event_type == "QUEUE_JOIN":
        # Note: The flat schema uses queue_completed / queue_abandoned for queue events
        # We'll skip raw queue joins since they are merged into completions in the flat schema
        return None

    elif event_type in ("QUEUE_LEAVE", "QUEUE_ABANDON"):
        abandoned = event_type == "QUEUE_ABANDON"
        return {
            "queue_event_id": store_event.get("event_id"),
            "event_type": "queue_abandoned" if abandoned else "queue_completed",
            "track_id": metadata.get("track_id", 0),
            "store_id": store_event.get("store_id"),
            "camera_id": store_event.get("camera_id"),
            "zone_id": store_event.get("zone_id"),
            "zone_name": metadata.get("zone_name", "Billing Queue"),
            "zone_type": "BILLING",
            "is_revenue_zone": "Yes",
            "queue_join_ts": metadata.get("queue_join_ts", store_event.get("timestamp")),
            "queue_served_ts": None if abandoned else store_event.get("timestamp"),
            "queue_exit_ts": store_event.get("timestamp"),
            "wait_seconds": metadata.get("wait_seconds", 0),
            "queue_position_at_join": metadata.get("queue_position_at_join", 0),
            "abandoned": abandoned,
            "zone_hotspot_x": metadata.get("bbox", {}).get("x1", 0.0),
            "zone_hotspot_y": metadata.get("bbox", {}).get("y1", 0.0),
            "gender": demographics["gender_pred"],
            "age": demographics["age_pred"],
            "age_bucket": demographics["age_bucket"]
        }

    return None

def main():
    parser = argparse.ArgumentParser(description="Map internal StoreEvents to flat Hackerearth schema.")
    parser.add_argument("--input", type=str, required=True, help="Input internal JSONL file")
    parser.add_argument("--output", type=str, required=True, help="Output flat JSONL file")
    args = parser.parse_args()

    processed_count = 0
    try:
        with open(args.input, "r") as infile, open(args.output, "w") as outfile:
            for line in infile:
                if not line.strip():
                    continue
                store_event = json.loads(line)
                flat_event = map_to_flat_schema(store_event)
                if flat_event:
                    outfile.write(json.dumps(flat_event) + "\n")
                    processed_count += 1
        
        print(f"Successfully mapped {processed_count} events to {args.output}")

    except Exception as e:
        print(f"Error mapping events: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
