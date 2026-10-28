<div class="tutorial-hero" markdown="1">

<span class="eyebrow">A hands-on GitHub Copilot workshop</span>

# Build with AI. Choose your process.

One Formula 1 project. Two development workflows. Learn to plan, implement,
test, and challenge AI-generated solutions using your own judgement.

[Start with setup](./setup.md) [Explore the two paths](#two-paths-one-project)

**About five hours &middot; Python + Git &middot; Beginner-intermediate developers**

</div>

## What you will build

You will repair a natural-language query that returns the wrong answer, then
design an API and UI improvement that makes sample-data limitations visible.
Both workflows start with the same requirements and acceptance checks.

This is not a contest between AI products. Both paths use GitHub Copilot;
Spec Kit adds a more explicit specification-driven process.

## Two paths, one project

<div class="path-grid" markdown="1">
<div class="path-card" markdown="1">

### Path A: Copilot-native

**Explore &rarr; plan &rarr; approve &rarr; implement &rarr; verify**

Try a lightweight workflow. Learn to supply context, review a plan, constrain
agent changes, and verify behavior yourself.

[Follow Path A](./copilot-native.md)

</div>
<div class="path-card" markdown="1">

### Path B: Copilot + Spec Kit

**Specify &rarr; clarify &rarr; plan &rarr; tasks &rarr; implement &rarr; verify**

Try a structured workflow. Find out when specifications, contracts, task lists,
and explicit checkpoints repay their overhead.

[Follow Path B](./copilot-spec-kit.md)

</div>
</div>

## Follow the workshop, step by step

| Step | What to do | Evidence to keep |
|------|------------|------------------|
| **1. Prepare** | [Install, run the baseline, and isolate the workflows](./setup.md) | Commit, environment, test results, capabilities |
| **2. Choose a path** | Read [Path A](./copilot-native.md) or [Path B](./copilot-spec-kit.md) | Reviewed plan and a human approval checkpoint |
| **3. Repair** | [Fix a successful request that returns the wrong data](./repair-lab.md) | Failing check, fix, regression test, passing checks |
| **4. Extend** | [Make local data coverage visible in the API and UI](./feature-lab.md) | Contract, implementation, tests, browser observations |
| **5. Compare** | Repeat on the other path from an independent baseline, then [assess the trade-offs](./assessment.md) | Decision record, rework, review effort, limitations |

Use the lesson menu to jump between the shared brief and your chosen workflow.
The two paths are alternatives to compare, not sequential implementation steps.
For a shorter session, complete setup and the paired repair lab first.

## Before you begin

- Basic Python knowledge, Git, a terminal, and Python 3.12+.
- VS Code and suitable GitHub Copilot access for the AI-assisted work.
- Time to review code and run checks, not just accept generated output.

**This website is the tutorial, not the running F1 application.** GitHub Pages
serves static content; run FastAPI locally using the setup guide. You do not need
Ollama, Azure, API keys, a database, or a frontend bundler for the core labs.
Treat the local season files as data samples, not verified complete seasons.

## For instructors and publishers

Use the [assessment rubric and pilot checklist](./assessment.md). The suggested
timing is an estimate; complete a real instructor pilot before teaching.

To publish your own copy, follow the [GitHub Pages walkthrough](./publishing.md).
The [source repository](https://github.com/cknzraposo/f1-app) also retains the
original Spec Kit showcase and standalone debugging lessons.
