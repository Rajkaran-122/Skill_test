# Store Intelligence Platform (SIP) — Architecture & DFD

This document outlines the formal system architecture, data flows, and component specifications for the Store Intelligence Platform. All diagrams have been styled in a clean, high-contrast monochrome (black and white) aesthetic for professional documentation purposes.

---

## 1. Context Data Flow Diagram (Level 0)

The Level 0 Context DFD illustrates how the SIP interacts with external entities. It abstracts the entire system into a single process node to show the boundary of the platform.

```mermaid
graph LR
    classDef default fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef external fill:#f3f3f3,stroke:#000000,stroke-width:2px,color:#000000;
    
    CCTV["CCTV Cameras (Store)"]:::external
    MANAGER["Store Manager / User"]:::external
    SIP(("Store Intelligence<br/>Platform (SIP)"))

    CCTV -->|Raw Video Streams| SIP
    SIP -->|Real-time Metrics, Alerts| MANAGER
```

> [!NOTE]
> The dashed borders indicate external entities outside the direct processing control of the platform.

---

## 2. Detailed Data Flow Diagram (Level 1)

The Level 1 DFD breaks down the SIP process into its major logical subsystems, illustrating how data is transformed from raw pixels into business intelligence.

```mermaid
graph TD
    classDef default fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef datastore fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef external fill:#f3f3f3,stroke:#000000,stroke-width:2px,color:#000000;

    CCTV["CCTV Cameras"]:::external
    MANAGER["Store Manager"]:::external

    P1("1.0 Computer Vision<br/>Pipeline")
    P2("2.0 Event Bus<br/>(Kafka)")
    P3("3.0 Event<br/>Processor")
    P4("4.0 API<br/>Platform")
    
    D1[("D1: TimescaleDB<br/>(Historical)")]:::datastore
    D2[("D2: Redis<br/>(Hot Metrics)")]:::datastore

    CCTV -->|Video Frames| P1
    P1 -->|Detection/Tracking| P2
    P2 -->|Raw CV Events| P3
    
    P3 -->|Persist Sessions| D1
    P3 -->|Update Live KPIs| D2
    
    P3 -.->|Pub/Sub Alerts| P4
    D1 -->|Query Aggregates| P4
    D2 -->|Fetch Hot Cache| P4
    
    P4 <-->|REST / WebSocket| UI("5.0 React Dashboard")
    UI -->|Rendered Insights| MANAGER
```

---

## 3. System Architecture Diagram

This structural architecture diagram maps the physical/deployment topology of the microservices, messaging layers, and data stores.

```mermaid
graph TD
    classDef default fill:#ffffff,stroke:#000000,stroke-width:2px,color:#000000;
    classDef layer fill:#fcfcfc,stroke:#000000,stroke-width:1px,color:#000000;
    
    subgraph Edge["Edge Processing Layer (Store)"]
        direction LR
        CAM["IP Cameras"] --> CV["CV Pipeline Service<br/>(YOLO11 / ByteTrack / OSNet)"]
    end
    class Edge layer

    subgraph Messaging["Messaging Layer"]
        KAFKA["Apache Kafka (KRaft Mode)<br/>Topics: visitor-events, zone-events..."]
    end
    class Messaging layer

    subgraph Processing["Data Processing Layer"]
        EP["Event Processor Service"]
        SE["Session Builder"]
        ME["Metrics Engine"]
        QE["Queue Engine"]
        AE["Anomaly Engine"]
        
        EP --- SE
        EP --- ME
        EP --- QE
        EP --- AE
    end
    class Processing layer

    subgraph Storage["Persistence Layer"]
        direction LR
        TS[("PostgreSQL 17<br/>+ TimescaleDB")]
        RD[("Redis 7.4<br/>(Cache & Pub/Sub)")]
    end
    class Storage layer

    subgraph Serving["Serving & UI Layer"]
        API["FastAPI Service<br/>(REST + WebSockets)"]
        DASH["React 19 Dashboard<br/>(Vite + Tailwind)"]
    end
    class Serving layer

    %% Connections
    CV -->|Publish Events| KAFKA
    KAFKA -->|Consume Batch| EP
    
    EP -->|SQL Insert| TS
    EP -->|SET / PUBLISH| RD
    
    TS -->|SQL Select| API
    RD -->|GET / SUBSCRIBE| API
    
    API <-->|HTTP / WS| DASH
```

---

## 4. Component Specifications

### 4.1 Edge Processing (Computer Vision)
- **Responsibility**: Ingests RTSP streams at 20+ FPS, runs inference, and abstracts pixels into logical events.
- **Key Algorithms**:
  - **Detector**: YOLO11 (Object Detection) isolating `class 0` (person).
  - **Tracker**: ByteTrack (Multi-Object Tracking) for frame-to-frame persistence.
  - **Re-ID**: OSNet (Appearance Features) extracting 512-D vectors for cross-camera re-identification.
  - **Zones**: Ray-casting point-in-polygon logic for geographical boundary detection.

### 4.2 Messaging Layer (Kafka KRaft)
- **Responsibility**: Decouples the GPU-heavy edge devices from the analytical backend, buffering spikes in store traffic.
- **Topics**: `visitor-events`, `zone-events`, `queue-events`, `conversion-events`, `dashboard-events`.

### 4.3 Analytics Engines (Event Processor)
- **Responsibility**: Consumes raw Kafka streams concurrently and applies stateful transformations.
- **Sub-Engines**:
  - **Session Builder**: Tracks a single visitor's journey (Entry -> Skincare -> Checkout -> Exit) into a unified timeline.
  - **Metrics Engine**: Computes conversion rates and unique visitor counts in real time.
  - **Queue Engine**: Uses spatial clustering (DBSCAN principles) to identify queue depths and wait times.
  - **Anomaly Engine**: Statistical rolling window (Standard Deviation) to detect 3σ spikes in queue depths or dead zones.

### 4.4 Data Persistence
- **TimescaleDB**: Optimizes PostgreSQL for time-series data. Stores raw historical logs and finalized visitor sessions. Uses Continuous Aggregates for hourly/daily rollups.
- **Redis**: Stores volatile, high-read-frequency data (current KPI numbers, active anomalies) and acts as the Pub/Sub broker for horizontal WebSocket scaling.

### 4.5 API & Presentation
- **FastAPI**: Asynchronous Python backend. Uses `asyncpg` for non-blocking DB queries and exposes a WebSocket Manager that subscribes to Redis to fan-out live updates.
- **React Dashboard**: Modern SPA. Connects to the WebSocket feed to trigger count-up animations, redraw Recharts area/line graphs, and push alert notifications without polling.

---

> [!TIP]
> This architecture is designed for **horizontal scalability**. If processing load increases (e.g., adding more stores), you can independently scale the CV Pipeline instances (Edge) and Event Processor instances (Cloud), relying on Kafka's consumer groups to balance the event load automatically.
