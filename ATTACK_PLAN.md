# BellaBell Attack Plan

This plan translates the product direction in `README.md` into an execution roadmap with practical engineering milestones, validation, and risk controls.

## 1) Define scope and success criteria (Day 0)

- Lock MVP scope to:
  - item CRUD,
  - CSS selector extraction,
  - scheduled checks,
  - change detection,
  - Email + Telegram notifications,
  - basic auth/local login,
  - history view with last known values.
- Define measurable success metrics:
  - extraction success rate on target test set (e.g., >90% with CSS strategy),
  - scheduler reliability (no missed jobs in 24h soak),
  - notification delivery success (e.g., >99% in staging test runs),
  - median check duration and alert latency.
- Write a concise non-goals list for MVP (e.g., Playwright extraction deferred).

## 2) Architecture and stack decisions (Day 1)

- Finalize service boundaries aligned with README compose layout:
  - `web` (UI + API),
  - `worker` (fetch/extract/compare/notify),
  - `scheduler` (enqueue jobs),
  - PostgreSQL,
  - Redis queue/cache.
- Decide core frameworks/libraries per service.
- Define deployment baseline:
  - docker-compose for local and initial self-hosting,
  - environment-variable based config,
  - secrets handling policy.

## 3) Data model and migrations (Day 1–2)

Create schema and migrations for:
- users/auth,
- monitored items,
- extraction configs (strategy + payload),
- check schedules,
- price observations/history,
- notifications + delivery logs,
- job execution logs and failure metadata.

Add indexes for common queries:
- due checks,
- item history by timestamp,
- notification retry lookups.

## 4) Build MVP backend APIs (Day 2–4)

- Auth endpoints (local login/basic auth pattern).
- Item management endpoints:
  - create/update/delete/list,
  - validate extraction config.
- History endpoints:
  - latest state + timeline of observations.
- Alert rule representation:
  - any change,
  - only drops,
  - only increases,
  - threshold fields reserved even if partially enforced in MVP.

Include OpenAPI/spec docs and request/response validation from day one.

## 5) Implement extraction engine v1 (Day 3–5)

- Implement strategy interface now, even with CSS-only MVP implementation.
- CSS extractor requirements:
  - robust text normalization,
  - currency symbol stripping,
  - decimal parsing with locale-aware guardrails,
  - deterministic error codes (selector missing, parse failed, network timeout).
- Build “test extraction” internal API (UI button can come later).

Prepare extension points for XPath/Regex/JSON-LD/Playwright.

## 6) Scheduling and worker pipeline (Day 4–6)

- Scheduler periodically finds due items and enqueues jobs.
- Worker pipeline per job:
  1. fetch,
  2. extract,
  3. normalize,
  4. compare against previous value,
  5. persist observation,
  6. trigger notifications if rule matches.
- Add retries, backoff, idempotency keys, and dead-letter handling.
- Enforce per-domain rate limiting to reduce block risk.

## 7) Notification integrations (Day 5–6)

- SMTP sender with template-based messages.
- Telegram bot sender with concise alert format.
- Delivery tracking table + retry policy by channel.
- Failure observability: classify auth errors, transient network errors, invalid chat IDs.

## 8) Build web UI MVP (Day 5–8)

- Screens/pages:
  - login,
  - items list/dashboard,
  - add/edit item form,
  - item detail with history summary.
- UX additions that materially reduce setup friction:
  - extraction preview (if backend endpoint is ready),
  - cron/interval presets,
  - clear validation and failure state messages.

## 9) Observability, reliability, and safety (Day 6–8)

- Structured logs with correlation/job IDs.
- Basic metrics:
  - checks executed,
  - extraction failures by reason,
  - alert sends and failures,
  - queue depth/latency.
- Health/readiness endpoints for each service.
- Add anti-abuse controls:
  - minimum allowed check interval,
  - request timeouts,
  - optional robots/TOS warning in UI.

## 10) Testing strategy (continuous, formalized Day 2+)

- Unit tests:
  - parser normalization edge cases,
  - alert rule evaluation,
  - scheduler due-time logic.
- Integration tests:
  - API + DB lifecycle,
  - worker processing from queued job to persisted observation.
- End-to-end smoke tests in compose:
  - create item,
  - run check,
  - confirm history update,
  - verify notification dispatch in test mode.
- Curate a fixture library of representative product pages.

## 11) Release readiness checklist (Day 8–9)

- Harden `.env.example` with all required vars and comments.
- Document backup/restore for PostgreSQL volumes.
- Produce operator runbook:
  - startup,
  - migration steps,
  - troubleshooting failed checks,
  - rotating SMTP/Telegram credentials.
- Create first tagged release and changelog.

## 12) Post-MVP expansion plan (Day 10+)

Based on README “Next” roadmap, prioritize in this order:
1. Playwright headless extraction,
2. Price history chart visualization,
3. Test extraction button in UI,
4. Multi-user/team model,
5. Import/export,
6. optional proxy/user-agent rotation,
7. per-site templates.

## Recommended add-ons beyond README

- **Site adapter test suite:** domain-specific regression tests to detect layout drift quickly.
- **Canary checks:** run a small control set every few minutes to detect systemic failures.
- **Notification dedup window:** suppress noisy repeated alerts during volatile changes.
- **Feature flags:** release advanced extractors incrementally.
- **SLOs + error budget:** force prioritization of reliability work before adding new features.

## Execution rhythm

- Daily: short standup + blocker review.
- Every 2 days: demo a vertical slice (UI → scheduler → worker → alert).
- End of week: soak test and reliability review before adding scope.

This attack plan keeps MVP tight while intentionally laying extension seams for the more difficult extraction and multi-tenant features.
