# AI-assisted and AI-native development

This project is a working showcase, not just a collection of prompts. Use the
F1 application to see how AI changes the way you understand requirements,
implement changes, test results, and decide what to ship.

First get the app running with [native Windows/macOS setup](./native-setup.md),
[Windows/WSL onboarding](./wsl-setup.md), or [shared Linux setup](./setup.md).
An agent cannot compensate for an unknown baseline
or an editor connected to the wrong interpreter.

## Two working styles, one accountable engineer

Terminology varies across teams. In this workshop:

| | AI-assisted development | AI-native development |
|---|-------------------------|-----------------------|
| Who drives the next step? | You choose each edit, question, and command | You define an outcome and let an agent coordinate a bounded sequence |
| Typical AI contribution | Completion, explanation, a focused edit, or test suggestions | Repository exploration, planning, multi-file edits, and tool-based verification |
| Your role | Implement and evaluate suggestions | Define constraints, approve plans/tools, steer, review, and independently verify |
| Useful starting point | Learning unfamiliar code or making a small, well-understood change | A task with clear acceptance criteria that benefits from coordinated work |
| Main risk | Accepting a plausible suggestion without understanding it | Delegating ambiguity or excessive permissions, then trusting a convincing completion report |

**AI-native does not mean unsupervised, automatically correct, or "no coding
knowledge required."** It describes a development workflow designed around the
AI/tool loop. Use less autonomy when understanding or confidence is low, and
pause delegation when you cannot explain the proposed changes.

Three terms help when configuring tools: the **model** generates and reasons
about responses; an **agent** combines that model with a loop that can use tools;
the **harness** is the runtime that supplies those tools, permissions, and
customization support. Changing the model does not automatically grant new
tools, load project instructions, or fix the selected Python environment.

Neither style requires adding a model to the product. The core F1 app still
uses local JSON and keyword parsing; you are changing how it is developed,
not making its runtime dependent on AI.

## Working style is different from workflow structure

The two existing paths compare **how you organize work**, not which one is
allowed to use agents:

| Working style | [Copilot-native workflow](./copilot-native.md) | [Copilot + Spec Kit](./copilot-spec-kit.md) |
|---------------|----------------------------------------------|------------------------------------------|
| AI-assisted | Use chat and focused suggestions; drive the edits and tests yourself | Ask for help with specs, plans, or individual tasks; implement and validate them yourself |
| AI-native | Let an agent execute an approved plan within a defined scope | Let an agent follow the specification, plan, and tasks with human approval gates |

"Copilot-native" means using Copilot's own workflow without the extra Spec Kit
process. It is **not** a synonym for "AI-native development." Spec Kit adds
explicit artifacts; it does not determine the level of autonomy or guarantee
quality.

For a fair comparison, change one dimension at a time. Compare working styles
while holding the process constant, or compare the two process paths while
holding the working style constant. You do not need to complete every possible
combination in one session.

## What changes in day-to-day engineering?

| Activity | What changes with AI | What remains your responsibility |
|----------|----------------------|----------------------------------|
| Requirements | A vague request can rapidly become a large implementation; write outcomes, constraints, and non-goals first | Decide what the user actually needs |
| Context gathering | The agent can search the repository and propose a request path | Check that it found current code rather than stale docs or similar symbols |
| Design | You can cheaply explore alternatives and generate plans/contracts | Judge compatibility, simplicity, data limitations, and trade-offs |
| Implementation | Work shifts from typing every line to directing and reviewing bounded changes | Understand the resulting code and reject unnecessary dependencies or scope expansion |
| Testing | Generating tests becomes easier, but the AI can repeat its own mistaken assumptions | Use independent acceptance criteria, meaningful fixtures, negative cases, and regression tests |
| Debugging | The agent can gather evidence and try a fix in a loop | Require a reproduction and a causal explanation, not random edits until a test goes green |
| Review and release | More code can arrive faster than a human can review it | Keep changes small, inspect diffs, run CI, and approve deployment yourself |
| Security and cost | Context may leave the machine; tools may execute commands or call services | Protect secrets, constrain permissions, follow policy, and monitor exposed usage/cost |

The goal is not to maximize generated code or eliminate human intervention.
It is to produce a correct, understandable change with an appropriate level
of effort and risk.

## Make this repository useful context

Give the assistant the smallest relevant context packet:

1. **Outcome:** the user problem and unchanged acceptance criteria.
2. **Constraints:** JSON storage, keyword-first queries, cached loaders,
   Ergast compatibility, and a build-free application UI.
3. **Relevant surfaces:** the request path, affected callers, and tests.
4. **Permissions:** what it may read, edit, run, or install.
5. **Evidence:** baseline results, a reproduction, and required verification.

This repository already provides:

| Resource | Purpose |
|----------|---------|
| [Project instructions](../../.github/copilot-instructions.md) | Shared architecture and development constraints |
| [Constitution](../../.specify/memory/constitution.md) | Principles used by the Spec Kit path |
| [Spec Kit agents](../../.github/agents) and [skills](../../.github/skills) | Reusable workflows; check discovery in the selected harness |
| [Query parser](../../app/query_parser.py) and [query router](../../app/routers/query.py) | A concrete path to inspect for the repair lab |
| [Application tests](../../tests) and [shared repair checks](./checks/repair_checks.py) | Existing behavior and a common acceptance contract |

Instructions and prompts guide an agent; they do not enforce permissions or
prove that it followed them. Verify the files and context actually loaded.
Do not upload credentials, private data, or unrelated repository content.
Treat copied web pages, issue text, and data as untrusted input, not authority
to override your constraints.

## Try both styles on the repair lab

Use the [shared repair brief](./repair-lab.md). Seed the same regression in
independent worktrees first. Do not change the acceptance criteria or carry
the first solution into the second attempt.

### Run 1: AI-assisted, developer-led

1. Open the query parser and the failing acceptance check yourself.
2. Ask Copilot for an explanation without authorizing edits:

   > Explain why the winners question is routed incorrectly. Cite the matching
   > rules and their order. Separate evidence from assumptions. Suggest two
   > possible fixes and their regression risks. Do not edit files or run commands.

3. Check the explanation against the code. Choose and implement a fix yourself.
4. Ask for focused test assistance:

   > Suggest a regression test that distinguishes race-winner questions from
   > championship questions. Explain what it would catch. Keep the existing
   > acceptance checks unchanged.

5. Review and add the test, run the checks below yourself, and inspect the diff.
   You remain in control of each step; AI accelerates specific pieces.

### Run 2: AI-native, agent-led with boundaries

1. Attach the same brief and give the agent a bounded outcome:

   > Investigate the repair brief using this repository. Preserve championship,
   > standings, and empty-query behavior. Keep the keyword-first architecture
   > and supplied checks unchanged. Propose a plan with exact verification
   > commands. Do not edit until I approve. Do not change dependencies,
   > operating-system settings, remote services, or publish anything.

2. Challenge an assumption and approve a scoped plan only when you understand it.
3. Authorize implementation:

   > Implement the approved plan in the current exercise worktree. Add a
   > regression test and run the focused acceptance checks. If requirements,
   > permissions, or scope change, stop and report rather than expanding the task.

4. Observe the tool loop: gather context, edit, run checks, inspect failures,
   and revise. Review individual tool requests.
5. Independently run verification and review the diff. Ask the agent to explain
   any line you cannot defend.

Use the supported planning/agent controls in your installed Copilot harness;
natural-language "do not edit" is not a technical permission boundary. If the
required tools are unavailable, record that limitation rather than pretending
the agent executed them.

### Same finish line for both runs

```bash
python -m pytest -q _docs/tutorials/checks/repair_checks.py
python -m pytest -q tests/integration/test_query_parsing.py tests/contract/test_query.py
git diff
```

Then run the application suite before accepting the change:

```bash
python -m pytest -q tests
```

Check response content, not just HTTP status or an agent's "done" message.
These checks use local data and do not require a runtime LLM.

## Learn to reject attractive shortcuts

| Suggestion | Engineering question to ask |
|------------|-----------------------------|
| "Replace JSON with a database" | Does the task justify violating the project's storage constraint? |
| "Change the expected result so the test passes" | Is the test wrong, or did the implementation violate the user's intent? |
| "Send all queries to an LLM" | Why add latency and external dependencies to a deterministic routing repair? |
| "Remove a broad keyword" | Which valid queries could stop working, and how will we prove compatibility? |
| "All tests passed, so ship it" | Which commands actually ran, what did they assert, and were UI/error cases checked? |

An alternative solution is not wrong merely because it differs from yours.
Accept or reject it using the requirements and evidence.

## Definition of done

- [ ] The change satisfies the original user need and acceptance criteria.
- [ ] You can explain the implementation and its trade-offs.
- [ ] Existing consumers and the application's architectural constraints remain intact.
- [ ] Student-written tests add value without weakening the supplied checks.
- [ ] Required commands actually ran; failures and unavailable checks are reported.
- [ ] UI behavior is inspected when the change affects the browser.
- [ ] The diff contains no secrets, incidental files, or unexplained dependencies.
- [ ] A human approves the change before commit, push, or deployment.

## Compare what actually improved

Record the working style alongside the process in the
[assessment sheet](./assessment.md). Compare correctness, review effort,
substantive corrections, time, tool permissions, and any visible usage/cost.
Do not assume that delegation is always faster or that a longer plan is better.

Explain where AI helped, where it misled you, what you verified independently,
and which responsibilities did not move to the tool. A hybrid workflow is a
valid conclusion: for example, use AI-assisted exploration to learn the code,
then delegate a well-defined implementation task.

Next: choose [Copilot-native](./copilot-native.md) or
[Copilot + Spec Kit](./copilot-spec-kit.md), keeping your chosen working style
constant for the process comparison.
