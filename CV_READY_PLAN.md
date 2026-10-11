# CV-Ready Backend Plan

## 1) Goal

Turn this project into a presentable, self-contained demo that works without real MongoDB credentials and can be shown on a CV without needing a production environment. The focus is on a clean demo flow, realistic mock data, and a very lightweight UI so the project is easier to explain and easier to run locally.

## 2) Current project issues

From the current codebase, the main blockers are:

- The application is tightly coupled to MongoDB and environment variables in [BacktestToLiveSlippage/config.py](BacktestToLiveSlippage/config.py).
- The app imports required settings at startup, so it will fail without a real `.env` file.
- The repo layer currently assumes live database collections and does not support a local/mock mode.
- There is no frontend or web demo layer yet, so the project is backend-only and harder to present.
- The project is built around real trading data and live broker names, which is not usable on a CV without a demo dataset.
- The dependency stack is not yet polished for a demo setup, and missing package info should be cleaned up.

## 3) Desired final state

The project should be able to:

- run locally with no private MongoDB credentials,
- load realistic sample data from JSON files,
- work in a demo mode by default for CV presentation,
- show a simple UI or web page to trigger a sample reconciliation,
- expose a clean API response that demonstrates the logic without depending on production systems,
- still keep the original backend logic available for real data when configured.

## 4) Proposed architecture

### A. Keep current backend logic as the core engine

The reconciliation engine in [BacktestToLiveSlippage/services/flow.py](BacktestToLiveSlippage/services/flow.py), the repositories, and the matching logic should remain the main project value. We should not rewrite the domain logic; instead, we should add compatibility layers around it.

### B. Add a demo/data layer

Create a mock-data folder with realistic sample files such as:

- `data/mock/backtest_trades.json`
- `data/mock/live_trades.json`
- `data/mock/strategies.json`
- `data/mock/clients.json`
- `data/mock/brokers.json`

These files should contain a small but realistic set of trading records matching the same schema the app expects.

### C. Add an environment-driven mode switch

Introduce a mode such as:

- `APP_MODE=demo`
- `APP_MODE=production`

When `demo` is selected:

- use mock JSON repositories instead of MongoDB repositories,
- skip external MongoDB credential requirements,
- load sample data from local files,
- keep the same API contract to the rest of the app.

When `production` is selected:

- keep the existing MongoDB workflow exactly as it is today.

### D. Add a minimal frontend for presentation

Because there is no frontend yet, keep it simple and lightweight:

- a single static HTML page served by FastAPI,
- small JavaScript to call the backend API,
- sample inputs for strategy, date range, tolerance, and client/broker filters,
- a result section showing summary + mismatch cards.

This is enough for a CV demo without needing a full React app.

## 5) Execution plan

### Phase 1: Stabilize the project for local demo use

Tasks:

- clean up the configuration flow in [BacktestToLiveSlippage/config.py](BacktestToLiveSlippage/config.py),
- make environment variables optional when demo mode is enabled,
- ensure app startup works without a real `.env`,
- add safe fallback messaging for missing production credentials,
- verify the FastAPI app starts successfully in local demo mode.

Deliverable:

- the backend boots locally without any real MongoDB access.

### Phase 2: Add mock data and repository abstraction

Tasks:

- create realistic mock JSON datasets in a dedicated folder,
- create a JSON-backed repository implementation parallel to the MongoDB version,
- make the dependency injection switch based on mode, so the app still uses the same service layer,
- validate that the matching engine can process the mock records successfully.

Deliverable:

- sample backtest and live trade data can be reconciled successfully using the existing logic.

### Phase 3: Add a simple demo UI

Tasks:

- create a lightweight HTML/JS dashboard or landing page,
- connect it to the existing API endpoints in [BacktestToLiveSlippage/routes/mismatch.py](BacktestToLiveSlippage/routes/mismatch.py),
- allow users to choose a strategy/date window and see summary results,
- keep styling minimal but polished enough for a CV and portfolio presentation.

Deliverable:

- a functioning local demo that is easy to explain in an interview or portfolio.

### Phase 4: Clean up for portfolio readiness

Tasks:

- add a clean README with setup instructions,
- mention demo mode clearly in docs,
- include sample output screenshots or response examples,
- add a couple of realistic sample queries,
- verify dependency list and Python package requirements.

Deliverable:

- a project that looks intentional, documented, and resume-ready.

### Phase 5: Optional enhancement (if time allows)

- add a single-page dashboard with charts or summary cards,
- expose a downloadable sample report,
- keep the original MongoDB-backed API untouched for real deployment cases.

## 6) Recommended file additions

Suggested additions for this transition:

- `data/mock/`
- `data/mock/backtest_trades.json`
- `data/mock/live_trades.json`
- `data/mock/clients.json`
- `data/mock/brokers.json`
- `repositories/json_backtest_repo.py` or equivalent adapter
- `repositories/json_live_repo.py` or equivalent adapter
- `templates/demo.html` or `static/demo.html`
- `README.md`
- `.env.example`

## 7) Risk and mitigation

### Risk: the project currently assumes production Mongo data everywhere

Mitigation: build the demo mode first so the app can start without external services.

### Risk: schema mismatches between Mongo records and JSON records

Mitigation: keep the JSON records aligned to the same normalized trade format used by the matching logic.

### Risk: too much time spent on frontend

Mitigation: use a minimal static UI, not a full frontend framework.

### Risk: complexity for local setup

Mitigation: keep the app defaulting to demo mode and provide a single command to run it.

## 8) Suggested first implementation order

1. Fix config and startup for demo mode.
2. Add JSON mock data fixtures.
3. Add JSON-backed repository support.
4. Validate the existing reconciliation logic with mock data.
5. Add a simple demo page to trigger requests.
6. Write final README and CV notes.

## 9) Acceptance criteria

The project is ready for CV presentation when:

- it launches locally without real MongoDB credentials,
- mock JSON data drives the workflow successfully,
- API endpoints return meaningful mismatch results,
- a simple UI is available for demonstration,
- the README clearly explains how to run the project.

## 10) Recommended next step

I recommend starting with Phase 1 and Phase 2 only, because those create the foundation. Once the app runs reliably in demo mode, the frontend and documentation become much easier and more meaningful.
