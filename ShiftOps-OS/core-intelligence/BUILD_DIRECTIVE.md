# Intent-to-Code System Layer — Build Directive

## What this system IS
- A system layer that converts human intent into structured guidance and/or code
- Form-factor agnostic (app, CLI, library, embedded system)
- Deterministic where enforcement is required

## What this system IS NOT
- Not an autonomous AI agent
- Not model-centric
- Not runtime-inferential
- Not a promise of full automation

## Authority Rules
- Human intent is the only authority
- AI-derived input is environmental context only
- Contracts are law
- Validators enforce; they do not fix
- Compilers execute deterministically or not at all

## Primary Outputs (in order)
1. Structured guidance / path direction
2. Ordered build steps
3. Code (language-agnostic: Python, JSON, Kotlin, scripts, etc.)

## AI Usage Boundary
- AI may assist with understanding upstream context (e.g., search engine AI results)
- AI never validates, decides, compiles, or mutates intent

## Allowed Changes
- Rename files for clarity
- Reframe README language
- Move files to reflect layer boundaries
- Add non-executing examples or schemas

## Forbidden Actions
- Introducing agent behavior
- Adding runtime inference
- Letting AI author intent
- Silent autofill after validation
  
