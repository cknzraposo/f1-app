# Native Windows and macOS: no WSL required

**WSL is optional.** The F1 application and tutorial site can be run with native
Python and Git. On a Mac, use macOS directly: WSL is a Windows feature, not
something you need to install or emulate.

| Your environment | Start here |
|------------------|------------|
| Windows without WSL, including a device where WSL is blocked | [Native Windows: PowerShell](#native-windows-powershell) |
| macOS, on Apple Silicon or Intel | [macOS: Terminal](#macos-terminal) |
| Windows with an approved WSL installation | [Windows + WSL guide](./wsl-setup.md) |
| Linux with Python 3.12+ and Git | [Shared project setup](./setup.md) |

Use an instructor-approved, supported Python **3.12 or newer**. The steps below
do not require a database, a runtime LLM, Docker, or a Linux virtual machine.
If you cannot install development tools, ask for an approved managed environment
rather than bypassing device policy.

## Native Windows: PowerShell

### 1. Install the tools

Install Python from [python.org](https://www.python.org/downloads/),
[Git for Windows](https://gitforwindows.org/), and
[VS Code for Windows](https://code.visualstudio.com/). Follow your organization's
approved installation process. Git for Windows also provides Git Bash, which
is useful for the optional Bash-based workflow helpers described below.

Open a **new PowerShell terminal** after installation:

```powershell
py -3 --version
git --version
```

Confirm Python is at least 3.12. If `py` is not available but `python --version`
reports the correct installed Python, use `python` instead of `py -3` for the
environment-creation command below. With multiple Python versions installed,
select the instructor's version explicitly, for example `py -3.12`.

### 2. Clone and create a Windows virtual environment

Run in **PowerShell**, not Git Bash or a WSL terminal:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\projects" | Out-Null
Set-Location "$HOME\projects"
git clone https://github.com/cknzraposo/f1-app.git
Set-Location f1-app
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

The interpreter should be inside this checkout's `.venv\Scripts` directory.
Clone your own fork instead if you need to push student work to GitHub.
Prefer a local development folder over a network drive or synchronized folder.

These commands deliberately call the environment's Python directly.
**Activation is not required**, and a blocked `Activate.ps1` does not stop you.
Do not weaken PowerShell execution policy just to activate the environment.

### 3. Run tests and the application

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
git rev-parse HEAD
git status --short
.\.venv\Scripts\python.exe -m uvicorn app.api_server:app --reload --host 127.0.0.1 --port 8000
```

Record the test result before starting the server. If any command fails, resolve
that failure before continuing. Keep the server running and open a second
PowerShell terminal for the health check:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

The returned object's `status` property should be `healthy`. Use the PowerShell
cmdlet here rather than assuming `curl` has the same behavior in every Windows
shell.

Open `http://localhost:8000/static/index.html` and
`http://localhost:8000/docs` in your browser. Ask the UI
**"who won the most races in 2023"** and check that it returns race winners.
Stop the server with Ctrl+C.

### 4. Preview the tutorial website, if needed

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-pages.txt
.\.venv\Scripts\python.exe -m mkdocs serve --dev-addr 127.0.0.1:8001
```

Open the address printed by MkDocs, normally
`http://localhost:8001/f1-app/`. The tutorial website and FastAPI application
are separate servers. Stop the preview with Ctrl+C.

For lab commands written as `python -m ...`, use
`.\.venv\Scripts\python.exe -m ...` in PowerShell unless you have deliberately
activated this environment. A WSL environment's `.venv/bin/python` is not a
Windows interpreter.

## macOS: Terminal

### 1. Install native tools

Install a supported Python 3.12+ from
[Python's macOS downloads](https://www.python.org/downloads/macos/), or use an
instructor-approved package manager installation. Current python.org universal2
installers support both Apple Silicon and Intel; choose a release compatible
with your macOS version. Do not replace macOS-managed Python or use `sudo pip`.

Install [VS Code for macOS](https://code.visualstudio.com/docs/setup/mac).
Then open Terminal and check:

```bash
python3 --version
git --version
```

If Git is missing, use the macOS Command Line Tools installation prompt or your
approved Git installation process. If `python3` selects an older system Python,
select the newly installed interpreter before creating the virtual environment.

### 2. Clone and create the environment

The following commands work in the usual macOS zsh terminal as well as Bash:

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/cknzraposo/f1-app.git
cd f1-app
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import sys; print(sys.executable)"
```

The interpreter should be inside this checkout's `.venv/bin` directory. Clone
your own fork if you plan to push changes. Activate this environment again in
each new terminal that runs Python commands:

```bash
cd ~/projects/f1-app
source .venv/bin/activate
```

### 3. Run tests and the application

```bash
python -m pytest -q tests
git rev-parse HEAD
git status --short
python -m uvicorn app.api_server:app --reload --host 127.0.0.1 --port 8000
```

Record and resolve baseline failures before starting the server. Keep that
terminal running, then check from a second Terminal window:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Expect `{"status":"healthy"}`. Open `http://localhost:8000/static/index.html`
and `http://localhost:8000/docs`, and try the same race-winners question as in
the Windows instructions. Stop the server with Ctrl+C.

### 4. Preview the tutorial website, if needed

With the virtual environment activated:

```bash
python -m pip install -r requirements-pages.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8001
```

Open the printed address, normally `http://localhost:8001/f1-app/`.
No WSL extension or Linux VM is needed.

## Shared editor and Copilot setup

1. Open the repository as a **local folder** in VS Code, using **File > Open
   Folder** or `code .`. Do not reopen it in WSL for these native instructions.
2. Enable the Python and Pylance extensions. In **Python: Select Interpreter**,
   select `.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS.
3. If `code` is unavailable, opening the folder through the UI is sufficient.
   On macOS, the Command Palette's **Shell Command** entry can add `code` to
   PATH; installing Copilot CLI is optional.
4. Enable Copilot, sign in with suitable access, and check the
   [capability matrix](./setup.md#capability-and-access-check).
5. Ask it to explain the query request path without editing anything. Check one
   cited file yourself before delegating work.

The Python interpreter, terminal shell, and Copilot harness are separate choices.
Tell the agent **"This is native Windows PowerShell; use the Windows .venv
interpreter"** or **"This is native macOS; use this checkout's .venv"**.
Review its actual commands, not just its stated intention.

## Bash-based Spec Kit helpers

The app and Copilot-native exercises do not require Bash. However, this checkout
contains [Bash helpers](../../.specify/scripts/bash) used by its checked-in Spec
Kit workflows. It does **not** contain equivalent PowerShell helper scripts.
Do not paste `.sh` script contents into PowerShell or run Bash scripts with `sh`.

- **Native Windows:** if permitted, select **Git Bash** as the VS Code terminal
  profile for those helpers. Git Bash is a native Windows shell, not WSL.
  Keep the Windows checkout and Windows virtual environment; use
  `./.venv/Scripts/python.exe` for Python commands in Git Bash.
- **macOS:** run Bash helpers explicitly with `bash`, even if your interactive
  shell is zsh. Check that the installed Bash is compatible with the workflow.
- **Either platform:** check the selected agent's terminal/runtime too; changing
  your visible terminal profile does not guarantee every agent tool uses it.

From the repository root in the appropriate **Bash** terminal, this read-only
help command checks that you can launch a helper:

```bash
bash .specify/scripts/bash/check-prerequisites.sh --help
```

This is not proof that the complete automated workflow works on your machine.
Resolve shell/path errors before proceeding. Do not reinitialize the repository
with a newer Spec Kit release just to hide a compatibility problem.

### If Bash is also unavailable

Use a **manual, template-based Spec Kit variant**, rather than claiming that
the automated commands ran:

1. Inspect existing branches and spec folders; choose an unused three-digit
   feature prefix and short name. Create the feature branch with Git/VS Code.
2. In VS Code, copy the [spec](../../.specify/templates/spec-template.md),
   [plan](../../.specify/templates/plan-template.md), and
   [task](../../.specify/templates/tasks-template.md) templates into a new
   feature directory under `specs/`. Do not overwrite the historical feature.
3. Follow the [Spec Kit path](./copilot-spec-kit.md): specify and clarify, review
   the constitution and plan, then break work into tasks. Tell Copilot explicitly
   not to invoke Bash helpers.
4. Drive implementation yourself or delegate approved tasks with native commands.
   Run the same acceptance checks and review the resulting diff.
5. Label the run **manual Spec Kit variant** in your comparison record. Record
   the tooling difference rather than treating it as identical automation.

This keeps both learning approaches available without requiring WSL or
circumventing installation restrictions.

## PowerShell equivalents for the comparison

The [shared comparison setup](./setup.md) shows Bash examples. These equivalents
let native Windows users prepare independent runs without WSL. Run each step
from the expected checkout and stop if it reports an error.

### Create independent worktrees

From a clean, published tutorial revision:

```powershell
$BASE = git rev-parse HEAD
git worktree add -b tutorial/repair-native ../f1-repair-native "$BASE"
git worktree add -b tutorial/repair-speckit ../f1-repair-speckit "$BASE"
git worktree add -b tutorial/feature-native ../f1-feature-native "$BASE"
git worktree add -b tutorial/feature-speckit ../f1-feature-speckit "$BASE"
```

Open each worktree in its own VS Code window. Create a separate Windows `.venv`
there with `py -3 -m venv .venv`, install the same requirements, and select its
interpreter. Do not copy virtual environments between operating systems.

### Isolate Spec Kit discovery in Path A

Run **only inside each Copilot-native exercise worktree**:

```powershell
New-Item -ItemType Directory -Force -Path ".tutorial-disabled/agents", ".tutorial-disabled/skills" | Out-Null
Move-Item -Path .github/agents/speckit.*.agent.md -Destination .tutorial-disabled/agents/
Move-Item -Path .github/skills/speckit-* -Destination .tutorial-disabled/skills/
git add -- .github/agents .github/skills .tutorial-disabled
git commit -m "Isolate Spec Kit workflows for the native tutorial"
```

If no files match, inspect the checkout; do not ignore the error. Keep shared
project instructions unchanged and also disable user/plugin Spec Kit sources
as described in the shared setup. Here **Copilot-native** names a process,
not the Windows operating system.

## Troubleshooting

| Problem | What to do |
|---------|------------|
| `py` or `python3` is missing or selects the wrong release | Recheck the approved Python installation and selected version before creating `.venv` |
| PowerShell blocks `Activate.ps1` | Use `.\.venv\Scripts\python.exe` directly; activation and execution-policy changes are unnecessary |
| `bash` is unavailable on Windows | The app still runs in PowerShell; use approved Git Bash for helpers or the manual Spec Kit variant |
| A command expects `.venv/bin/python` on native Windows | Replace it with the Windows interpreter path; do not mix WSL and Windows environments |
| An Apple Silicon installation reports architecture/import errors | Check that the interpreter and installed packages match the intended architecture; recreate the project environment with the correct interpreter |
| Packages fail to install on a chosen Python release | Check dependency compatibility and use the instructor's supported version; do not silently change pinned dependencies |
| HTTPS/certificate errors occur during installation | Use the installer's certificate setup or the organization's approved CA configuration; do not disable certificate verification |
| Tests or the UI cannot find local data | Run from the repository root, not from `app/` or a different checkout |
| Port 8000 or 8001 is busy | Stop your previous process or choose another port and update the browser URL |

Next: read [AI-assisted versus AI-native development](./ai-development.md),
then continue with [shared comparison setup](./setup.md). The same acceptance
criteria and human-review standards apply on every platform.

References: [Python on Windows](https://docs.python.org/3/using/windows.html),
[Python on macOS](https://docs.python.org/3/using/mac.html), and
[VS Code on macOS](https://code.visualstudio.com/docs/setup/mac).
