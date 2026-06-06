# Delivery Service

The Delivery Service generates personalized content ideas for creators.

---

## Responsibilities

- Creator matching
- Idea generation
- Daily delivery scheduling
- Delivery analytics

---

## Workflow

```text
Creator DNA
       +
Content Patterns
       ↓
Matching Engine
       ↓
Idea Generator
       ↓
Daily Delivery
```

---

## Components

### Matcher

Matches creators with relevant content opportunities.

### Generator

Produces personalized content ideas.

### Scheduler

Controls delivery frequency and timing.

---

## Endpoints

### Deliver Ideas

```http
POST /ideas/deliver/{creator}
```

### Stats

```http
GET /ideas/stats/{creator}
```

---

## Health Check

```http
GET /health
```

---

## Dependencies

- PostgreSQL
- RabbitMQ
