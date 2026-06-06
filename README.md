# CreatorDNA

CreatorDNA is an AI-powered content intelligence platform that helps creators consistently generate high-performing content ideas tailored to their unique content style.

The platform analyzes viral content across multiple niches, extracts successful content patterns, builds creator-specific DNA profiles, and generates personalized content opportunities every day.

---

## Architecture

```text
                    ┌─────────────────┐
                    │   Frontend UI   │
                    │    Next.js      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   API Gateway   │
                    │     FastAPI     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼

┌────────────────┐  RabbitMQ Events  ┌────────────────┐
│ Ingestion      │ ───────────────▶ │ Analysis       │
│ Service        │                  │ Service        │
└────────────────┘                  └────────────────┘
                                             │
                                             ▼
                                   ┌────────────────┐
                                   │ Delivery       │
                                   │ Service        │
                                   └────────────────┘
                                             │
                                             ▼
                                      Personalized
                                      Content Ideas

Shared Infrastructure:
- PostgreSQL
- RabbitMQ
- Redis
```

## Core Workflow

### 1. Content Ingestion

The ingestion service continuously discovers trending content across selected niches and stores metadata for analysis.

### 2. Content Analysis

The analysis service processes newly ingested content and extracts:

- Hooks
- Angles
- Story structures
- Content themes
- Audience signals

### 3. Creator DNA Profiling

During onboarding, CreatorDNA analyzes a creator's existing content and builds a personalized profile including:

- Primary niche
- Secondary niches
- Tone of voice
- Hook style
- Audience type
- Content format preferences
- Posting behavior

### 4. Idea Generation

The delivery service matches creator DNA against proven content patterns and generates tailored content opportunities.

---

## Services

| Service           | Purpose                                |
| ----------------- | -------------------------------------- |
| API Gateway       | Authentication, onboarding, public API |
| Ingestion Service | Trend discovery and video collection   |
| Analysis Service  | Content pattern extraction             |
| Delivery Service  | Personalized idea generation           |
| Frontend          | Creator dashboard                      |

---

## Tech Stack

### Backend

- Python
- FastAPI
- PostgreSQL
- RabbitMQ
- Redis
- APScheduler

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Axios

---

## Local Development

### Prerequisites

- Docker
- Docker Compose
- Python 3.11+
- Node.js 20+

### Start Infrastructure

```bash
docker-compose up --build
```

### Service Ports

| Service           | Port  |
| ----------------- | ----- |
| API Gateway       | 8000  |
| Ingestion Service | 8001  |
| Analysis Service  | 8002  |
| Delivery Service  | 8003  |
| PostgreSQL        | 5432  |
| RabbitMQ          | 5672  |
| RabbitMQ UI       | 15672 |
| Frontend          | 3000  |

---

## Environment Variables

```env
DATABASE_URL=
RABBITMQ_URL=
JWT_SECRET=
CLAUDE_API_KEY=
INTERNAL_SERVICE_SECRET=
```

---

## Event Flow

### VideoIngested

Published by:

- Ingestion Service

Consumed by:

- Analysis Service

### ContentPatternCreated

Published by:

- Analysis Service

Consumed by:

- Delivery Service

---

## Repository Structure

```text
frontend/
services/
├── api-gateway/
├── ingestion-service/
├── analysis-service/
└── delivery-service/

shared/
├── database.py
├── rabbitmq/
└── schemas/
```

---

## Future Enhancements

- Multi-platform support
- Trend forecasting
- Team workspaces
- Creator collaboration recommendations
- Performance feedback loop
- A/B tested idea generation

---

## License

Private Project.
