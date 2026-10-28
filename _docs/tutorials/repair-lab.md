# Shared lab 1: a successful request with the wrong answer

Use this brief unchanged for [Path A](./copilot-native.md) and
[Path B](./copilot-spec-kit.md). Budget 35 minutes per path, excluding setup.

## Problem and acceptance criteria

A user asks "who won the most races in 2023", receives HTTP 200, but sees
championship standings instead of race winners.

Your change must:

1. Route that question and case/whitespace variants to
   `/api/seasons/2023/winners` using the keyword parser.
2. Keep "who won the 2010 championship" routed to standings.
3. Keep "2023 standings" working.
4. Preserve the query response envelope and correct `dataType`, not just HTTP 200.
5. Continue rejecting empty queries with HTTP 400.
6. Add a student-written regression test and pass the existing application tests
   without requiring runtime LLM access.

Do not delete valid championship keywords just to silence the symptom. Alternative
solutions are welcome if they satisfy the full behavior contract.

## Seed the same regression in both repair worktrees

The published application is already fixed. Before timing the exercise, change
only the first two rule blocks in `QueryParser.parse()` in
[query_parser.py](../../app/query_parser.py). Put the championship block first:

```python
        result = self._parse_championship_query(query_lower)
        if result:
            return result

        result = self._parse_race_winners_query(query_lower)
        if result:
            return result
```

Leave every other rule and helper unchanged. Review the diff, then checkpoint
the seeded state:

```bash
git diff -- app/query_parser.py
git add app/query_parser.py
git commit -m "Seed parser priority regression for tutorial repair lab"
python -m pytest -q _docs/tutorials/checks/repair_checks.py
```

**Expected: failing checks for race winners**, while championship and standings
checks still pass. If everything passes, the bug was not seeded. If imports or
fixture setup fail, fix the environment before starting the timer.

The checks inject tiny deterministic API responses, so they assess routing,
not whether the sample season happens to reproduce official championship totals.
Record the failing test names and actual `dataType`.

## Complete the selected workflow

Give the problem and acceptance criteria to Copilot. Follow the selected path's
exploration, planning, human approval, implementation and review stages.
The [older debugging lesson](../student-guide.md#lesson-2--give-overlapping-patterns-an-explicit-priority-order)
explains the solution, so leave it closed during the independent scored run.
This lab is a workflow comparison, not a hidden-answer examination.

## Verify

```bash
python -m pytest -q _docs/tutorials/checks/repair_checks.py
python -m pytest -q tests/integration/test_query_parsing.py tests/contract/test_query.py
python -m pytest -q tests
git diff --stat
git diff
```

In the browser, submit the winners question and a championship question. Confirm
that the displayed content matches each question. API acceptance checks alone
do not establish rendering correctness.

Record which rules overlap, why the chosen fix preserves existing queries, and
one AI suggestion you challenged. Complete [the comparison sheet](./assessment.md).

## Recovery

Keep the seeded commit as the repair baseline. Do not run broad reset commands
or discard unrelated work. If you want another attempt, create a new branch
from the recorded seeded commit in a new worktree. Only restore an individual
file after checking its diff and confirming that its uncommitted changes are
disposable. Do not carry your first solution into the other path.
