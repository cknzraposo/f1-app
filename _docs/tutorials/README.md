# AI-assisted development: choose your workflow

Build judgement, not dependence on generated code. Compare two ways of using
GitHub Copilot on the same FastAPI and vanilla-JavaScript application:

- [Path A: Copilot-native](./copilot-native.md): explore, plan, approve, implement,
  verify.
- [Path B: Copilot + Spec Kit](./copilot-spec-kit.md): specify, clarify, plan,
  tasks, implement, verify.

Spec Kit is a workflow toolkit used with Copilot, not a competing AI model.
Neither path is assumed to win. A small repair and a cross-layer feature let you
investigate whether additional structure is worth its cost.

For the website version, see the [tutorial landing page](./index.md).
Repository owners can follow the [GitHub Pages publishing walkthrough](./publishing.md).

## Outcomes and route

By the end, you should be able to:

1. Provide useful context and distinguish requirements from assumptions.
2. Select an appropriate level of agent autonomy and workflow structure.
3. Review a plan before authorizing edits.
4. Verify behavior rather than accepting a confident answer or HTTP 200.
5. Explain a suggestion you rejected and defend a workflow choice with evidence.

| Step | Material | Suggested time |
|------|----------|----------------|
| 1 | [Shared setup and capability check](./setup.md) | 30 minutes |
| 2 | [Repair lab](./repair-lab.md), through both paths | 35 minutes per path |
| 3 | Repair comparison and discussion | 20 minutes |
| 4 | [Feature lab](./feature-lab.md), through both paths | 75 minutes per path |
| 5 | [Assessment and reflection](./assessment.md) | 30 minutes |

Allow about five hours plus breaks; split across two or three sessions. These
are planning estimates, not measured classroom results. For a shorter workshop,
complete setup and the paired repair lab; assign the feature lab as follow-up.

## Shared rules

- Both paths receive the same brief, constraints, fixtures, and acceptance checks.
- Use separate branches/worktrees from the same recorded revision, fresh chats,
  and matching model, harness, permissions, and time budgets.
- Keep project-wide instructions identical. Isolate Spec Kit-specific
  customizations in Path A as described in [setup](./setup.md).
- Stop for human approval after planning, before implementation, and before
  accepting a final diff. Never enable blanket command approval for the course.
- Do not add a database, frontend build system, or runtime LLM dependency.
- Do not change acceptance checks to make a solution pass. Students add their
  own regression tests as well.
- Preserve the original Ergast response and existing consumers.

## What is and is not included

The repair already works in the application: deliberately seed the documented
regression in your exercise branch. The feature endpoint is intentionally
**not implemented**. Its opt-in acceptance checks should fail until students
implement it. Ordinary application tests do not discover those checks.

The API uses checked-in JSON. Some season files are samples; derived standings
are not proof of official championship results. The feature lab makes this
limitation visible without inventing full-season totals.

The application does not need Ollama or Azure for these lessons. Using Copilot
as a development assistant still requires appropriate access and network
connectivity. The browser also uses CDN resources, so do not promise a fully
offline web experience.

## Further reading

- [Standalone debugging lessons](../student-guide.md) and [tutor notes](../tutor-guide.md)
- [Historical showcase](../github-copilot-learning-guide.md)
- [Original Spec Kit artifacts](../../specs/001-f1-data-display/README.md)
- [Current capabilities and optional extensions](./setup.md#capability-and-access-check)
- [Instructor pilot checklist](./assessment.md#instructor-pilot-checklist)
