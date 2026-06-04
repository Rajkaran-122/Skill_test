# Scaling Strategy & Failure Handling

The Store Intelligence Platform (SIP) is designed to scale horizontally to support thousands of physical retail locations while maintaining high availability and real-time dashboard latency.

---

## Part 1: Scaling Strategy

How the architecture evolves as the business scales:

### 40 Stores (MVP Stage)
* **Edge:** Single GPU (e.g., RTX 3060) per store running the CV Pipeline.
* **Cloud:** Monolithic `docker-compose` on a single strong EC2 instance (FastAPI, Redis, Postgres, Kafka).
* **Bottleneck:** Database write-throughput and Kafka I/O on a single EBS volume.

### 400 Stores (Growth Stage)
* **Edge:** Nvidia Jetson Orin Nano clusters at the edge.
* **Cloud:** Transition to **Kubernetes (EKS/GKE)**. 
  * Kafka deployed via Strimzi Operator across 3 brokers.
  * TimescaleDB configured with multiple disks for WAL and Data.
  * FastAPI scaled to 5-10 pods behind an Ingress Controller.
* **Bottleneck:** The Event Processor struggling to consume messages fast enough.

### 4,000+ Stores (Enterprise Stage)
* **Messaging:** Kafka partitioned by `store_id` (e.g., 100 partitions). 
* **Processing:** The Event Processor, Session Builder, and Metrics Engine are split into isolated Kubernetes Deployments, each autoscaling based on Kafka consumer lag (KEDA).
* **Database:** TimescaleDB scaled using a Multi-Node architecture (distributed hypertables) to parallelize queries across compute nodes.
* **Cache:** Redis Cluster mode enabled to handle millions of real-time KPI reads/writes per second.

---

## Part 2: Failure Handling & Resilience

A production system assumes failure is inevitable. Here is how SIP handles node degradation:

### 1. Camera Disconnects / Network Loss
**Scenario:** A store loses internet connection for 2 hours.
**Handling:** The Edge CV Pipeline continues processing video and buffers the JSON events locally to a lightweight SQLite/Redis queue. Once internet is restored, it bulk-publishes the historical events to Kafka with their original timestamps.

### 2. Kafka Cluster Down
**Scenario:** The central Kafka brokers crash.
**Handling:** Edge nodes backoff exponentially. Backend systems lose incoming data streams but the **React Dashboard remains online**, serving historical data from TimescaleDB and the last-known state from Redis.

### 3. Redis Cache Failure
**Scenario:** Redis goes out of memory or crashes.
**Handling:** FastAPI catches the Redis connection timeout. It instantly degrades gracefully by routing `GET /metrics` requests directly to TimescaleDB to calculate KPIs on the fly. Real-time WebSocket alerts temporarily pause until Redis restarts.

### 4. Database (TimescaleDB) Outage
**Scenario:** Primary Postgres node fails.
**Handling:** Patroni/PgBouncer automatically promotes the hot-standby replica to Primary. During the 10-second failover window, the Event Processor catches the SQL `ConnectionRefused` errors and pauses Kafka consumption, ensuring zero events are dropped.

### 5. Anomaly Engine Overload
**Scenario:** Black Friday traffic causes 100x event spikes, delaying anomaly detection.
**Handling:** The Anomaly Engine consumers are decoupled from the Metrics Engine consumers. If anomalies fall behind, live KPIs (visitors, conversion) continue to update instantly while anomalies process with slightly higher latency.
