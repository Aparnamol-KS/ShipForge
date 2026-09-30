# ShipForge

> A self-hosted CI/CD platform that automates repository builds through GitHub webhooks, Redis-based job processing, Docker-isolated execution, and a React dashboard.

---

## Overview

ShipForge is a mini CI/CD platform built to understand and implement the core components behind modern continuous integration systems.

A GitHub push can trigger a build in ShipForge. The backend validates the webhook, creates a build record, places the build into a Redis queue, and a background worker executes the build inside an isolated Docker environment.

The build progresses through configurable stages:

```text
Install → Test → Build
```

Build status, stages, logs, and lifecycle events are persisted and exposed through the dashboard.

---

## Features

### Project Management

* Create projects
* Configure GitHub repository URLs
* Configure install, test, and build commands
* View project details
* View build history

### Build System

* Manual build triggering
* Automatic builds through GitHub webhooks
* Sequential build numbering
* Build status tracking
* Build stage tracking
* Failed-stage tracking
* Build duration tracking
* Build logs
* Retry failed builds
* Cancel queued or running builds

### GitHub Integration

* GitHub push webhook support
* HMAC SHA-256 webhook signature verification
* Repository-based project matching
* Branch extraction
* Commit SHA tracking
* Push event filtering

Each build runs inside a Docker-based execution environment.

### Queue & Worker

* Redis-backed build queue
* Background worker
* Decoupled API and build execution
* One-time worker mode for development/testing

### Real-Time Events

* WebSocket build updates
* Build status events
* Build stage events
* Dashboard polling for build state

### Dashboard

The React dashboard provides:

* Project overview
* Build history
* Build status
* Build stage
* Build duration
* Build logs
* Retry controls
* Cancellation controls
* Real-time build updates

---

# Architecture

```text
                         ┌──────────────────┐
                         │      GitHub      │
                         └────────┬─────────┘
                                  │
                           Push Webhook
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │       API        │
                         └───────┬──────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
             ┌─────────────┐          ┌─────────────┐
             │ PostgreSQL  │          │    Redis    │
             │             │          │    Queue    │
             └─────────────┘          └──────┬──────┘
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │   Worker    │
                                      └──────┬──────┘
                                             │
                                      Clone Repository
                                             │
                                             ▼
                                      ┌─────────────┐
                                      │    Docker   │
                                      │   Builder   │
                                      └──────┬──────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                           Install         Test           Build
                              │              │              │
                              └──────────────┼──────────────┘
                                             ▼
                                       Build Result
                                             │
                              ┌──────────────┴──────────────┐
                              ▼                             ▼
                         PostgreSQL                   Redis Events
                              │                             │
                              └──────────────┬──────────────┘
                                             ▼
                                      React Dashboard
```

---

# Build Lifecycle

A build follows a controlled state machine:

```text
QUEUED
  │
  ▼
RUNNING
  │
  ├──────────────► SUCCESS
  │
  ├──────────────► FAILED
  │
  └──────────────► CANCELLED
```

A queued build can also be cancelled before execution:

```text
QUEUED → CANCELLED
```

Terminal states:

```text
SUCCESS
FAILED
CANCELLED
```

cannot transition to another state.

---

# Build Pipeline

Each project can define three commands:

```text
install_command
test_command
build_command
```

The worker executes configured stages sequentially.

For example:

```text
pip install -r requirements.txt
        ↓
pytest
        ↓
python build.py
```

If a stage fails, subsequent stages are not executed.

The failed stage is stored with the build.

---

# GitHub Webhook Flow

When a GitHub repository receives a push:

```text
GitHub Push
    │
    ▼
POST /webhooks/github
    │
    ▼
Verify X-Hub-Signature-256
    │
    ▼
Check event type
    │
    ▼
Extract:
    ├── repository
    ├── branch
    └── commit SHA
    │
    ▼
Find ShipForge project
    │
    ▼
Create Build
    │
    ▼
Queue Build
    │
    ▼
Worker executes build
```

ShipForge ignores unsupported webhook events and validates the webhook signature before processing the payload.

---

# Docker Architecture

ShipForge uses Docker to isolate build execution.

The development environment consists of:

```text
Docker Compose
│
├── PostgreSQL
├── Redis
└── ShipForge Worker
        │
        └── Docker socket
                │
                ▼
        Build Containers
```

The worker uses the Docker Engine to create temporary build containers.

The build environment is based on the ShipForge build image and contains the tools required for repository execution.

Build containers are run with:

```text
--rm
```

so the container is automatically removed after execution.

---

# Technology Stack

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis
* Pytest

## Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Axios

---

# Database

ShipForge uses PostgreSQL to persist project and build information.

The main entities are:

```text
Project
   │
   │ 1:N
   ▼
Build
   │
   │ 1:N
   ▼
BuildLog
```

### Project

Stores:

* Project name
* Description
* Repository URL
* Install command
* Test command
* Build command
* Creation/update timestamps

### Build

Stores:

* Project
* Build number
* Status
* Current stage
* Failed stage
* Branch
* Commit SHA
* Creation time
* Start time
* Finish time

### BuildLog

Stores:

* Build ID
* Build output
* Timestamp

---

# Redis Queue

Redis is used to decouple build creation from build execution.

Instead of executing a potentially long-running build inside the API request:

```text
API
 ↓
Create Build
 ↓
Queue Job
 ↓
Return Response
```

The worker consumes the job separately:

```text
Redis
 ↓
Worker
 ↓
run_build()
```

This allows the API and build execution to operate independently.

---

# Local Development

## Prerequisites

Install:

* Git
* Python 3.12
* Node.js
* Docker Desktop
* `uv`

---

## Start Infrastructure

From the project root:

```bash
docker compose up -d
```

This starts:

```text
PostgreSQL
Redis
ShipForge Worker
```

---

## Backend

```bash
cd backend
uv sync
```

Run the FastAPI application using the project's configured development command.

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# Testing

Backend tests are run with:

```bash
cd backend
uv run pytest
```

V1 currently has:

```text
70 passed
```

The test suite covers areas including:

* Build creation
* Build lifecycle
* Build retry
* Build cancellation
* Build logs
* Docker execution
* Repository handling
* Workspace management
* Redis queue
* Redis events
* WebSockets
* GitHub webhooks
* Webhook security
* Project APIs

---

# V1 Scope

ShipForge V1 focuses on establishing the core CI/CD architecture:

```text
GitHub
  ↓
Webhook
  ↓
FastAPI
  ↓
Redis
  ↓
Worker
  ↓
Docker
  ↓
Install / Test / Build
  ↓
PostgreSQL
  ↓
Dashboard
```

The goal of V1 is to provide a working foundation rather than reproduce the complete feature set of large CI/CD platforms.

---

