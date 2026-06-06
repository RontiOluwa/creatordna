# API Gateway

The API Gateway is the public-facing entry point into CreatorDNA.

## Responsibilities

- Authentication
- Creator onboarding
- Profile management
- Idea delivery access
- Internal service orchestration

---

## Authentication

### Endpoints

```http
POST /auth/register
POST /auth/login
GET /auth/me
```

### Features

- Password hashing
- JWT authentication
- Session validation

---

## Creator Onboarding

### Endpoint

```http
POST /creators/onboard
```

Builds creator DNA profiles using submitted content samples.

---

## Idea Access

### Endpoints

```http
POST /ideas/deliver/me
GET /ideas/stats/me
```

Acts as a proxy to the Delivery Service.

---

## Security

- JWT authentication
- Internal service secrets
- Request validation
- Ownership verification

---

## Startup

```bash
uvicorn main:app --reload --port 8000
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
- Delivery Service
