# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based system for managing a research request rotation among participants. The system uses MongoDB for data persistence, Bitwarden for secrets management, and is deployed as Google Cloud Run jobs.

## Architecture

### Two-Job System

The application consists of two separate Cloud Run jobs:

1. **res-req-job** (`src/res_req.py`): Main job that manages the research request rotation
   - Reads participant order from `order.json` (single source of truth)
   - Queries MongoDB to load participant data (emails, names)
   - Links participants in a circular rotation using `next_participant` references
   - Likely sends emails/notifications to participants in sequence

2. **check-reply-job** (`src/check_reply.py`): Job that monitors participant replies
   - Currently minimal implementation

### Data Models (`models/`)

- **Participant** (`models/participant.py`): Pydantic model with:
  - Name fields (first_name, last_name, full_name)
  - Email management (primary_email, all_emails list)
  - Circular reference to next_participant for rotation logic
  - Auto-computed full_name and all_emails via validators

- **Log** (`models/log.py`): Tracks sent emails with participant, timestamp, and content

### Secrets Management

- Uses Bitwarden SDK (`src/bw_secrets.py`) to retrieve secrets at runtime
- Requires environment variables: `BW_API_URL`, `BW_ID_URL`, `BW_ACCESS_TOKEN`
- MongoDB connection string is fetched from Bitwarden vault

### MongoDB Schema

Database: `res-req`
Collections:
- `participants`: Stores participant documents with first_name, last_name, primary_email, all_emails
- `logs`: Stores email send history

### Participant Order System

The `order.json` file defines the rotation sequence. The application:
1. Reads the ordered list of full names from `order.json`
2. Looks up each participant in MongoDB by splitting full name into first/last
3. Creates a circular linked list via `next_participant` references
4. Maintains rotation state across executions

## Development Commands

### Local Setup

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export BW_API_URL="<bitwarden-api-url>"
export BW_ID_URL="<bitwarden-identity-url>"
export BW_ACCESS_TOKEN="<bitwarden-access-token>"
```

### Running Jobs Locally

```bash
# Run main research request job
python src/res_req.py

# Run reply checking job
python src/check_reply.py
```

## Deployment

The project uses Google Cloud Build with separate build configs for each job:

```bash
# Deploy res-req job
gcloud builds submit --config=ci/build_res_req.yaml

# Deploy check-reply job
gcloud builds submit --config=ci/build_check_reply.yaml
```

Each deployment:
1. Builds Docker image using Python 3.12 base
2. Pushes to Google Artifact Registry (us-central1-docker.pkg.dev)
3. Creates/updates corresponding Cloud Run job in us-central1 region

## Important Notes

- The system uses Python 3.12 (recent upgrade from commit history)
- Both jobs append "-job" suffix to their Cloud Run job names (res-req-job, check-reply-job)
- Participant lookup relies on exact "FirstName LastName" format in `order.json`
- The `next_participant` circular reference means the last participant points back to the first
- Secrets are never committed; always retrieved from Bitwarden at runtime
