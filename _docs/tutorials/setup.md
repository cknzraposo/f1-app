# Shared setup and reproducible comparison

Use this setup for both [learning paths](./README.md). **WSL is optional**:
choose the environment that is available and approved on your machine.

| Environment | First-time onboarding |
|-------------|-----------------------|
| Native Windows / PowerShell | [Windows without WSL](./native-setup.md#native-windows-powershell) |
| macOS / Terminal | [Native macOS](./native-setup.md#macos-terminal) |
| Windows / WSL | [WSL onboarding](./wsl-setup.md) |
| Linux with Python 3.12+ and Git already installed | Continue below |

The shell snippets below are Bash-style examples for Linux, macOS, or WSL.
Do not paste them unchanged into PowerShell. Use the native guide's
[PowerShell comparison equivalents](./native-setup.md#powershell-equivalents-for-the-comparison)
and explicit Windows `.venv` interpreter commands; activation is optional.

Already cloned the project and installed its dependencies through an onboarding guide?
Skip the installation commands below and continue with the capability check.
Before comparing workflows, read
[AI-assisted versus AI-native development](./ai-development.md): working style
and workflow structure are separate choices.

## Install and record a baseline

```bash
git clone https://github.com/cknzraposo/f1-app.git
cd f1-app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q tests
git rev-parse HEAD
git status --short
```

Resolve baseline failures before starting either path. Record the full commit,
Python/package versions (`python --version`, `python -m pip freeze`), test count,
warnings, and operating system. Dependency lower bounds are not a lockfile;
use the same resolved package versions in both environments. Do not copy
environment files containing secrets into your submission.

Start the app when needed:

```bash
uvicorn app.api_server:app --reload --host 127.0.0.1 --port 8000
```

Open `/docs` and `/static/index.html` at `http://127.0.0.1:8000`.
Run only one worktree's server on that port at a time; stop it with Ctrl+C.
For interpreter or editor problems, use the
[native-platform troubleshooting](./native-setup.md#troubleshooting) or
[WSL troubleshooting](./wsl-setup.md#troubleshooting) guide for your environment.

## Capability and access check

Features, names, access, and organizational policies change. Check the controls
available in your installed VS Code/Copilot environment before choosing how much
work to delegate.

| Capability | Course use | Preflight and fallback |
|------------|------------|------------------------|
| Copilot chat with repository context | Core: explain the request path and cite code | Sign in, open the correct worktree, inspect attached context |
| Plan agent / `/plan`, where available | Core: propose before editing | Otherwise explicitly request a plan without edits; this is an instruction, not a permissions boundary |
| Agent implementation and test tools | Core: scoped edits and verification | Check workspace trust, terminal permissions, Python selection; run tests yourself if agent tools cannot |
| Project instructions | Core: preserve architecture and contracts | Inspect which instructions the selected harness actually loads |
| Skills, custom agents, prompt files | Demonstrate only when they solve a repeated problem | Support and locations vary by harness; prompt files are Local-harness-specific in the referenced docs |
| Copilot cloud agent and Copilot code review | Optional extension | Check account entitlement, organization policy, repository permissions and usage budget |
| MCP integration | Optional extension | Use only an approved server with minimal permissions and no secrets in configuration committed to Git |
| Parallel sessions/worktrees, hooks, plugins | Optional extension | Confirm support; do not make previews or marketplace installation prerequisites |

Before class, fill in: date, VS Code version, Copilot extension/runtime version
where exposed, harness/session target, model, account access, organization
restrictions, enabled customizations, tool approvals, and usage budget. A model
choice does not determine the harness's file-format support.

Official references:

- [AI in VS Code](https://code.visualstudio.com/docs/agents/overview)
- [Planning](https://code.visualstudio.com/docs/agents/run/planning)
- [Customization types and harness compatibility](https://code.visualstudio.com/docs/agent-customization/overview)
- [Customization concepts](https://code.visualstudio.com/docs/agents/concepts/customization)
- [Copilot on GitHub: cloud work and review](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)
- [Spec Kit](https://github.com/github/spec-kit)

## Create independent lab worktrees

Start from a clean, published tutorial revision. Do not point `BASE` at an
uncommitted local draft: worktrees contain committed files only. Tutors can
publish an immutable course tag; record its resolved full commit as well.
The commands create new branches; choose unused names rather than deleting
existing student branches.

```bash
BASE=$(git rev-parse HEAD)
git worktree add -b tutorial/repair-native ../f1-repair-native "$BASE"
git worktree add -b tutorial/repair-speckit ../f1-repair-speckit "$BASE"
git worktree add -b tutorial/feature-native ../f1-feature-native "$BASE"
git worktree add -b tutorial/feature-speckit ../f1-feature-speckit "$BASE"
```

Open **one worktree per VS Code window**, not all in one multi-root workspace.
Create a separate `.venv` and install the recorded dependency versions in each.
Activate it or use its interpreter directly as in the native setup guide.
Select that interpreter in VS Code. Verify your working directory and `git branch --show-current`
before every lab command. Never implement the feature on top of a repair
solution when comparing paths.

## Prevent workflow leakage

Use a fresh VS Code profile with Settings Sync off for the comparison. Inspect
user, organization, extension/plugin, and workspace customizations. Disable
unrelated agents and skills in both paths; keep identical shared
project instructions. Start a new chat for every run.

In **each native worktree only**, move Spec Kit-discoverable files outside their
standard discovery directories before opening the chat:

```bash
mkdir -p .tutorial-disabled/agents .tutorial-disabled/skills
mv .github/agents/speckit.*.agent.md .tutorial-disabled/agents/
mv .github/skills/speckit-* .tutorial-disabled/skills/
git add .github/agents .github/skills .tutorial-disabled
git commit -m "Isolate Spec Kit workflows for the native tutorial"
```

These are intentional, recorded setup differences, not student solution changes.
The supplied revision has matching files. If a glob has no matches, inspect the
checkout rather than ignoring the error. Leave `.github/copilot-instructions.md`
unchanged in both paths. Do not load historical specs or disabled files as task
context in Path A. Spec Kit files supplied by plugins/user settings must also be
disabled there; moving workspace files alone is insufficient.

The generated `.github/agents/copilot-instructions.md` is historical plan output,
not the shared `.github/copilot-instructions.md`. Its old `src/` commands do not
describe this checkout. Verify commands against this setup and the actual tree.
If Spec Kit regenerates agent context during a run, record that workflow artifact
separately rather than silently changing the shared baseline instructions.

Use the customization UI or diagnostics supported by your installed harness to
confirm which files are active. If Spec Kit still appears in the native run,
fix discovery and restart the session before timing it. This reduces workflow
contamination; it is **not a security boundary** preventing repository searches.

For Spec Kit, use the checked-in agents and templates first. Check that the
`speckit.specify`, `speckit.clarify`, `speckit.plan`, `speckit.tasks`, and
`speckit.implement` workflows are discoverable. If the harness does not support
them, use a supported Local session or explicitly attach and follow the
checked-in workflow files, recording that fallback. Do not silently install the
latest CLI over the repository. The historical generated release is unknown;
record the commit of these files and any separately installed CLI version.

Shell support is separate from workflow discovery. This checkout's Spec Kit
automation invokes Bash helpers, not PowerShell equivalents. Native Windows
users can use approved Git Bash or the
[manual, template-based variant](./native-setup.md#if-bash-is-also-unavailable).
Record that difference rather than claiming identical automation.

## Safety and evidence

Review commands before approval. Do not share keys, private student data, or
unapproved repository content with external tools. Instructions are guidance,
not enforcement. Prefer local tests over external integrations for the core labs.

Record setup time separately from task time. Freeze model/settings and allow
the same tools in both paths; record unavoidable differences. Reopening an old
conversation or copying a previous solution invalidates an independent run.
Use [the comparison sheet](./assessment.md) to capture the outcome.

## Validate the tutorial starter

From the repository root, run:

```bash
python -m pytest -q tests _docs/tutorials/checks/repair_checks.py _docs/tutorials/checks/materials_checks.py
```

The materials checks validate local tutorial links and prove that the shared
repair checks detect a simulated championship-first regression, without
modifying application files. The repair checks must pass on the unbroken
starter. Record your own output rather than relying on a fixed test count.

Run the feature contract separately:

```bash
python -m pytest -q --tb=short _docs/tutorials/checks/coverage_checks.py
```

On the starter, checks expecting a coverage response and integer-year validation
fail because the coverage route is absent. Missing-file checks can already
receive 404. These expected red checks must not be added to the starter's default
passing application command. After implementing the feature, every feature
check must pass.

The supplied checks are executable Python files named `*_checks.py`, not
`test_*.py`, and are selected explicitly. Do not equate repository-level
validation with the [interactive instructor pilot](./assessment.md#instructor-pilot-checklist).

### Setup troubleshooting

| Symptom | Action |
|---------|--------|
| `venv` fails because `ensurepip` is unavailable | Follow the WSL guide to install the matching Ubuntu venv package, or use an instructor-provided Python installation with venv support |
| `ModuleNotFoundError: httpx` | Activate the intended interpreter and reinstall `requirements.txt`; the dependency is now declared |
| VS Code finds no tests | Run the explicit `python -m pytest` command from the repository root |
| Agent terminal cannot start because of sandbox prerequisites | Report the tool limitation; run the same checks through an approved terminal/task runner, without changing file-access policies |
| Spec Kit workflow is missing | Inspect harness compatibility and customization discovery; use the documented workflow-file fallback and record it |
| Dependency deprecation warnings | Record them separately from test failures; do not make unrelated upgrades during the comparison |
| `test_season_data_caching` fails its wall-clock threshold | Record both timings and rerun that test in isolation before rerunning the suite; do not weaken the assertion or mistake this timing check for deterministic cache evidence |
