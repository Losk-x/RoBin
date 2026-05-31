# AGENTS.md

## Project scope

RoBin is a C++17 benchmark harness for robustness experiments on range indexes, especially updatable learned indexes. Most code changes affect benchmark comparability, hot-path index behavior, or result reproducibility. Prefer small, evidence-backed changes over broad refactors.

## Repository map

- `src/benchmark/` - `microbench` entry point, benchmark driver, workload generation, flag parsing, metrics, and shared utilities.
- `src/competitor/` - index implementations and adapters behind `indexInterface`.
- `src/competitor/indexInterface.h` - common index contract used by the benchmark.
- `src/competitor/partition_interface.h` - partitioned wrapper for selected indexes.
- `run.py` - single-run wrapper that maps high-level benchmark choices to `./build/microbench` flags.
- `reproduce.sh` - full throughput and tail-latency reproduction sweep.
- `run_case_profiling.sh`, `run_all_profiling.sh` - profiling campaigns.
- `script/`, `result/`, `profiling_result/` - notebooks and existing analysis artifacts.
- `datasets/` - generated/downloaded datasets; ignored by git.
- `build/` - local CMake build directory; ignored by git.

## Non-negotiable engineering rules

- Do not change benchmark semantics, dataset handling, workload composition, random seeding, output schemas, or index parameters unless the task explicitly requires it.
- Do not mix performance changes with cleanup. Mention unrelated dead code instead of deleting it.
- Do not add abstractions or configurability unless the current task needs them.
- Preserve comparability with existing result notebooks and CSV consumers.
- Treat hot paths as allocation-sensitive. Avoid heap allocations, string construction, virtual dispatch changes, extra branches, sorting, copying, or synchronization in per-operation paths unless measured and justified.
- Keep profiling-only code under the existing `PROFILING` / `ROOT_PROFILING` gates. Normal benchmark builds must not pay profiling overhead.
- Do not commit generated datasets, local build outputs, perf data, temporary logs, or ad-hoc CSVs unless the task explicitly asks for a checked-in artifact.

## Build and dependencies

Required local dependencies are GCC/G++ >= 11.4, CMake >= 3.14, OpenMP, TBB, jemalloc, MKL, and Boost. The project also uses git submodules.

Standard build from repository root:

```bash
rm -rf build
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
make -j
```

Equivalent project script:

```bash
bash build.sh release
```

Profiling build:

```bash
bash build.sh profiling
```

`build.sh` installs system packages, initializes submodules, deletes `build/`, configures CMake, and builds `microbench`. Use the manual CMake flow when package installation or deleting the existing build directory is not appropriate.

## Dataset and run prerequisites

Prepare datasets with:

```bash
bash prepare.sh
```

This downloads data under `datasets/`, generates derived datasets, and builds Release. Benchmark runs expect binary key files such as `datasets/linear`, `datasets/covid`, `datasets/fb-1`, and `datasets/osm`.

If `/usr/bin/numactl` exists, `run.py` requires a NUMA node binding:

```bash
export numanode=0
```

`run.py` invokes `./build/microbench` from the repository root. Run it from the root, not from `build/`.

## Validation expectations

For any nontrivial code change:

1. Build the affected target (`microbench`) successfully.
2. Run the smallest correctness scenario that exercises the changed path.
3. If the change can affect benchmark output or hot-path performance, run at least one small benchmark sanity run after correctness validation.
4. Record the exact commands and whether datasets were present.

There is no separate unit-test suite in this repository. Use focused `microbench` or `run.py` invocations as behavioral validation.

Example small sanity command, assuming data is prepared and `numanode` is set when needed:

```bash
python3 run.py --index=btree --dataset=linear --concurrency=1 --sampling_method=uniform --bulkload_size=0 --insert_pattern=sorted --taskset=1-1
```

This maps to test suite 21 and produces/updates `out.csv`. Remove or move ad-hoc outputs if they are not part of the deliverable.

Use full reproduction only when explicitly required or when validating a benchmark campaign:

```bash
bash reproduce.sh
```

Profiling sanity:

```bash
bash run_case_profiling.sh
```

`run_all_profiling.sh` is a broad campaign; do not use it as a quick validation substitute.

## Benchmark discipline

- Correctness checks come before benchmarks.
- Do not make performance claims from an uncommitted dirty tree, failed build, missing datasets, or a run that only started.
- For decision-grade benchmark results, tie results to a specific commit, exact command, environment, dataset, and output path.
- Keep NUMA binding, thread count, taskset, dataset, bulkload size, sampling method, insert pattern, and index list explicit in records.
- Preserve existing output columns and meanings unless the task is specifically to change result schema; update all notebooks/scripts that consume changed columns.
- If a long run is required, start it detached only after short validation is green and record the session name, attach command, and expected output paths.

## Research records

For substantial benchmark, performance, or experiment work, create a durable record under:

```text
reports/<module>/<YYYYMMDD>-<slug>.md
```

Use `reports/benchmark/` for benchmark-harness changes unless a narrower module is obvious. Create or update `reports/<module>/README.md` with module context when adding the first record.

Each record should include:

- Goal
- Design
- Validation Method
- Results, with raw artifact paths
- Conclusions and remaining uncertainty

Do not treat a substantial optimization or experiment as complete until its record exists.

## Git, GitHub, branch, and worktree discipline

All nontrivial changes should flow through a feature branch and pull request. Use the current task branch as the PR base unless the user specifies another base; for this repository, `refactor` is the active integration branch for refactor/workflow updates.

Prefer temporary worktrees for independent experiments, benchmark variants, or load-bearing changes that need a clean comparison point. Before creating in-repo worktrees, ensure `.worktrees/` is ignored; add it to `.gitignore` if needed.

Recommended names:

- Branch: `<type>/<scope>-<description>`
- Worktree: `.worktrees/<scope>-<description>`

Use names that encode the affected module or experiment variable. Examples: `fix/benchmark-scan-boundary`, `perf/alex-bulkload-layout`, `docs/agents-git-workflow`.

Use worktrees because they:

- isolate independent experiments and review branches;
- keep the integration branch clean for comparison and rebasing;
- avoid `git stash` juggling;
- give each branch its own build artifacts.

Do not treat dirty-worktree benchmark results as decision-grade evidence. Benchmark committed snapshots when results may influence conclusions.

Before committing or opening a PR:

1. Inspect `git status --short --branch` and preserve unrelated user changes.
2. Stage only files that belong to the task.
3. Verify generated datasets, local build outputs, perf data, temporary logs, and ad-hoc CSVs are not staged unless explicitly requested.
4. Record build, correctness, benchmark, and artifact evidence in the handoff or change record.

## Pull request and review flow

Agents may create branches, commits, and pull requests when asked, but should not merge their own PRs unless the project explicitly allows it.

Once a branch has been pushed or a PR has been opened, preserve review history by adding follow-up commits for fixes. Do not amend or force-push over reviewer-visible history. Reviewers should be able to compare the initial proposal, each review response, and the final state.

PR descriptions should help reviewers reason about the change, not just list files. Use this structure unless a narrower repository template exists:

PR titles and descriptions must be written in English. If the original task is in another language, translate it into English instead of copying it verbatim.

```markdown
## Task Description
<!-- Original task or requirement -->

## What Changed
<!-- What changed at the behavior/design level -->

## Key Design Decisions
- Decision 1: ... because ...
- Decision 2: ... because ...

## Alternatives Considered
<!-- Plausible options that were rejected and why -->

## Test Coverage
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed: <description>

## Known Limitations / Follow-up Tasks
<!-- Current limitations, if any -->

## Review Guidance
<!-- Where reviewers should focus -->
```

For review feedback, prefer small follow-up commits with traceable messages. Rebase or squash only before reviewer-visible history exists, or when the repository maintainer explicitly requests it.

## Commit message convention

Use a conventional, traceable commit format:

```text
<type>(<scope>): <imperative summary>

<body: background and motivation for this change>

Agent-Task: <original task description or task ID>
Agent-Model: <model used, if applicable>
Agent-Decision: <key design decisions and rationale>
Agent-Limitation: <known limitations or "none">
```

Common types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `ci`, `chore`.

Use a scope that names the affected module or workflow area. Multi-scope commits should be rare; when needed, separate scopes with `/`.

## C++ style and implementation guidance

- Match nearby style. This codebase uses C++17, header-heavy templates, explicit pointers, existing macros, and mixed 2-space/legacy indentation depending on file.
- Keep adapters conforming exactly to `indexInterface<KEY_TYPE, PAYLOAD_TYPE>`: `bulk_load`, `get`, `put`, `update`, `remove`, `scan`, `init`, `memory_consumption`, and profiling hooks under `PROFILING`.
- Preserve `Param` behavior and fields when plumbing benchmark context into competitors.
- Avoid changing third-party competitor implementations unless required; adapter-level fixes are preferred when they preserve upstream behavior.
- Be careful with sentinel keys. The README notes that Face data is shifted to `fb-1` because some indexes use `numeric_limits<uint64_t>` as a sentinel.
- Maintain existing random seeds and deterministic workload generation unless the task is explicitly about randomness or methodology.
- Avoid exceptions in hot benchmark paths; existing code generally uses return codes, `assert`, `INVARIANT`, and process exit.
- When adding includes, prefer the minimal include in the file that uses it. Remove includes made unused by your change.

## Python and shell guidance

- `run.py` is part of the benchmark contract. Changes to argument choices or command construction can invalidate reproduction scripts and notebooks; update all callers together.
- Keep shell scripts reproducible and explicit about output locations.
- Avoid relying on interactive shell state except documented environment such as `numanode`.
- Do not silently swallow failed benchmark commands; existing scripts record failed cases in result logs.

## Output and artifact conventions

- `out.csv` is the default benchmark output and is ignored by git.
- `result/` and `profiling_result/` contain checked-in notebooks and/or analysis artifacts; do not overwrite them accidentally during ad-hoc validation.
- Full reproduction scripts move generated CSVs into `result/`.
- Profiling scripts write logs under `log/` or profiling-specific paths; keep these out of commits unless explicitly requested.

## Review handoff

When handing off a change, include:

- What changed at the behavior/design level.
- Build command and result.
- Correctness command(s) and result.
- Benchmark sanity command(s), result, and output paths, if relevant.
- Commands not run, with the concrete reason.
- Any long-running benchmark status, session name, attach command, and expected outputs.
