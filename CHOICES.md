# Architectural and Technical Choices

Below are three critical architectural decisions made during the design of the Store Intelligence Platform, detailing the options considered, AI consultations, and the final rationale.

---

## 1. Detection Model Selection

**Options Considered:**
- **YOLO11 + ByteTrack**: A modern, extremely fast object detection network paired with a robust bounding-box intersection (IOU) tracker.
- **RT-DETR + DeepSORT**: A transformer-based detector paired with a heavy appearance-based tracker.

**What AI Suggested:**
When I asked Claude 3.5 Sonnet to evaluate the tradeoffs for a retail environment with heavy partial occlusions (e.g., billing queues), the AI strongly recommended YOLO11 combined with ByteTrack. It pointed out that ByteTrack keeps low-confidence detection boxes and associates them via tracklets, which gracefully handles customers temporarily obscured by shelves or other people, whereas DeepSORT would likely fragment their IDs.

**What I Chose and Why:**
I chose **YOLO11 + ByteTrack**. I agreed with the AI's assessment regarding partial occlusions. Retail environments require high frame-rate processing for multi-camera feeds. YOLO11 offers the speed needed for real-time edge processing, and ByteTrack provides resilience without the high computational overhead of extracting embeddings on every single frame.

---

## 2. Event Schema Design Rationale

**Options Considered:**
- **Flat JSON Schema**: A simple schema where every possible event attribute (e.g., `queue_depth`, `sku_zone`) exists at the root level.
- **Nested Metadata Schema**: Core routing and identification attributes at the root, with context-specific data pushed into a nested `metadata` object.

**What AI Suggested:**
I consulted ChatGPT (GPT-4o) on how to design a schema that supports diverse event types (entries, queue joins, zone dwells) without requiring constant database schema migrations. The AI suggested the **Nested Metadata Schema**. It advised that storing the `metadata` object as a `JSONB` column in PostgreSQL/TimescaleDB would allow for flexible, schema-less indexing of edge-case metrics (like `queue_depth`) while keeping the core schema strongly typed.

**What I Chose and Why:**
I chose the **Nested Metadata Schema** and implemented it in the Pydantic models. By keeping `event_id`, `timestamp`, and `visitor_id` at the root, the API can quickly validate and deduplicate incoming events. Pushing flexible data into the `metadata` block means the detection pipeline can evolve to send new attributes (like `group_size`) without breaking the API ingestion contract.

---

## 3. API Architecture Choice (Streaming vs HTTP)

**Options Considered:**
- **Direct Database Inserts**: The FastAPI `/events/ingest` endpoint parses the payload and writes directly to PostgreSQL.
- **Kafka Event Streaming**: The FastAPI endpoint validates the payload, but immediately offloads it to a Kafka topic for asynchronous processing.

**What AI Suggested:**
I asked an LLM to review the architecture for scaling to 40 stores sending high-frequency dwell events. The AI pointed out that direct database inserts would bottleneck the API and cause 503 errors during traffic spikes (like a Black Friday event). It strongly recommended introducing an event broker like **Apache Kafka** to decouple ingestion from persistence.

**What I Chose and Why:**
I chose to use **Kafka (KRaft Mode)** for the ingestion layer. While I initially thought Kafka might be overkill for a single-store demo, I agreed with the AI that building for production scale requires asynchronous processing. The API now merely validates schema and idempotency, returning a 200 OK instantly, while the backend `Event Processor` service consumes the Kafka topic and handles the heavy SQL aggregations in TimescaleDB at its own pace.
