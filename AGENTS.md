# AGENTS.md

This file is the operating constitution for AI agents working on this repository. Follow it before proposing or making code changes.

## Project Purpose

This project focuses on:

- AI-assisted automation
- Telegram-based workflows
- Bitcoin and financial market monitoring
- Upbit-based KRW-BTC data collection
- reproducible infrastructure
- maintainable server operations
- long-running local or server-side monitoring services

Priority order:

1. stability
2. maintainability
3. simplicity
4. observability
5. performance

This project prioritizes:

- simplicity
- reproducibility
- operational stability
- low maintenance cost

Over:

- hype
- unnecessary abstraction
- premature scaling
- feature count

## Technology Stack Limits

- Primary language is Python.
- Keep the project Python-first unless explicitly requested otherwise.
- Existing runtime assumptions include Python, `.env` configuration, Telegram Bot API, Upbit market data, SQLite/CSV persistence, shell/batch scripts, Docker, and systemd-style services.
- Prefer Docker Compose over Kubernetes.
- Do not introduce new frameworks, queues, databases, schedulers, or infrastructure layers without a clear operational need.
- Streamlit/dashboard code is optional and should not become a required dependency for headless server operation unless explicitly requested.
- Prefer the existing dependency set in `requirements.txt` before adding new packages.

## Architecture Principles

- Keep architecture simple.
- Prefer monolith over microservices.
- Prefer explicit logic over abstraction.
- Prefer reproducibility over cleverness.
- Avoid hidden automation.
- Avoid premature optimization.
- Do not silently rewrite architecture.
- Keep changes scoped to the requested task.
- Preserve restartable, script-friendly operations.
- Treat Telegram workflows, monitoring jobs, persistence, and alerting as operationally sensitive paths.

## File Creation Rules

Do not create unnecessary markdown files.

Allowed:

- `AGENTS.md`
- `README.md`
- `docs/*`
- explicitly requested files

Do not create:

- `MEMORY.md`
- `NOTES.md`
- `TEMP.md`
- `SUMMARY.md`
- duplicated instruction files
- extra planning or scratch markdown files

Before creating any file:

- Confirm that the file is necessary.
- Prefer editing an existing relevant file.
- Keep generated files minimal and purposeful.
- Do not create temporary artifacts in the repository root unless explicitly requested.

## Agent Behavior Rules

- Do not overengineer.
- Do not silently rewrite architecture.
- Explain major design decisions.
- Keep changes scoped.
- Avoid introducing unnecessary dependencies.
- Prefer deterministic behavior.
- Make operational impact visible when changing services, schedules, alerts, persistence, or deployment scripts.
- Preserve existing user workflows unless the requested task requires changing them.
- Do not make broad formatting-only rewrites.
- Do not rename files, commands, environment variables, or services without a clear reason.
- Prefer small, reviewable changes.

## Python Rules

- Prefer standard library when practical.
- Minimize dependencies.
- Keep functions small and explicit.
- Avoid magic behavior.
- Use type hints when useful.
- Keep imports at the top of files.
- Prefer clear error handling around network calls, file IO, and environment variables.
- Maintain readable logging for scripts and long-running services.
- Do not introduce global mutable state unless it is simple, intentional, and safe for the current execution model.
- Preserve compatibility with headless server environments.

## Investment and Backtesting Rules

- This project provides monitoring and alerting, not financial advice.
- Do not present signals, alerts, or backtest results as guaranteed profit opportunities.
- Keep investment-related wording factual, cautious, and transparent.
- Clearly distinguish live market data, derived indicators, alerts, and hypothetical backtest results.
- Avoid look-ahead bias in any backtest or historical simulation.
- Account for fees, slippage, market hours/data intervals, and execution assumptions when adding backtest logic.
- Keep backtest logic reproducible from stored inputs or clearly documented data sources.
- Do not add automated trading or order execution unless explicitly requested.
- Treat alert thresholds and strategy assumptions as configuration or explicit code, not hidden behavior.

## Logging Rules

- All long-running services must produce logs.
- Logs should be human-readable.
- Avoid excessive verbosity.
- Critical failures must be visible immediately.
- Include enough context to debug failed API calls, Telegram delivery, persistence errors, and scheduler/service failures.
- Do not log secrets, tokens, chat IDs when avoidable, credentials, or raw sensitive environment values.

## Reliability and Operational Stability Rules

- Services should recover automatically.
- Prefer restartable systems.
- Avoid manual-only operations.
- Design for crash recovery.
- Keep deployments reproducible.
- Prefer idempotent jobs where practical.
- Handle external API failures gracefully.
- Use retries and backoff for transient network operations where appropriate.
- Avoid changes that increase operational fragility for the bot, local monitor, scheduled jobs, Docker, or systemd services.
- Make state files and caches understandable and safe to recreate when possible.

## Security Rules

- Never hardcode secrets.
- Use `.env` files or deployment secret stores.
- Do not commit tokens or credentials.
- Minimize exposed ports.
- Avoid printing secrets in logs, errors, tests, or generated output.
- Keep Telegram bot tokens, chat IDs, API keys, and operational credentials out of source code.
- Preserve `.gitignore` protections for local secrets, caches, logs, virtual environments, and generated data.
- Validate or constrain externally triggered bot commands where practical.

## Git Rules

- Keep commits focused.
- Avoid large unrelated changes.
- Do not rewrite history without reason.
- Prefer readable commit messages.
- Do not include generated caches, local logs, virtual environments, secrets, or unrelated data in commits.
- Review diffs before committing.
- Avoid mixing refactors with behavior changes unless necessary.

## Operating Philosophy

- Stability is more important than feature count.
- Keep architecture simple and reproducible.
- Prefer boring, understandable operations.
- Prefer explicit scripts and clear service behavior over hidden automation.
- Optimize for a small project that can be maintained reliably over time.
- Every automation should be understandable, observable, and recoverable.
- A working, low-maintenance monitor is more valuable than a clever but fragile system.
