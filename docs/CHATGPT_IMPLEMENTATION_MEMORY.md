# CHATGPT_IMPLEMENTATION_MEMORY.md

## Current System State (Phase 4 Completed)
- **Math Engines**: 11 deterministic engines built, including complex `TransitEngine` and `YogaEngine`. No AI hallucination.
- **Backend**: FastAPI wrapper built. Endpoints for processing charts, querying the question engine, and exporting reports.
- **Reports**: Jinja2 HTML templates and WeasyPrint PDF builders implemented.
- **Frontend**: React + Vite PWA built. Uses Zustand for stateless data holding.
- **Testing**: 619 Pytest assertions currently passing.

## Strict Rules Learned
1. **Never parse PDFs**: This system solely reads `canonical_content.json` and `machine_index.json`.
2. **Deterministic Only**: The astrology engine must remain a pure math function. LLMs are only used at the very end in the Question Engine, heavily grounded by the math outputs.
3. **Stateless First**: The current architecture avoids a database. The entire `ChartProcessResponse` is held in the browser's memory (Zustand) to enable instantaneous offline-like speeds.

## Next Phase Context
If proceeding to Phase 5, the primary goal is **Database Persistence**. This will involve migrating the stateless memory into PostgreSQL via SQLAlchemy, implementing user authentication, and allowing saved chart histories. The frozen mathematical engines must NOT be modified during this infrastructure work.
