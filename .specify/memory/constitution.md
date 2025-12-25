<!--
=============================================================================
SYNC IMPACT REPORT - Constitution Amendment
=============================================================================
Version Change: 1.0.0 → 1.1.0

Modified/Added Principles:
  - NEW: Principle VI - Code Quality & Separation of Concerns

Sections Added:
  - Code Quality & Separation of Concerns principle with module cohesion,
    responsibility isolation, and testability requirements

Sections Removed:
  - None

Templates Requiring Updates:
  ✅ plan-template.md - Updated (added code quality gates)
  ✅ spec-template.md - No changes needed (already emphasizes testability)
  ✅ tasks-template.md - Updated (added code quality task types)
  ✅ agent-file-template.md - No changes needed (general purpose template)
  ✅ checklist-template.md - No changes needed (general purpose template)

Follow-up TODOs:
  - None

Amendment Rationale:
  MINOR version bump - Added new principle requiring module cohesion,
  responsibility isolation, and testability. Enhances code maintainability
  without breaking existing governance structure.

=============================================================================
-->

# App Constitution

## Core Principles

### I. Self-Contained Operation
The application MUST function fully without external runtime dependencies. Core functionality MUST NOT require external services, databases, or third-party APIs to operate.

**Rationale**: Dependencies create failure points, increase complexity, and reduce reliability. Self-contained systems are predictable, debuggable, and always available.

### II. Deterministic-First Processing
At least 90% of requests MUST be handled by deterministic algorithms before attempting non-deterministic approaches. Deterministic processing MUST be attempted first, with non-deterministic methods as fallback only.

**Rationale**: Deterministic algorithms are orders of magnitude faster, require no external services, and produce consistent results. Non-deterministic approaches should enhance, not replace, core functionality.

### III. Zero Build Complexity (NON-NEGOTIABLE)
User interfaces MUST be deployable without compilation, transpilation, or build steps. Source code MUST be directly executable without preprocessing.

**Rationale**: Build steps add complexity, slow development cycles, and create deployment friction. Direct execution enables instant iteration and eliminates entire categories of tooling failures.

### IV. Data Format Stability
API contracts MUST preserve upstream data formats without transformation. Data structures from authoritative sources MUST be returned unmodified.

**Rationale**: Format transformations introduce bugs, break compatibility, and increase maintenance burden. Preserving canonical formats ensures predictability and interoperability.

### V. Aggressive Optimization & Fault Tolerance
Frequently accessed data MUST be cached with sensible retention policies. System MUST continue operating when optional features fail or are unavailable.

**Rationale**: Performance optimization reduces latency and enables scale. Graceful degradation ensures partial functionality is always better than complete failure.

### VI. Code Quality & Separation of Concerns
Modules MUST have single, well-defined responsibilities. Functions MUST be independently testable without extensive mocking. Related functionality MUST be co-located; unrelated concerns MUST be isolated.

**Rationale**: Clear boundaries reduce cognitive load, prevent cascading changes, and enable parallel development. Testability without complex setup indicates proper abstraction. Co-location improves discoverability while isolation prevents coupling.

## Architecture Priorities

Speed > Reliability > Simplicity > Flexibility

When these priorities conflict, prefer the higher-ranked priority. The system optimizes for instant response times, zero external dependencies, minimal complexity, and optional enhancements.

## Anti-Patterns

❌ Require external runtime dependencies for core functionality  
❌ Make optional enhancements mandatory  
❌ Introduce compilation or build requirements  
❌ Transform canonical data formats  
❌ Add dependencies without graceful fallback  
❌ Prioritize flexibility over simplicity  
❌ Mix unrelated concerns in single modules  
❌ Create functions requiring extensive mocking to test  

## Governance

This constitution supersedes all other practices. All changes MUST be verified against these principles. Amendments require justification demonstrating alignment with simplicity-over-complexity philosophy. Complexity MUST always be justified.



**Version**: 1.1.0 | **Ratified**: 2025-12-25 | **Last Amended**: 2025-12-26
