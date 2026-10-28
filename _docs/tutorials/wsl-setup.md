# Get race-ready: Windows, WSL, and VS Code

Start here if you are setting up this project on Windows for the first time.
You will finish with the F1 app running in Linux, VS Code connected to that
environment, and Copilot ready to help you develop it.

Already on Linux or macOS? Use the [shared project setup](./setup.md).
WSL is a Windows development environment, not an AI prerequisite.

You need a WSL-compatible, supported Windows environment, permission to install
development tools, and internet access for downloads and Copilot. Check
[Microsoft's WSL requirements](https://learn.microsoft.com/en-us/windows/wsl/install)
if you use an older or managed Windows installation.

## What runs where?

| Windows | Ubuntu inside WSL |
|---------|-------------------|
| VS Code desktop application and browser | Git checkout, Python environment, tests, and FastAPI |
| WSL installation and management commands | Linux terminal commands and project development |
| GitHub account sign-in through VS Code | Workspace tools used by the connected editor/agent |

Keep the repository and Python interpreter in the same environment. Opening
Linux files in a Windows-only editor session or selecting Windows Python for a
WSL checkout is a common source of confusing failures.

## 1. Install WSL and Ubuntu

**Run in Windows PowerShell as Administrator**, not in a Linux terminal:

```powershell
wsl --install
```

Restart Windows if requested. Open **Ubuntu** from the Start menu and create
your Linux username and password. This is separate from your GitHub account.
When Linux asks for a password, the terminal does not display characters as
you type.

Back in **Windows PowerShell**, check the installed distribution:

```powershell
wsl --list --verbose
```

Use WSL 2 for the workshop. If no Ubuntu distribution is installed, list the
available distributions and install one by its exact displayed name:

```powershell
wsl --list --online
wsl --install -d Ubuntu
```

For an existing WSL 1 installation, consult the
[official WSL installation and conversion instructions](https://learn.microsoft.com/en-us/windows/wsl/install)
before changing it. On a managed computer, have your administrator approve
WSL and virtualization rather than working around organization policy.

**Checkpoint:** Ubuntu opens successfully and the distribution list shows WSL 2.

## 2. Install the Linux development tools

**Run the remaining Bash commands in Ubuntu**, unless a step says otherwise:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl
python3 --version
git --version
```

Use Python **3.12 or newer**. If your Ubuntu release provides an older version,
use an instructor-approved newer Ubuntu/Python installation. Do not replace
Ubuntu's system Python or install project packages with `sudo pip`.

These are deliberate OS setup steps for you to review. Giving an AI agent
permission to edit project files is not permission to change your operating
system.

## 3. Clone into the Linux filesystem

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/cknzraposo/f1-app.git
cd f1-app
pwd
```

The path should look like `/home/YOUR-USER/projects/f1-app`. Prefer the Linux
filesystem for Linux tooling rather than a checkout under `/mnt/c/...`.

The public repository can be cloned without write access. If you want to push
your own work or publish a student site, fork the repository on GitHub first
and substitute **your fork's clone URL**. Copilot sign-in does not automatically
grant permission to push to the upstream repository.

## 4. Create an isolated Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -c "import sys; print(sys.executable)"
```

The interpreter path should end with `f1-app/.venv/bin/python`, not a Windows
`.exe` or an unrelated Python installation.

Activate this environment again in every new terminal:

```bash
cd ~/projects/f1-app
source .venv/bin/activate
```

If you cloned into a different directory, use that path instead.

## 5. Connect VS Code to WSL

1. Install [VS Code for Windows](https://code.visualstudio.com/), including its
   **Add to PATH** option.
2. In VS Code, install Microsoft's
   [WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl).
3. From the Ubuntu terminal, inside the repository, run:

   ```bash
   code .
   ```

4. Confirm the editor's remote indicator says **WSL: Ubuntu** or your chosen
   distribution. A normal Windows window is not the same environment.
5. In that window, install/enable the Python and Pylance extensions where VS Code
   requests them. Use **Python: Select Interpreter** and choose `.venv/bin/python`.
6. Open a new integrated terminal. Check `pwd` and the interpreter command from
   the previous step; activate `.venv` if necessary.

VS Code stays on Windows while its workspace server and development tools run
in WSL. Do not install a second Linux desktop copy of VS Code to achieve this.

## 6. Establish a working app before involving AI

From the activated environment at the repository root:

```bash
python -m pytest -q tests
git rev-parse HEAD
git status --short
```

Record your test result and starting commit. Do not copy a test count from
someone else's machine or ask Copilot to change assertions until a baseline
failure disappears. Understand and resolve setup errors first.

Start the API:

```bash
python -m uvicorn app.api_server:app --reload --host 127.0.0.1 --port 8000
```

Keep that terminal running. Open a **second Ubuntu terminal**, then check:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"healthy"}
```

In your Windows browser, open:

| Address | Check |
|---------|-------|
| `http://localhost:8000/static/index.html` | The F1 query interface loads |
| `http://localhost:8000/docs` | FastAPI's interactive endpoint documentation loads |
| `http://localhost:8000/api/seasons/2023` | The local Ergast-format JSON is returned |

Ask the UI **"who won the most races in 2023"** and check that it shows race
winners, not championship standings. The bundled records are local samples;
the purpose is to verify the app, not infer official full-season statistics.
Stop the server with Ctrl+C when finished.

## 7. Make Copilot useful in the correct workspace

1. In the WSL-connected VS Code window, enable GitHub Copilot and sign in with
   an account that has appropriate access under your organization's policy.
2. Confirm you can open Copilot Chat. Model/tool availability depends on your
   plan, settings, and selected agent harness; use the
   [capability check](./setup.md#capability-and-access-check).
3. Start with a read-only request:

   > Explain how "who won the most races in 2023" travels from the browser to
   > the API, query parser, and JSON data. Cite the actual files and functions.
   > Do not edit files or install anything.

4. Open at least one cited file and confirm the explanation matches the code.
5. Before allowing edits, read the
   [AI-assisted versus AI-native guide](./ai-development.md). Review individual
   tool requests; do not enable blanket terminal approval.

Copilot for development and the app's optional Ollama/Azure integration are
different things. Neither runtime model service is required for this workshop.

## 8. Preview the tutorial website, if needed

The application and documentation have separate dependency files and servers:

```bash
python -m pip install -r requirements-pages.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8001
```

Open the address printed by MkDocs, normally
`http://localhost:8001/f1-app/`. Port 8001 leaves port 8000 available for FastAPI.
GitHub Pages hosts the built tutorial only; it cannot run the Python API.

## Troubleshooting

| Symptom | What to check |
|---------|---------------|
| `wsl --install` shows help or no distribution is available | In PowerShell, check the installed/online distribution lists and Microsoft's WSL installation guide |
| WSL cannot start because virtualization is unavailable | Follow Microsoft's troubleshooting guidance or ask the device administrator; do not disable security controls |
| `code: command not found` | Check the Windows VS Code installation's PATH option and restart the terminal; alternatively use **WSL: Connect to WSL** in VS Code |
| VS Code shows a Windows interpreter | Reopen the folder in WSL and select the Linux `.venv/bin/python` |
| `venv` reports missing `ensurepip` | Ensure the matching Ubuntu venv package is installed, or use an instructor-provided interpreter |
| An import is missing | Activate the intended `.venv` and install the repository's requirements there |
| `Address already in use` | Stop your previous server or choose another port and update the browser URL |
| Windows cannot open localhost but the WSL `curl` check succeeds | Check WSL networking, port forwarding, firewall, and organization policy; do not expose the server publicly as a workaround |
| Git cannot push your changes | Check your fork's remote and approved Git authentication; cloning a public repository and signing into Copilot do not grant upstream write access |

## Ready-to-develop checklist

- [ ] Repository and `.venv` are inside WSL.
- [ ] VS Code is connected to that WSL distribution.
- [ ] Tests run using the selected Linux interpreter.
- [ ] The health endpoint, UI, and API docs work.
- [ ] Copilot can explain a request path without changing files.
- [ ] You can distinguish developer tools from the app's runtime dependencies.

Next: read [what changes with AI development](./ai-development.md), then use
the [shared comparison setup](./setup.md) before starting a lab.

References: [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install)
and [VS Code development in WSL](https://code.visualstudio.com/docs/remote/wsl).
