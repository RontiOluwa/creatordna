# Analysis Service

The Analysis Service converts raw content into reusable intelligence.

---

## Responsibilities

- Consume ingestion events
- Analyze content
- Extract content angles
- Identify patterns
- Store insights

---

## Workflow

```text
VideoIngested Event
          ↓
Content Extraction
          ↓
Pattern Detection
          ↓
Angle Generation
          ↓
Database Storage
```

---

## Event Consumption

Consumes:

```text
VideoIngested
```

---

## Features

### Hook Analysis

Identifies successful opening structures.

### Angle Extraction

Determines the central message or content perspective.

### Pattern Recognition

Finds recurring viral characteristics.

---

## Endpoints

```http
GET /angles
```

Retrieve generated content angles.

---

## Health Check

```http
GET /health
```

---

## Dependencies

- PostgreSQL
- RabbitMQ
