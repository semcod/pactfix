# ticket-004: Fix pytest collection, markdown analysis, E2E live debug, and PERF-AUDIT findings

- **Status**: IN_PROGRESS
- **Workflow state**: VERIFIED

SESSION_EXECUTION_AUTHORIZATION: continue analysis, repairs, and standard alignment across projects using `wellmanifest/wellman`.

## Acceptance Criteria
- [x] AC-01: Exclude `test-projects` and `_fixtures` in `pytest.ini` and `pactfix-py/pyproject.toml`.
- [x] AC-02: Restore full `server.py` (`analyze_code_multi` and `DebugHandler` HTTP server) so `tests/test_markdown_analysis.py` and `tests/test_e2e_live_debug.py` pass (`226 passed`).
- [x] AC-03: Fix `PERF-AUDIT-HEALTH-002` in `docker-compose.yml` and `PERF-AUDIT-KWARG-001` in `pactfix-py/pactfix/cli.py`.
- [x] AC-04: Adopt Wellmanifest `baseline` standards in `.governance/`.
