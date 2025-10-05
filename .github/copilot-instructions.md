<!-- .github/copilot-instructions.md
     Purpose: concise, actionable guidance for AI coding agents working on this repo.
-->

# Guidance for AI coding agents — dissertation repo

Focus: make targeted code changes and suggestions that respect this repository's architecture and developer workflows.

- Big picture

  - This repository contains experiments and O-RAN xApps used to collect KPM metrics and run network experiments. Primary components:
    - xApps (Python): `detector_xapp.py`, `kpm5_xapp.py` and supporting library in `openran/oran-sc-ric/xApps/python/lib/` (notably `xAppBase.py` and `e2sm_kpm_module.py`). These use the RMR/RIC runner and E2SM-KPM message formats.
    - RIC platform: `openran/oran-sc-ric/` contains docker compose for the Near-RT RIC (python_xapp_runner, submgr, appmgr, etc.). Use `docker compose up` from that directory to start the platform.
    - Experiment automation: `run_enhanced.sh` orchestrates experiments (Docker stacks, gNB, UEs, GNU Radio scenarios, iPerf, metrics collection) and expects repo-local paths and a structured `BASE_EXP_DIR` with per-experiment folders.

- Key workflows (how developers run and test code)

  - Start RIC and run xApps: cd `openran/oran-sc-ric` then `docker compose up` (or `docker compose exec python_xapp_runner ./your_xapp.py` to run xApps). The xApps directory is mounted into the container for live edits.
  - Run experiments: `run_enhanced.sh` is the orchestrator. It relies on absolute paths configured near the top (CSV_FILE, GNB_CONF, UE_CONF, BASE_EXP_DIR). Avoid hardcoding changes — prefer parameterizing via script args or env vars.
  - Generate datasets/experiments: see `generate_experiments.py` and `generate_malicious_experiments.py` for how experiment directories/conditions are created. Use these to create reproducible experiment inputs.

- Project-specific conventions and patterns

  - xApps use a common `xAppBase` class. New xApps should subclass `xAppBase` and use the `@xAppBase.start_function` decorator for the `start` method.
  - Metric names are comma-separated strings in CLI flags (see `--metrics` in `kpm5_xapp.py` and `detector_xapp.py`). Tests and patches should preserve that parsing.
  - Experiments rely on per-experiment directory layout: each experiment directory contains `conditions.csv`, `run_scenario.sh`, and subfolders `metrics/`, `gnb_logs/`, `ue_logs/`. Keep that layout when generating or validating experiments.
  - Long-running system interactions (docker, tmux, ip netns, sudo) are managed in shell script `run_enhanced.sh`. Avoid making Python-only changes that require shell-side adjustments without updating the script.

- Integration points & external dependencies

  - Docker Compose (in `openran/oran-sc-ric/docker-compose.yml`) runs the RIC and python xApp runner. Changes to xApp APIs must be compatible with the `python_xapp_runner` environment.
  - srsRAN and Open5GS services are expected; `run_enhanced.sh` interacts with local system tools (tmux, ip netns, sudo, lsof, docker). Any edits touching ports, IP ranges, or file paths must keep these scripts' expectations.
  - ML artifacts: `detector_xapp.py` expects joblib / PyTorch models passed by CLI flags (`--s1_model_path`, etc.). If changing model I/O, update CLI defaults and any training artifact generators.

- Code smells and safety checks for PRs

  - When modifying xApps, ensure logging and graceful shutdown hooks are preserved (signal handlers set in `if __name__ == '__main__'` blocks). The RIC expects the xApp to register routes and subscriptions and to handle SIGINT/SIGTERM.
  - When changing CSV layouts or metric names, update `kpm5_xapp._write_csv_header`, `run_enhanced.sh` validation and any dataset generators to keep consistency.
  - Avoid changing absolute paths embedded in `run_enhanced.sh` without introducing a configurable environment variable — the script is used on other machines with those paths configured.

- Examples (copyable patterns from repo)

  - Subclassing xAppBase: see `kpm5_xapp.py` and `detector_xapp.py` — implement `subscription_callback` and decorate `start`:
    - `@xAppBase.start_function\ndef start(self, e2_node_id, ue_ids, metric_names): ...`
  - Running RIC + xApp locally:
    - cd `openran/oran-sc-ric` && `docker compose up` (then run xApp inside `python_xapp_runner` container)

- What to do when you can't run services locally

  - If Docker/srsRAN/Open5GS aren't available, restrict edits to pure-Python units (e.g., feature engineering in `detector_xapp.py`) and add unit tests that mock out E2 indications and file system interactions. Keep tests isolated from `run_enhanced.sh` orchestration.

- Where to look for more context
  - xApp base and E2 modules: `openran/oran-sc-ric/xApps/python/lib/xAppBase.py` and `.../e2sm_kpm_module.py`
  - Orchestration for experiments: `run_enhanced.sh` and `openran/my-srsproject-demo/multi-ue-setup/`
  - Dataset generators: `generate_experiments.py`, `generate_malicious_experiments.py`

If any section is unclear or you'd like more examples (unit test skeletons, example Docker commands, or a suggested PR checklist), tell me which area to expand and I'll iterate.
