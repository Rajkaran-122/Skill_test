import asyncio
import uuid
import random
from datetime import datetime, timedelta
import sys
import os

# Add parent dir to path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import async_session_maker
from src.db.models import VisitorEventDB, StoreSessionDB, AnomalyDB
from sqlalchemy import text

STORE_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890" # STORE001
ZONES = ["ENTRANCE", "SKINCARE", "ELECTRONICS", "GROCERIES", "CHECKOUT", "EXIT"]
CAMERAS = ["CAM01", "CAM02", "CAM03", "CAM04", "CAM05"]

async def seed_data():
    async with async_session_maker() as session:
        print("Generating mock data for STORE001...")
        
        # Clear existing
        await session.execute(text("TRUNCATE TABLE visitor_events RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE store_sessions RESTART IDENTITY CASCADE"))
        await session.execute(text("TRUNCATE TABLE anomalies RESTART IDENTITY CASCADE"))
        
        now = datetime.now()
        
        # 1. Generate Store Sessions
        sessions_to_add = []
        events_to_add = []
        
        for i in range(120): # 120 visitors today
            visitor_id = str(uuid.uuid4())
            entry_offset = random.randint(1, 10 * 60) # mins ago
            entry_time = now - timedelta(minutes=entry_offset)
            dwell = random.randint(5, 45)
            exit_time = entry_time + timedelta(minutes=dwell)
            converted = random.random() < 0.35 # ~35% conversion

            # Add Session
            s = StoreSessionDB(
                visitor_id=visitor_id,
                store_id=STORE_ID,
                entry_time=entry_time,
                exit_time=exit_time,
                converted=converted
            )
            sessions_to_add.append(s)

            # Add Events for this visitor
            # Entry
            events_to_add.append(VisitorEventDB(
                event_id=str(uuid.uuid4()),
                store_id=STORE_ID,
                camera_id="CAM01",
                visitor_id=visitor_id,
                event_type="ENTRY",
                zone_id="ENTRANCE",
                timestamp=entry_time,
                confidence=0.95
            ))
            
            # Random Zones
            zones_visited = random.sample(["SKINCARE", "ELECTRONICS", "GROCERIES"], k=random.randint(1, 3))
            for z in zones_visited:
                events_to_add.append(VisitorEventDB(
                    event_id=str(uuid.uuid4()),
                    store_id=STORE_ID,
                    camera_id=random.choice(CAMERAS),
                    visitor_id=visitor_id,
                    event_type="ZONE_ENTER",
                    zone_id=z,
                    timestamp=entry_time + timedelta(minutes=random.randint(1, dwell-2)),
                    confidence=0.9
                ))

            # Checkout if converted
            if converted:
                events_to_add.append(VisitorEventDB(
                    event_id=str(uuid.uuid4()),
                    store_id=STORE_ID,
                    camera_id="CAM04",
                    visitor_id=visitor_id,
                    event_type="CHECKOUT",
                    zone_id="CHECKOUT",
                    timestamp=exit_time - timedelta(minutes=2),
                    confidence=0.98
                ))

        session.add_all(sessions_to_add)
        session.add_all(events_to_add)

        # 2. Generate Anomalies
        anomalies = [
            AnomalyDB(
                store_id=STORE_ID,
                anomaly_type="QUEUE_SPIKE",
                severity="HIGH",
                description="Queue depth exceeded threshold",
                timestamp=now - timedelta(minutes=15),
                metric_value=12.0,
                threshold=10.0,
                resolved=False
            ),
            AnomalyDB(
                store_id=STORE_ID,
                anomaly_type="DEAD_ZONE",
                severity="MEDIUM",
                description="No traffic in Groceries for 45 min",
                timestamp=now - timedelta(minutes=45),
                metric_value=0.0,
                threshold=1.0,
                resolved=False
            )
        ]
        session.add_all(anomalies)

        await session.commit()
        print(f"Successfully inserted {len(sessions_to_add)} sessions, {len(events_to_add)} events, and {len(anomalies)} anomalies!")

if __name__ == "__main__":
    asyncio.run(seed_data())
