# Intent-to-Code System Layer

This repository implements an **Intent-to-Code System Layer**.

The purpose of the system is to take **human intent**, enrich it with
non-authoritative world context, apply governed structure, and return:

- structured guidance,
- ordered build steps,
- and optionally executable code.

This system is **form-factor agnostic**. It may be used as an application,
CLI, library, embedded system, or supporting layer inside another tool.

---

## What This System Is

- A system layer that structures human intent
- A deterministic enforcement pipeline where required
- Language-agnostic by design (Python, JSON, Kotlin, scripts, etc.)
- Human-in-the-loop by default

---

## What This System Is Not

- Not an autonomous AI agent
- Not model-centric
- Not a runtime inference engine
- Not a promise of full automation

---

## Primary Outputs

Depending on the intent provided, the system may produce one or more of:

1. Structured guidance / path direction
2. Ordered build steps
3. Code (in any appropriate language or format)

Code generation is an outcome, **not a requirement**.

---

## Authority Model

- Human intent is the sole authority
- AI-derived input is treated as environmental context only
- Context may inform understanding, never decisions
- Contracts define allowed structure and constraints
- Validators enforce contracts without mutation
- Execution occurs deterministically or not at all
## Intent Shape

Intent always specifies a goal and whether guidance should be produced.
Code generation is optional and requested explicitly.

---

## AI Usage Boundary

AI is used only to assist with **understanding upstream context**, such as:

- search engine AI summaries
- normalized descriptions of common practices or steps

AI never:
- authors intent
- validates intent
- decides outcomes
- compiles code
- mutates structured inputs

---

## System Structure

The system is composed of distinct, non-overlapping layers:

- **Context Harvest**  
  Descriptive, inert data representing external knowledge.

- **Intent**  
  Human-authored structured intent.

- **Validation**  
  Contract enforcement. No autofill. No correction.

- **Execution Paths**  
  Optional outcomes, such as compilers or generators.
## Guidance and Paths

The system may produce structured guidance artifacts that describe
ordered build paths without executing code.

Guidance is a first-class output and may be produced independently
of any compiler or generator.

The compiler is **one possible execution path**, not the system itself.

---

## Contracts

Schemas under `/contracts/core/` define the canonical structure of the system.

Contracts are authoritative and must be satisfied before any execution occurs.
If validation fails, execution stops with explanation.

---

## Design Goals

- Preserve human authority
- Prevent hidden behavior
- Enable auditability
- Avoid vendor lock-in
- Support use in restricted or offline environments
## Clarification vs Correction

When validation fails, the system may return explanatory messages.

These messages:
- explain why execution stopped
- do not ask questions
- do not modify intent
- do not trigger retries

Clarification is informational only.

---
### Checklist Exporter

An optional execution path that converts guidance into a
human-readable checklist (e.g., Markdown).

This path does not generate code and does not modify intent.

### Execution Router

Execution paths are selected explicitly based on intent outputs.

There are no default executions.
Each execution path runs deterministically or not at all.

## Context Harvest

Context Harvest artifacts describe non-authoritative information about
the external world (e.g., common practices, patterns, constraints).

Context:
- informs understanding
- does not decide outcomes
- does not generate steps
- does not mutate intent

Context is always upstream and inert.

## Intent Draft Assistance

Context Harvest artifacts may be used to assist humans
in drafting intent.

Draft assistance:
- suggests structure
- highlights considerations
- surfaces constraints

Drafts are non-authoritative and must be reviewed
and authored by a human before validation.

## Status

This repository represents an evolving system layer.
Implementation details may change, but the authority model does not.

