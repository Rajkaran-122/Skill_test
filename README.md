# Store Intelligence Platform (SIP)

> AI-Powered Retail Analytics — Transforming CCTV footage into real-time business intelligence.

![Status](https://img.shields.io/badge/status-in%20development-blue)
![Python](https://img.shields.io/badge/python-3.12+-3776ab)
![React](https://img.shields.io/badge/react-19-61dafb)
![License](https://img.shields.io/badge/license-proprietary-red)

## Architecture

```
CCTV Cameras → YOLO11 Detection → ByteTrack Tracking → OSNet Re-ID
    → Event Generator → Kafka 4.0 (KRaft)
    → Session Builder | Queue Engine | Metrics Engine | Anomaly Engine
    → PostgreSQL + TimescaleDB
    → FastAPI (REST + WebSocket)
    → React Dashboard
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) NVIDIA GPU + nvidia-container-toolkit for CV pipeline

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Services

```bash
# Development mode
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Create Kafka topics
docker compose exec kafka bash /opt/kafka/create-topics.sh
```

### 3. Verify

```bash
# Check service health
curl http://localhost:8000/api/v1/health

# Open dashboard
open http://localhost:3000

# View Grafana
open http://localhost:3001
```

### 4. Simulate Events

```bash
python scripts/simulate_video.py --events 1000 --kafka localhost:9094
```

## Services

| Service | Port | Description |
|:--------|:-----|:------------|
| **API** | 8000 | FastAPI REST + WebSocket |
| **Dashboard** | 3000 | React + TailwindCSS |
| **Grafana** | 3001 | Monitoring dashboards |
| **Prometheus** | 9090 | Metrics collection |
| **PostgreSQL** | 5432 | TimescaleDB (time-series) |
| **Redis** | 6379 | Cache + Pub/Sub |
| **Kafka** | 9092/9094 | Event streaming (KRaft) |

## API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| POST | `/api/v1/events/ingest` | Batch event ingestion |
| GET | `/api/v1/stores/{id}/metrics` | Store KPIs |
| GET | `/api/v1/stores/{id}/funnel` | Conversion funnel |
| GET | `/api/v1/stores/{id}/heatmap` | Zone activity heatmap |
| GET | `/api/v1/stores/{id}/anomalies` | Active anomalies |
| GET | `/api/v1/health` | System health check |
| WS | `/api/v1/ws/dashboard/{id}` | Real-time dashboard stream |

## Technology Stack

| Layer | Technology |
|:------|:-----------|
| Detection | YOLO11 (Ultralytics) |
| Tracking | ByteTrack |
| Re-ID | OSNet (TorchReID) |
| Streaming | Apache Kafka 4.0 (KRaft) |
| Backend | FastAPI (async) |
| Database | PostgreSQL 17 + TimescaleDB |
| Cache | Redis 7.4 |
| Frontend | React 19 + TailwindCSS 4 |
| Monitoring | Prometheus + Grafana |

## North Star Metric

```
Store Conversion Rate = Converted Visitors / Total Unique Visitors
```

## Development

```bash
# Run tests
make test

# Run specific service tests
make test-api
make test-cv

# View logs
make logs

# Database shell
make db-shell
```

## License

Proprietary — All rights reserved.
