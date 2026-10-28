# Comparison evidence and instructor guide

Assess working software and student judgement, not prompt length, document
volume, task checkboxes, or an agent's confidence.

## Comparison sheet

Copy this table into your submission for each lab. Use "not available" for
metrics your account does not expose; do not invent token or cost figures.

| Evidence | Path A: Copilot-native | Path B: Copilot + Spec Kit |
|----------|------------------------|---------------------------|
| Baseline commit and exercise checkpoint | | |
| OS, Python and resolved dependency versions | | |
| VS Code, harness, model, date, access/policy limits | | |
| Active instructions, skills, agents and tool permissions | | |
| Setup time (separate) and active task time | | |
| Planning, implementation and review time | | |
| Acceptance results: pass/fail counts and command output | | |
| Existing suite result and warnings | | |
| Feature browser checklist evidence, if applicable | | |
| Missed requirements and regressions found | | |
| Rework: substantive correction cycles and why | | |
| Human interventions and rejected suggestions | | |
| Artifacts created, maintained, useful or redundant | | |
| Exposed usage/cost and how it was measured | | |
| Unresolved risks or incomplete work | | |

A correction cycle means a new request to repair an unmet requirement or
regression, not every conversational turn. Report wall-clock time and active
time separately when waiting materially affects results.

## Required student reflection

Write a short decision record answering:

1. What did you verify independently rather than trusting Copilot?
2. Quote or summarize one incorrect or unnecessary suggestion you rejected.
   If none occurred, challenge an assumption with a counterexample and record
   the response; do not fabricate an error.
3. Which requirement was most likely to be missed? What caught it?
4. Which workflow would you choose for a small fix, an uncertain cross-layer
   change, and a team handover? Explain the trade-offs.
5. What would change your choice? Suggest a hybrid workflow if justified.

Submit code diffs, your own tests, execution evidence, relevant plans/specs,
and the decision record. Redact secrets and personal information from logs;
you do not need to publish entire conversations.

## Rubric (100 points, identical for both paths)

| Area | Points | Full-credit evidence |
|------|--------|----------------------|
| Correctness and compatibility | 35 | Meets shared acceptance criteria, preserves existing contracts and tests |
| Verification quality | 25 | Red-to-green evidence, meaningful student regression tests, negatives, feature browser checks |
| Human judgement | 25 | Challenges assumptions, reviews diffs, rejects or improves suggestions with reasons |
| Workflow evaluation | 15 | Honest measurements, useful artifacts, reasoned recommendation and limitations |

Do not award correctness points for skipped checks or a fabricated green report.
More artifacts do not automatically earn more points. When a feature remains
incomplete at the time limit, assess the recorded evidence and explicitly mark
the unmet criteria.

## Instructor pilot checklist

Before teaching:

- [ ] Publish a clean course revision/tag containing these materials and record
      its full commit. Do not publish completed feature solutions in the starter.
- [ ] Install requirements in a fresh environment and capture the application
      test baseline. A previously working local `.venv` is not a clean-install test.
- [ ] Complete the capability/access matrix in [setup](./setup.md). Record the
      actually tested versions rather than advertising unspecified "latest" support.
- [ ] Confirm shared instructions load in both paths and Spec Kit discovery is
      disabled in native worktrees, including user/plugin sources.
- [ ] Check that the supplied Spec Kit workflows run in the selected harness;
      pilot any fallback explicitly. Do not silently upgrade existing templates.
- [ ] Seed the repair identically in both repair worktrees. Confirm the
      acceptance checks fail for the intended routing error, not missing packages.
- [ ] Confirm repair checks pass on the unbroken starter, and the feature
      checks fail because the feature is not implemented.
- [ ] Pilot both complete workflows, including a feature implementation and
      browser checks, on disposable instructor branches. Keep answer branches
      separate from student starters.
- [ ] Trial timing with at least one learner; adjust the estimated schedule.
- [ ] Alternate or randomize path order across pairs. Ask students not to copy
      solutions between runs; a second attempt still has unavoidable familiarity.
- [ ] Check network/account restrictions and usage budgets. Have manual test
      commands and the standalone debugging workshop available as fallbacks.

After teaching:

- [ ] Compare correctness before speed or usage.
- [ ] Separate setup overhead, task work and review effort.
- [ ] Discuss why sample data, passing tests, and fluent explanations can mislead.
- [ ] Record access failures and incomplete criteria, not just successful demos.
- [ ] Collect anonymized observations with appropriate consent.
- [ ] Update versions, timing and troubleshooting before the next class.

**Pilot status:** repository-level checks can validate the starter and supplied
contracts, but no classroom trial, student timing study, account entitlement
test, or end-to-end interactive Copilot/Spec Kit teaching session is claimed
by these materials. Complete the checklist before describing the course as
classroom-validated.

## Optional advanced sessions

Keep these outside the initial scored comparison:

- Delegate a bounded task to Copilot's cloud agent and compare environment setup,
  latency, permissions, usage, and human review with local execution.
- Request Copilot code review on a PR, verify each finding, and explain one
  accepted or rejected recommendation. AI review does not replace human review.
- Add one useful instruction, skill, or tool-limited custom agent after observing
  repeated rework; demonstrate that the selected harness loads it.
- Connect an approved MCP server for a specific need. Explain the trust boundary,
  external data exposure and minimum permissions before enabling it.
- Compare independent worktree sessions on non-overlapping tasks; measure
  coordination and merge overhead rather than assuming parallelism is free.
- Investigate hooks or plugins only after checking current availability and
  organizational policy. Keep preview features optional.

Refer to [the dated capability matrix and official sources](./setup.md#capability-and-access-check).
Small classroom comparisons are observations, not proof that one workflow is
universally superior.
