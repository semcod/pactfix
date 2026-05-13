# Changelog

## [Unreleased]

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Changed
- Refactored Docker Compose and Kubernetes analyzers
- Updated PYPI.md documentation
- Code quality metrics improvements with 6 supporting modules

### Changed
- Refactored core code architecture for better maintainability
- Updated Playwright E2E test configuration

### Added
- GitLab CI support with dedicated analyzer
- Jenkinsfile support for pipeline analysis
- Enhanced language detection for YAML files
- Better error messages and fix explanations
- Comprehensive documentation with examples
- Test coverage badges and GitHub stats
- Interactive table of contents in README
- Multi-language support status table (24+ languages)

### Fixed
- Quote positioning detection in bash command substitutions (SC1073)
- Missing fix comments for bash analysis
- Python test import issues (pytest configuration)
- E2E test stability improvements
- Stats not updating when typing code
- Example code loading issues
- Clear input functionality

### Improved
- API documentation with all endpoints (`/api/analyze`, `/api/health`, `/api/snippet`)
- Development setup instructions
- Project structure documentation
- Docker sandbox testing documentation

### Added
- Real-time code analysis with debouncing
- History tracking for all fixes
- Export functionality (download/copy)
- Share via URL feature
- Statistics display (lines, chars, errors, warnings)
- Multi-language support for 20+ formats
- Docker sandbox testing
- Pactfix CLI integration

### Fixed
- Initial UI responsiveness issues
- Basic syntax highlighting

### Changed
- Updated Makefile build targets
- Updated pactfix sandbox module
- Updated sandbox test scripts
- Updated git commit helper

### Added
- Initial release
- Basic bash/shell analysis with ShellCheck integration
- Python code analysis (print, except, mutable defaults, == None)
- Web-based UI with real-time feedback
- Docker support and containerized deployment
- API endpoints for code analysis (`/api/analyze`, `/api/health`, `/api/snippet`)

---

### From Docker
```bash
docker-compose pull
docker-compose up -d
```

### From Source
```bash
git pull origin main
pip install -e pactfix-py
python3 server.py
```

- chore(release): perform multiple release bumps
- refactor(core): cleaner code architecture
- refactor(docs): add code quality metrics split across 6 supporting modules
- refactor: introduce new DSL (refactoring with new DSL)
- docs: document Changelog, including [1.2.0] - 2026-01-29
- fix(core): resolve Changelog [Unreleased] entries
- chore: update 6 files

