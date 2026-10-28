# Path B: Copilot + Spec Kit

Use [shared setup](./setup.md) and a fresh Spec Kit worktree for each lab.
Use the **same** [repair brief](./repair-lab.md) or
[feature brief](./feature-lab.md) as Path A.

Choose your [working style](./ai-development.md) separately from this process.
You can use AI assistance while driving each task yourself, or let an agent
execute approved tasks. Spec Kit's artifacts do not make a workflow autonomous.

The repository includes [agents](../../.github/agents),
[skills](../../.github/skills), and [templates](../../.specify/templates).
These checked-in workflows are the course reference, not a promise of
compatibility with every future Spec Kit release or Copilot harness.

**Platform caveat:** the checked-in automation invokes Bash helpers. WSL is not
required, but PowerShell alone does not execute those helpers. Native Windows
users should read the [Git Bash and manual-variant options](./native-setup.md#bash-based-spec-kit-helpers)
before starting. macOS users can invoke helpers with Bash from Terminal.

## 1. Inspect the existing constitution

Read [the constitution](../../.specify/memory/constitution.md) and shared project
instructions. Identify constraints relevant to your lab. Do not rewrite the
project constitution merely to make a proposed implementation fit.

Use the installed workflow picker or slash-command completion to find
`speckit.specify`. Some harnesses expose workflows as custom agents, others as
skills; use the supported entry point rather than assuming a command exists.
The conventional names below describe the checked-in workflow.

## 2. Specify and clarify

Invoke `speckit.specify` with the shared brief:

> Create a new specification for this tutorial lab. Use the supplied acceptance
> criteria unchanged. Identify constraints and non-goals. Do not overwrite
> specs/001-f1-data-display or implement code.

The workflow may create and switch to a numbered feature branch. This is
expected **inside this dedicated worktree**; record the new branch. Do not
switch another worktree onto it. Use a new feature directory for each run;
do not hard-code its number.

Review the generated spec, then run `speckit.clarify` if uncertainties remain.
If the brief already answers a question, point to that evidence rather than
inventing a new requirement. Record "no clarification needed" when appropriate.

## 3. Plan and decompose

Run `speckit.plan` with the architecture constraints and verification commands.
Review its design, contracts and constitution checks **before** continuing.
Then run `speckit.tasks`. Optionally use `speckit.analyze` or
`speckit.checklist` to look for inconsistencies.

Human approval gate:

- Does every acceptance criterion map to implementation and verification work?
- Are sample data and unknown completeness represented honestly?
- Are unchanged API contracts and UI consumers protected?
- Is the artifact/work breakdown proportionate to this task?

For the small repair, record unnecessary artifacts or duplicated effort
instead of pretending that more documentation always improves quality.

## 4. Implement and verify

- **AI-assisted run:** take one generated task at a time. Ask for focused
  explanations or suggestions, then drive implementation and test commands
  yourself.
- **AI-native run:** after approval, run `speckit.implement` against the generated
  tasks, reviewing its scope and tool requests.

Both styles require regression tests and the same opt-in acceptance command
used in Path A. Review commands and diffs; Spec Kit does not make agent actions
safe or generated tests correct.

Run the application tests yourself. For the feature, complete the browser
checklist. Compare implementation, spec, contracts and task status; a checked
task box is not execution evidence. Mark incomplete work honestly.

## 5. Evaluate the structure

Submit the working change, relevant artifacts and
[comparison evidence](./assessment.md). Identify a decision that became clearer
because it was written down, and an artifact that did not justify its effort.
Explain when you would use a lighter, heavier, or hybrid workflow next time.

The [original showcase](../github-copilot-learning-guide.md) and
[historical feature](../../specs/001-f1-data-display/README.md) remain available
for reflection after the independent run. Do not use their status labels as
proof that your new lab passed.
