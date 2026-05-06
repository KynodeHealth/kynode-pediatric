# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.
#
# Multi-stage Dockerfile for the KYNODE Pediatric Local Node.
# Stage 1 builds the four pediatric packages + the local-node app into a
# venv. Stage 2 copies just the venv + the package source into a slim
# runtime image so the published container stays small.
#
# Why python:3.12-slim instead of 3.14: 3.12 is the current "LTS-style"
# Python on cloud platforms (fly.io, Render, Cloud Run all default here),
# the test suite passes on it, and it has wheels for every dependency we
# use without falling back to source builds on every deploy.

FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Copy only what we need to install. Order matters for layer caching:
# pyproject files first (rarely change), then sources.
COPY packages/growth-curves /build/packages/growth-curves
COPY packages/triage-ranges /build/packages/triage-ranges
COPY packages/anomaly-detection /build/packages/anomaly-detection
COPY packages/vaccinations /build/packages/vaccinations
COPY apps/local-node /build/apps/local-node

RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install \
        ./packages/growth-curves \
        ./packages/triage-ranges \
        ./packages/anomaly-detection \
        ./packages/vaccinations \
        ./apps/local-node


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    KYNODE_LOCAL_NODE_DB=/data/kynode_pediatric_local_node.sqlite3

# We intentionally run as root in the container.
#
# Why: Railway (and similar PaaS) mount persistent volumes at /data with
# root ownership, so a non-root user cannot create the SQLite file at
# startup and the deploy fails. The two clean alternatives — an init
# script that chowns /data before dropping privileges, or a SUPPLEMENTAL
# group with shared GID — both add operational fragility for a pre-pilot
# demo container that does not accept user uploads, executes no
# arbitrary code, and reads no untrusted SQL. The threat model is
# "stateless FastAPI serving deterministic JSON" — root inside the
# container provides no meaningful blast radius beyond the container
# itself.
RUN mkdir -p /data
COPY --from=builder /opt/venv /opt/venv

WORKDIR /data
EXPOSE 8080

# uvicorn factory mode: kynode_pediatric_local_node:create_app reads
# KYNODE_LOCAL_NODE_DB from env to put the SQLite file on the persistent
# /data volume mount that the host (fly.io / Railway / Render) provides.
#
# Shell-form CMD so $PORT expands at runtime. Railway assigns a dynamic
# PORT via env var; fly.io and local docker run keep the 8080 default.
# This makes the same image portable across all three hosts without
# rebuilds.
CMD uvicorn kynode_pediatric_local_node:create_app --factory --host 0.0.0.0 --port ${PORT:-8080}
