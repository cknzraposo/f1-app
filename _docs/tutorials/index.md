<div class="race-hero" markdown="1">
<div class="hero-copy" markdown="1">

<span class="eyebrow">GITHUB COPILOT / HANDS-ON WORKSHOP</span>

# Build fast.<br><span>Think for yourself.</span>

AI is your co-driver. You're the engineer. Go from local setup to AI-assisted
coding and agent-led development on a real Formula 1 project. Compare the
workflows, challenge the output, and keep judgement in the driver's seat.

[Start the workshop &rarr;](./setup.md) [Explore the workflows](#two-paths-one-finish-line)

</div>
<div class="hero-visual" markdown="1">

![An original top-down race car illustration on an imaginary learning circuit](./assets/racecar.svg)

<div class="telemetry"><span></span><span>MODE: HANDS-ON</span><span>DRIVER: YOU</span></div>

</div>
</div>

<div class="session-stats">
  <div><strong>02</strong><span>WORKFLOWS TO COMPARE</span></div>
  <div><strong>02</strong><span>REAL-WORLD LABS</span></div>
  <div><strong>~5 hrs</strong><span>LABS + COMPARISON</span></div>
  <div><strong>01</strong><span>ENGINEER IN CONTROL</span></div>
</div>

<p class="section-label">THE BRIEF / A NEW WAY TO BUILD</p>

## Learn the tools. Own the decisions.

<div class="section-intro" markdown="1">

New to the environment? Choose [native Windows or macOS](./native-setup.md),
or [Windows with WSL](./wsl-setup.md). WSL is optional, not a workshop requirement.
Then explore [AI-assisted versus AI-native development](./ai-development.md):
when to ask for a focused suggestion, when to delegate a bounded task, and what
you still need to understand, test, and review.

Working style and workflow structure are different choices. You can use
developer-led assistance or agent-led execution with **either** path below.
Allow extra time for onboarding and the AI orientation.

</div>

<p class="section-label">01 / PICK YOUR RACING LINE</p>

## Two paths. One finish line.

<p class="section-intro">The same F1 application. The same requirements. Two ways
to work with Copilot. Find out how much process your task actually needs,
instead of assuming that faster or more structured is always better.</p>

<div class="path-grid" markdown="1">
<div class="path-card" markdown="1">

<span class="lane-label">PATH A / THE QUICK LINE</span>

### Copilot-native

Go from a clear brief to a reviewed plan, scoped changes, and working tests.
Keep the process lightweight, with human approval at the important moments.

<span class="workflow-line">Explore &rarr; Plan &rarr; Approve<br>Implement &rarr; Verify</span>

Best question to ask: **How much structure is enough?**

[Take the Copilot-native path &rarr;](./copilot-native.md)

</div>
<div class="path-card strategy" markdown="1">

<span class="lane-label">PATH B / THE STRATEGY LINE</span>

### Copilot + Spec Kit

Make the requirements explicit. Work through specifications, contracts,
and tasks before implementation, then check whether the extra structure paid off.

<span class="workflow-line">Specify &rarr; Clarify &rarr; Plan<br>Tasks &rarr; Implement &rarr; Verify</span>

Best question to ask: **When does structure earn its keep?**

[Take the Spec Kit path &rarr;](./copilot-spec-kit.md)

</div>
</div>

<p class="section-label">02 / FROM THE PIT LANE TO THE FINISH</p>

## Your weekend on the grid.

<p class="section-intro">Get the project running, test both approaches on the same
challenges, then make a decision backed by evidence. No blind acceptance.
No points for generating more code.</p>

<div class="race-plan" markdown="1">
<div class="race-stage" markdown="1">

<span class="stage-number">01 / THE PIT LANE</span>

### Get race-ready.

Start with [native Windows or macOS](./native-setup.md),
[Windows + WSL](./wsl-setup.md), or shared project setup. Run the app,
connect Copilot, and record a passing baseline before edits.

[Set up your environment &rarr;](./setup.md)

</div>
<div class="race-stage" markdown="1">

<span class="stage-number">02 / THE SPRINT</span>

### Find the wrong turn.

A request succeeds but returns the wrong data. Repair the query parser,
challenge an AI suggestion, and prove the fix with a regression test.

[Enter the repair lab &rarr;](./repair-lab.md)

</div>
<div class="race-stage" markdown="1">

<span class="stage-number">03 / THE GRAND PRIX</span>

### Build. Test. Defend.

Add a data-coverage feature across the API and UI. Compare review effort,
rework, and correctness across both paths.

[Enter the feature lab &rarr;](./feature-lab.md)

</div>
</div>

Repeat the labs on the other path from an independent baseline, then
[compare your evidence and reflect](./assessment.md). The paths are alternatives
to evaluate, not sequential implementation steps. Short on time? Start with
setup and the paired repair lab.

<div class="pit-note" markdown="1">
<span class="pit-icon" aria-hidden="true">i</span>
<div markdown="1">

### The workshop is online. Your F1 app runs locally.

GitHub Pages serves this tutorial; run FastAPI locally using the setup guide.
You'll need basic Python, Git, Python 3.12+, VS Code, and suitable Copilot access.
No runtime LLM, API keys, database, or frontend bundler is required for the labs.
The checked-in season files are samples, not verified complete seasons.

</div>
</div>

## In the instructor's garage.

Use the [assessment rubric and pilot checklist](./assessment.md) to teach the
workshop. Timing is an estimate, so complete an instructor pilot before class.
The [publishing walkthrough](./publishing.md) explains how to deploy your own copy.
The [source repository](https://github.com/cknzraposo/f1-app) retains the original
Spec Kit showcase and standalone debugging lessons.
