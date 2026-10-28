# Path A: Copilot-native

Follow [shared setup](./setup.md), including disabling Spec Kit discovery.
Use either [the repair brief](./repair-lab.md) or
[the feature brief](./feature-lab.md); do not change their acceptance criteria.
Run each exercise in its own worktree and fresh chat.

First choose your [working style](./ai-development.md). "Copilot-native" names
this lightweight process, not the level of agent autonomy. You can drive each
step yourself with AI assistance, or delegate bounded execution to an agent.

## 1. Explore, do not edit

Attach the lab brief and relevant source files, not the entire documentation
tree. Use a request such as:

> Explain the request path relevant to this brief. Cite files and symbols.
> Separate observed behavior from assumptions. Identify existing tests and
> API consumers. Do not edit files or invoke Spec Kit workflows.

Check at least one claim against the actual code. Correct stale architecture
assumptions: routes and frontend logic now live in modules, not just the older
monolithic files mentioned in some historical instructions.

## 2. Plan and approve

Select Plan or `/plan` where supported, or explicitly request:

> Propose the smallest complete change satisfying this brief. Preserve JSON
> storage, keyword-first behavior, caching, existing response contracts and the
> build-free UI. Identify ambiguous requirements, relevant files, regression
> risks, and exact verification commands. Do not edit until I approve.

Challenge one assumption and ask for an alternative. Approve only after the
plan covers negative cases and every affected consumer. For a simple repair,
a short plan is enough; a separate generated specification is not mandatory.

## 3. Implement a bounded change

For an **AI-assisted run**, request focused suggestions and apply/review changes
one step at a time; run the commands yourself.

For an **AI-native run**, after approval switch to an implementation-capable
agent if needed and delegate the bounded task:

> Implement the approved plan. Add your own regression tests, preserve the
> supplied acceptance checks, and run the narrow checks first. Stop and report
> unexpected requirements or changes outside the approved scope.

Review tool requests. Do not approve dependency changes, remote calls, or
destructive commands simply because the agent asks. Ask for the actual test
output, not just "tests pass."

## 4. Review and verify yourself

Run the lab's acceptance command and application tests. Inspect `git diff`:
does it repair the behavior, weaken a test, mutate cached JSON, or hide an
error? For the feature lab, complete the browser checks as well. A passing API
test is not a substitute for checking the UI.

Keep a short decision note using [the assessment sheet](./assessment.md).
Include rejected suggestions and unresolved limitations. Do not force the
agent to generate extra documents just to resemble Path B.

## 5. Optional: add only useful customization

After the timed comparison, repeat a task and identify a real source of rework:

- Repeatedly missed project convention: refine shared project instructions.
- Repeated multi-step verification: consider a skill.
- A recurring review role with limited tools: consider a custom agent.
- A single reusable request in a supported Local session: consider a prompt file.

Show evidence that the customization is loaded and improves the repeated task.
Do not add all four by default. Keep extensions separate from the scored run
unless both paths receive the same configuration.
