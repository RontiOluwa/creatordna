# Ingestion Service

The Ingestion Service discovers trending content and publishes ingestion events.

---

## Responsibilities

- Trend discovery
- Video scraping
- Metadata collection
- Event publishing
- Scheduled ingestion jobs

---

## Workflow

```text
Discover Videos
      ↓
Validate
      ↓
Store Metadata
      ↓
Publish VideoIngested Event
```

---

## Endpoints

### Trigger Full Scrape

```http
POST /ingest/trigger
```

### Trigger Category Scrape

```http
POST /ingest/trigger/{category}
```

### Status

```http
GET /ingest/status
```

Returns scheduler information.

---

## Scheduler

Runs automated ingestion jobs using APScheduler.

---

## Events Published

```text
VideoIngested
```

---

## Health Check

```http
GET /health
```
