# Pactown Live Debug 🚀

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](Dockerfile)
[![ShellCheck](https://img.shields.io/badge/ShellCheck-integrated-orange.svg)](https://www.shellcheck.net/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-202%20passing-green.svg)](#testing)
[![E2E](https://img.shields.io/badge/e2e-41%20tests-yellow.svg)](#testing)

> Multi-language code analyzer and auto-fixer with real-time feedback and Docker sandbox testing support.

---

## 📋 Spis treści

- [Features](#-features)
- [Quick Start](#-quick-start)
  - [Docker (recommended)](#docker-recommended)
  - [Without Docker](#-without-docker)
- [How to Use](#-how-to-use)
- [Examples](#-examples)
  - [Bash Script Analysis](#bash-script-analysis)
  - [Python Code Analysis](#python-code-analysis)
  - [Dockerfile Analysis](#dockerfile-analysis)
  - [Multi-language Support](#multi-language-support)
- [Detected Issues](#-detected-issues)
- [API Reference](#-api-reference)
- [Pactfix CLI](#-pactfix-cli-)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Contributing](#contributing)
- [License](#license)

---

## ⚡ Features

- ⚡ **Real-time analysis** - Błędy widoczne podczas pisania
- 🔧 **Auto-fix** - Automatyczne naprawianie typowych błędów
- 📜 **History tracking** - Pełna historia wykrytych błędów i poprawek
- 💾 **Export options** - Pobieranie poprawionego skryptu lub kopiowanie do schowka
- 🐳 **Docker sandbox** - Testowanie poprawek w izolowanym środowisku
- 🧪 **Multi-language** - Wsparcie dla 24+ języków i formatów
- 🔄 **Live preview** - Podgląd poprawek w czasie rzeczywistym
- 📊 **Statistics** - Liczba linii, znaków, błędów i ostrzeżeń
- 🔗 **Share via URL** - Udostępnianie kodu przez link

# Clone the repository
git clone https://github.com/wronai/pactown-debug.git
cd pactown-debug

# Build and run with Docker Compose
docker-compose up --build

# Or directly with Docker
docker build -t pactown-debug .
docker run -p 8081:8081 pactown-debug
```

Open http://localhost:8081 in your browser.

# Requirements: Python 3.10+ and ShellCheck
sudo apt-get install shellcheck  # Ubuntu/Debian
brew install shellcheck           # macOS

# Clone and run
git clone https://github.com/wronai/pactown-debug.git
cd pactown-debug
pip install -e pactfix-py
python3 server.py
```

## 📖 How to Use

1. **Paste your code** - Insert your script in the left panel
2. **Automatic analysis** - Errors are detected in real-time
3. **View fixes** - Right panel shows corrected code with explanations
4. **Export** - Download or copy the fixed script

### Bash Script Analysis

**Input (with errors):**
```bash
#!/usr/bin/bash
OUTPUT=/home/student/output-

for HOST in server{a,b}; do
    echo "$(ssh student@${HOST} hostname -f") >> ${OUTPUT}${HOST}
    if test -f $OUTPUT/$HOST; then
        rm -v $OUTPUT/$HOST
    fi
done
```

**Output (fixed):**
```bash
#!/usr/bin/bash
OUTPUT=/home/student/output-

for HOST in server{a,b}; do
    echo "$(ssh student@${HOST} hostname -f)" >> ${OUTPUT}${HOST}  # ✅ NAPRAWIONO: Poprawiono pozycję cudzysłowu zamykającego
    if test -f ${OUTPUT}/${HOST}; then  # ✅ NAPRAWIONO: Dodano klamerki do zmiennych
        rm -v ${OUTPUT}/${HOST}  # ✅ NAPRAWIONO: Dodano klamerki do zmiennych
    fi || exit 1  # ✅ NAPRAWIONO: Dodano obsługę błędów dla rm
done || exit 1  # ✅ NAPRAWIONO: Dodano obsługę błędów dla for loop
```

### Python Code Analysis

**Input (with issues):**
```python
#!/usr/bin/env python3
import os
import sys

def process_data(items=[]):
    for item in items:
        if item == None:
            print "Item is None"
            continue
        try:
            result = item * 2
        except:
            print "Error processing item"
    return items

if __name__ == "__main__":
    data = [1, 2, None, 4]
    process_data(data)
```

**Output (fixed):**
```python
#!/usr/bin/env python3
import os
import sys

def process_data(items=None):  # ✅ NAPRAWIONO: Unikaj mutable default arguments
    if items is None:
        items = []
    for item in items:
        if item is None:  # ✅ NAPRAWIONO: Użyj 'is None' zamiast '== None'
            print("Item is None")  # ✅ NAPRAWIONO: Użyj print() z nawiasami (Python 3)
            continue
        try:
            result = item * 2
        except Exception as e:  # ✅ NAPRAWIONO: Unikaj bare except, łap konkretny wyjątek
            print(f"Error processing item: {e}")  # ✅ NAPRAWIONO: Użyj f-string i print()
    return items

if __name__ == "__main__":
    data = [1, 2, None, 4]
    process_data(data)  # ✅ NAPRAWIONO: Dodano docstring do funkcji
```

### Dockerfile Analysis

**Input (with issues):**
```dockerfile
FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y python3
COPY . /app
WORKDIR /app
CMD python3 app.py
```

**Output (fixed):**
```dockerfile
FROM ubuntu:latest  # ✅ NAPRAWIONO: Użyj konkretnego tagu zamiast latest
RUN apt-get update && apt-get install -y python3 && rm -rf /var/lib/apt/lists/*  # ✅ NAPRAWIONO: Połącz RUN i wyczyść cache
COPY . /app
WORKDIR /app
CMD ["python3", "app.py"]  # ✅ NAPRAWIONO: Użyj exec form
```

### Multi-language Support

Pactown Live Debug supports 24+ languages and formats:

| Language | Status | Example |
|----------|--------|---------|
| **Bash/Shell** | ✅ Full | `#!/bin/bash` |
| **Python** | ✅ Full | `def hello():` |
| **JavaScript** | ✅ Full | `console.log()` |
| **Dockerfile** | ✅ Full | `FROM node:18` |
| **Docker Compose** | ✅ Full | `version: '3.8'` |
| **Kubernetes YAML** | ✅ Full | `apiVersion: v1` |
| **Terraform** | ✅ Full | `resource "aws_instance"` |
| **SQL** | ✅ Full | `SELECT * FROM` |
| **Nginx Config** | ✅ Full | `server { ... }` |
| **GitHub Actions** | ✅ Full | `on: [push]` |
| **GitLab CI** | ✅ New | `stages: ...` |
| **Jenkinsfile** | ✅ New | `pipeline { ... }` |
| **Ansible** | ✅ Full | `---\n- hosts:` |
| **Markdown** | ✅ Full | ``` fenced blocks |
| **JSON** | ✅ Full | `{ "key": "value" }` |
| **TOML** | ✅ Full | `[section]` |
| **INI** | ✅ Full | `key=value` |
| **And more...** | 🚧 In Progress | PHP, Go, Rust, Java |

### Bash/Shell
| Code | Description | Example |
|------|-------------|---------|
| SC1073 | Syntax errors - misplaced quotes, brackets | `echo "$(cmd")` |
| SC2086 | Unquoted variables | `echo $VAR` |
| SC2006 | Use backticks instead of $() | ``cmd`` |
| SC2164 | cd without error handling | `cd /path` |
| SC2162 | read without -r flag | `read var` |

### Python
| Code | Description | Example |
|------|-------------|---------|
| PY001 | Use print() without parentheses | `print "text"` |
| PY002 | Mutable default arguments | `def func(items=[]):` |
| PY003 | Use == None instead of is None | `if x == None:` |
| PY004 | Bare except clause | `except:` |
| PY005 | Missing docstring | `def func():` |

### Dockerfile
| Code | Description | Example |
|------|-------------|---------|
| DF001 | Use 'latest' tag | `FROM ubuntu:latest` |
| DF002 | Multiple RUN instructions | `RUN apt-get update`\n`RUN apt-get install` |
| DF003 | Missing cache cleanup | `RUN apt-get update` |
| DF004 | Use shell form of CMD | `CMD python app.py` |

### POST /api/analyze

Analyzes code and returns fixes for detected issues.

**Request:**
```json
{
  "code": "#!/bin/bash\necho $VAR",
  "language": "bash"  // optional, auto-detected if not provided
}
```

**Response:**
```json
{
  "originalCode": "#!/bin/bash\necho $VAR",
  "fixedCode": "#!/bin/bash\necho \"$VAR\"",
  "errors": [],
  "warnings": [
    {
      "line": 2,
      "column": 6,
      "code": "SC2086",
      "message": "Double quote to prevent globbing and word splitting",
      "severity": "warning"
    }
  ],
  "fixes": [
    {
      "line": 2,
      "message": "Dodano cudzysłowy wokół zmiennej",
      "before": "echo $VAR",
      "after": "echo \"$VAR\""
    }
  ],
  "language": "bash",
  "context": {}
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.5",
  "features": {
    "shellcheck": false,
    "bash_analysis": true,
    "python_analysis": true,
    "auto_fix": true,
    "pactfix_api": false,
    "pactfix_url": "http://pactfix-api:5000"
  }
}
```

### POST /api/snippet

Save or update a code snippet.

**Request:**
```json
{
  "code": "#!/bin/bash\necho hello",
  "mode": "code"
}
```

**Response:**
```json
{
  "id": "abc123def456",
  "url": "http://localhost:8081/#abc123def456"
}
```

## 🛠️ Pactfix CLI

The project includes the `pactfix` CLI tool for analyzing and auto-fixing code in multiple languages.

### Key Features

- **Project-wide scanning** (`--path`) - Analyze entire projects
- **Docker sandbox** (`--sandbox`) - Test fixes in containers
- **Automated testing** (`--test`) - Run tests in sandbox
- **Multi-language support** - Bash, Python, Go, Node.js, Dockerfile, and more

# Analyze and fix entire project
pactfix --path ./my-project

# Run with Docker sandbox
pactfix --path ./my-project --sandbox

# Sandbox with tests
pactfix --path ./my-project --sandbox --test

# Insert comments above fixes
pactfix --path ./my-project --comment

# Fix specific file
pactfix --file script.sh

# List supported languages
pactfix --list-languages
```

### Testing with Sandboxes

The project includes test projects in `pactfix-py/test-projects/`:

```bash
# Run with in-container tests
make test-sandbox-tests
```

Each test project has `_fixtures/faulty/` with baseline code for deterministic testing.

## 🏗️ Project Structure

```
pactown-debug/
├── app/                    # Frontend application
│   ├── index.html         # Main UI
│   └── assets/            # Static assets
├── server.py              # Python backend server
├── pactfix-py/            # Pactfix CLI tool
│   ├── pactfix/           # Main package
│   │   ├── analyzer.py    # Core analysis engine
│   │   ├── analyzers/     # Language-specific analyzers
│   │   └── cli.py         # CLI interface
│   ├── test-projects/     # Test projects with fixtures
│   │   ├── bash-project/
│   │   ├── python-project/
│   │   └── ...
│   └── scripts/           # Test scripts
├── tests/                 # Backend tests
├── e2e/                   # E2E tests (Playwright)
├── Dockerfile             # Container definition
├── docker-compose.yml     # Docker Compose config
├── Makefile              # Build and test targets
├── playwright.config.ts  # Playwright configuration
└── README.md             # This file
```

# Sandbox with in-container tests
make test-sandbox-tests
```

### Test Coverage

- **Backend**: 8 tests covering API endpoints
- **Pactfix CLI**: 202 tests covering all analyzers
- **E2E**: 41 tests covering UI interactions
- **Sandbox**: Multiple real-world project scenarios

### Tech Stack

- **Frontend**: Vanilla JavaScript, CSS Grid, CSS Variables
- **Backend**: Python 3.10+, http.server
- **Analysis**: ShellCheck (with fallback to built-in analysis)
- **Testing**: Playwright (E2E), pytest (CLI), unittest (Backend)
- **Container**: Docker, Alpine-based

### Roadmap

- [x] Support for Python/Node.js/Go/Dockerfile
- [x] GitLab CI and Jenkinsfile support
- [ ] AI-powered explanations (llama.cpp)
- [ ] Collaborative debugging sessions
- [ ] VSCode extension
- [ ] More auto-fix rules
- [ ] Real-time collaboration
- [ ] Code snippet library
- [ ] Integration with GitHub PRs

### Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/pactown-debug.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Add tests for new features
   - Follow the existing code style
   - Update documentation

4. **Run tests**
   ```bash
   make test
   ```

5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```

6. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes clearly
   - Link any relevant issues
   - Ensure CI passes

# Clone the repo
git clone https://github.com/wronai/pactown-debug.git
cd pactown-debug

# Install dependencies
pip install -e pactfix-py[dev]

# Install playwright browsers
npx playwright install

# Run tests in watch mode
make test-frontend  # E2E tests
make test-pactfix   # CLI tests
```

## 📄 License

Apache 2.0 License © 2026 Pactown Team

---

<div align="center">

**[⬆ Back to top](#pactown-live-debug-)**

Built with ❤️ by the [Pactown](https://pactown.dev) team

*Part of the [Pactown](https://pactown.dev) project - Educational platform for juniors*

[![GitHub stars](https://img.shields.io/github/stars/wronai/pactown-debug.svg?style=social&label=Star)](https://github.com/wronai/pactown-debug)
[![GitHub forks](https://img.shields.io/github/forks/wronai/pactown-debug.svg?style=social&label=Fork)](https://github.com/wronai/pactown-debug/fork)
[![GitHub issues](https://img.shields.io/github/issues/wronai/pactown-debug.svg)](https://github.com/wronai/pactown-debug/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/wronai/pactown-debug.svg)](https://github.com/wronai/pactown-debug/pulls)

</div>

<!-- taskill:status:start -->

## Status

_Last updated by [taskill](https://github.com/oqlos/taskill) at 2026-04-25 13:41 UTC_

| Metric | Value |
|---|---|
| HEAD | `5b97217` |
| Coverage | — |
| Failing tests | — |
| Commits in last cycle | 50 |

> A series of release commits plus targeted refactors and docs updates. Notable changes include core architecture cleanup, a new DSL refactor, documentation updates for the changelog (v1.2.0), and addition of code-quality metrics split into six supporting modules.

<!-- taskill:status:end -->
