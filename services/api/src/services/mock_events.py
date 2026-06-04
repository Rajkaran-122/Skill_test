import asyncio
import json
import random
import structlog
from datetime import datetime, timezone
from sqlalchemy import select

logger = structlog.get_logger(__name__)

async def simulate_mock_events(app):
    """Simulate real-time events for the dashboard across all cameras."""
    logger.info("Starting local mock event simulation loop")
    
    # Import session factory to write to DB during mock loop
    from src.db.session import _session_factory
    from src.db.models import AnomalyDB

    cameras = ['CAM01', 'CAM02', 'CAM03', 'CAM04']
    zones_map = {
        'CAM01': 'Entrance',
        'CAM02': 'Cosmetics Aisle',
        'CAM03': 'Fragrance Section',
        'CAM04': 'Checkout Area'
    }
    
    # Track the last alert time to prevent spamming the DB
    last_alert_time = 0

    try:
        while True:
            await asyncio.sleep(2)
            if not app.state.ws_manager:
                continue
                
            store_id = "STORE001"
            
            # 1. Generate dynamic person counts for each camera
            # Set to perfectly match the static MP4 CCTV footage frames
            person_counts = {
                'CAM01': 2,
                'CAM02': 5,
                'CAM03': 3,
                'CAM04': 0
            }

            # Force CAM02 or CAM04 to sometimes spike for demonstration of Insights Engine
            # (We will artificially inflate CAM02 occasionally to trigger the crowding alert)
            if random.random() > 0.8:
                person_counts['CAM02'] = random.randint(9, 15)

            # 2. Check for Insights / Anomalies to write to DB
            current_time = asyncio.get_event_loop().time()
            if current_time - last_alert_time > 15:  # At most 1 alert every 15s
                new_anomaly = None
                
                if person_counts['CAM02'] > 8:
                    new_anomaly = AnomalyDB(
                        store_id=store_id,
                        anomaly_type="CROWDING_DETECTED",
                        severity="HIGH",
                        description="High crowding in Cosmetics Aisle. High conversion potential. Dispatch assistance.",
                        metric_value=person_counts['CAM02'],
                        threshold=8.0
                    )
                elif person_counts['CAM04'] > 5:
                    new_anomaly = AnomalyDB(
                        store_id=store_id,
                        anomaly_type="QUEUE_SPIKE",
                        severity="CRITICAL",
                        description="Queue depth exceeding acceptable limits at Checkout. Open an additional register.",
                        metric_value=person_counts['CAM04'],
                        threshold=5.0
                    )
                
                if new_anomaly and _session_factory:
                    try:
                        async with _session_factory() as db:
                            # Avoid duplicates by checking if similar unresolved exists
                            query = select(AnomalyDB).where(
                                AnomalyDB.store_id == store_id, 
                                AnomalyDB.anomaly_type == new_anomaly.anomaly_type,
                                AnomalyDB.resolved == False
                            )
                            existing = (await db.execute(query)).scalar_one_or_none()
                            if not existing:
                                db.add(new_anomaly)
                                await db.commit()
                                logger.info(f"Mock Anomaly Generated: {new_anomaly.anomaly_type}")
                                last_alert_time = current_time
                    except Exception as e:
                        logger.error(f"Failed to write mock anomaly: {e}")

            # 3. Generate the event stream batch
            events = []
            num_events = random.randint(1, 4)
            for _ in range(num_events):
                cam = random.choice(cameras)
                events.append({
                    "event_id": f"evt_{random.randint(1000,9999)}",
                    "event_type": random.choice(["VISITOR_ENTER", "VISITOR_EXIT", "ZONE_DWELL", "PRODUCT_ENGAGE"]),
                    "camera_id": cam,
                    "zone_id": zones_map[cam],
                    "confidence": round(random.uniform(0.85, 0.99), 2)
                })

            # Broadcast the batch
            payload = {
                "type": "EVENTS_BATCH",
                "store_id": store_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "person_counts": person_counts,
                "events": events
            }
            
            await app.state.ws_manager.broadcast_local(store_id, json.dumps(payload))
            
    except asyncio.CancelledError:
        logger.info("Mock event simulation loop stopped")
