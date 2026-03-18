# EXECUTION CONTRACT — Intent-to-Code OS

## Purpose
This document defines the execution boundaries, invocation rules, and
responsibility separation for the Intent-to-Code system.

It exists to prevent architectural drift, implicit behavior, and
unauthorized execution paths.

This contract is authoritative.

---

## Core Principles

- Deterministic execution only
- No inference
- No defaults
- No agent loops
- AI is non-authoritative
- Python is a carrier, not the system

---

## Canonical Execution Order

Intent
→ Validation (security envelope enforced)
→ Guidance Producer (Batch 11, optional)
→ Guidance Executor (Batch 10A)
→ Guidance Exporter (Batch 10B)
→ Router returns explicit results

No batch may reorder this flow.

---

## Batch Definitions

### Router
**Role**
- Sole execution authority
- Explicit invocation only

**May**
- Invoke batches by name
- Gate execution by intent flags
- Return execution results

**May Not**
- Generate guidance
- Mutate intent
- Perform execution logic

---

### Batch 11 — Guidance Producer
**Role**
- Upstream context production

**May**
- Read validated intent
- Perform passive search
- Produce in-memory guidance payload

**May Not**
- Execute logic
- Write files
- Invoke executors or exporters
- Modify intent

---

### Batch 10A — Guidance Executor
**Role**
- Deterministic rendering

**May**
- Consume guidance payload
- Produce rendered output

**May Not**
- Perform search
- Write files
- Change routing
- Mutate intent

---

### Batch 10B — Guidance Exporter
**Role**
- File persistence (markdown only)

**May**
- Write guidance markdown to outputs/

**May Not**
- Execute logic
- Perform search
- Mutate guidance
- Affect routing

---

### Compiler
**Role**
- Code generation (optional path)

**May**
- Execute only when explicitly requested

**May Not**
- Run implicitly
- Affect guidance flow

---

## Data Flow Rules

- Intent is read-only after validation
- Guidance is ephemeral and in-memory
- Only exporters may write to disk
- Router owns execution decisions

---

## Prohibited Behaviors (Hard Violations)

- Producers executing logic
- Executors writing files
- Exporters invoking other batches
- Any AI component deciding execution
- Implicit defaults or fallbacks

Any violation requires rollback.

---

## Failure Handling

- Missing guidance → skip guidance path
- Empty search results → render empty guidance
- No retries
- No escalation
- No silent execution changes

---

## Authority Statement

This contract supersedes:
- inline comments
- chat history
- future convenience changes

If code and this contract disagree, the contract wins.
