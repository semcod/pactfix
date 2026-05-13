<!-- code2docs:start --># pactfix

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.9-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-224-green)
> **224** functions | **5** classes | **73** files | CC̄ = 10.1

> Auto-generated project documentation from source code analysis.

**Author:** Tom Softreck <tom@sapletta.com>  
**License:** MIT[(LICENSE)](./LICENSE)  
**Repository:** [https://github.com/wronai/pactown-debug](https://github.com/wronai/pactown-debug)

### From PyPI

```bash
pip install pactfix
```

### From Source

```bash
git clone https://github.com/wronai/pactown-debug
cd pactfix
pip install -e .
```


# Generate full documentation for your project
pactfix ./my-project

# Only regenerate README
pactfix ./my-project --readme-only

# Preview what would be generated (no file writes)
pactfix ./my-project --dry-run

# Check documentation health
pactfix check ./my-project

# Sync — regenerate only changed modules
pactfix sync ./my-project
```

### Python API

```python
from pactfix import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `pactfix`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `pactfix.yaml` in your project root (or run `pactfix init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

pactfix can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- pactfix:start -->
# Project Title
... auto-generated content ...
<!-- pactfix:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
pactfix/
├── output├── project        ├── faulty        ├── fixed            ├── fixed_faulty            ├── fixed_fixed    ├── config        ├── faulty            ├── fixed_fixed        ├── fixed            ├── fixed_faulty        ├── fixed        ├── faulty            ├── fixed_faulty            ├── fixed_fixed        ├── fixed            ├── fixed_fixed        ├── faulty            ├── fixed_faulty        ├── fixed            ├── fixed_faulty            ├── fixed_fixed    ├── git_commit_helper        ├── spec    ├── src/        ├── analyzer        ├── fixed_js        ├── sandbox        ├── server    ├── pactfix/        ├── __main__        ├── cli            ├── rust            ├── docker_compose            ├── ruby            ├── ini_generic            ├── python_lang            ├── markdown        ├── analyzers/            ├── json_generic            ├── go            ├── kubernetes            ├── helm            ├── html            ├── github_actions            ├── bash            ├── gitlab_ci            ├── apache            ├── makefile            ├── sql            ├── jenkinsfile            ├── dockerfile            ├── nginx            ├── toml_generic            ├── ansible            ├── javascript            ├── php            ├── csharp            ├── systemd            ├── java            ├── css            ├── typescript├── server            ├── terraform        ├── Dockerfile            ├── markpact            ├── yaml_generic        ├── analyzer```

### Classes

- **`Sandbox`** — Docker-based sandbox for running and testing fixed code.
- **`DebugHandler`** — HTTP handler for the debug server.
- **`Issue`** — —
- **`Fix`** — —
- **`AnalysisResult`** — —

### Functions

- `port()` — —
- `userAge()` — —
- `processUser()` — —
- `result()` — —
- `callback()` — —
- `x()` — —
- `userAge()` — —
- `processUser()` — —
- `result()` — —
- `callback()` — —
- `x()` — —
- `userAge()` — —
- `processUser()` — —
- `result()` — —
- `callback()` — —
- `x()` — —
- `userAge()` — —
- `processUser()` — —
- `result()` — —
- `callback()` — —
- `x()` — —
- `process()` — —
- `process()` — —
- `process()` — —
- `process()` — —
- `fs()` — —
- `http()` — —
- `path()` — —
- `data()` — —
- `processFile()` — —
- `content()` — —
- `result()` — —
- `response()` — —
- `fs()` — —
- `http()` — —
- `path()` — —
- `data()` — —
- `processFile()` — —
- `content()` — —
- `result()` — —
- `response()` — —
- `fs()` — —
- `http()` — —
- `path()` — —
- `data()` — —
- `processFile()` — —
- `content()` — —
- `result()` — —
- `response()` — —
- `fs()` — —
- `http()` — —
- `path()` — —
- `data()` — —
- `processFile()` — —
- `content()` — —
- `result()` — —
- `response()` — —
- `process_data(items)` — —
- `calculate_average(numbers)` — —
- `process_data(items)` — —
- `calculate_average(numbers)` — —
- `process_data(items)` — —
- `calculate_average(numbers)` — —
- `get_staged_files()` — Get list of staged files
- `categorize_file(filename)` — Categorize file and return appropriate description
- `generate_commit_message(files)` — Generate commit message based on changed files
- `get_current_version()` — Get current version from VERSION file or default to 1.0.0
- `bump_version(version)` — Bump patch version
- `update_version_file(new_version)` — Update VERSION file
- `update_changelog(version, files)` — Update CHANGELOG.md with new version and changes
- `main()` — —
- `waitForAnalysisDone()` — —
- `status()` — —
- `input()` — —
- `value()` — —
- `errorCount()` — —
- `fixedCount()` — —
- `codeLines()` — —
- `output()` — —
- `highlightedSpans()` — —
- `lineNumbers()` — —
- `outputHtml()` — —
- `h()` — —
- `hash()` — —
- `langBadge()` — —
- `response()` — —
- `data()` — —
- `result()` — —
- `hasQuoteError()` — —
- `process_data(items)` — —
- `calculate_average(numbers)` — —
- `detectLanguage()` — —
- `ext()` — —
- `lines()` — —
- `firstLine()` — —
- `analyzeBash()` — —
- `lineNum()` — —
- `stripped()` — —
- `fixed()` — —
- `analyzePython()` — —
- `analyzePHP()` — —
- `analyzeJavaScript()` — —
- `applyFixes()` — —
- `analyzeCode()` — —
- `lang()` — —
- `analyzer()` — —
- `fixedCode()` — —
- `analyzeFile()` — —
- `code()` — —
- `result()` — —
- `process_data(items)` — —
- `calculate_average(numbers)` — —
- `detect_project_language(project_path)` — Detect the primary language of a project based on files present.
- `create_language_dockerfile(language, output_dir)` — Create a Dockerfile for a specific language.
- `create_all_dockerfiles(output_dir)` — Create Dockerfiles for all supported languages.
- `health()` — Health check endpoint.
- `analyze()` — Analyze code endpoint.
- `detect()` — Detect language endpoint.
- `languages()` — List supported languages.
- `create_app()` — Application factory.
- `run_server(host, port, debug)` — Run the Flask server.
- `main()` — —
- `process_file(input_path, output_path, language, comment)` — Process a single file.
- `process_stdin(output_path, language, comment, log_file)` — Process code from stdin.
- `process_batch(directory, verbose)` — Process all files in a directory.
- `fix_all_examples(verbose, comment)` — Fix all files in examples/ directory and save to fixed/ subdirectories.
- `init_dockerfiles(output_dir)` — Create Dockerfiles for all supported languages.
- `setup_sandbox_only(project_path, verbose)` — Setup sandbox without running fixes.
- `process_project(project_path, comment, sandbox, run_tests)` — Process entire project - scan, fix all files, optionally run in sandbox.
- `analyze_rust(code)` — Analyze Rust code for common issues.
- `analyze_docker_compose(code)` — —
- `analyze_ruby(code)` — Analyze Ruby code for common issues.
- `analyze_ini(code)` — Analyze INI/CFG for common issues.
- `analyze_python(code)` — Analyze Python code.
- `analyze_markdown(code)` — Analyze Markdown by extracting fenced code blocks and analyzing each.
- `analyze_json(code)` — Analyze JSON for common issues.
- `analyze_go(code)` — Analyze Go code for common issues.
- `analyze_kubernetes(code)` — —
- `analyze_helm(code)` — Analyze Helm-related YAML/templates for common issues.
- `analyze_html(code)` — Analyze HTML for common issues.
- `analyze_github_actions(code)` — Analyze GitHub Actions workflow.
- `analyze_bash(code)` — Analyze Bash script.
- `analyze_gitlab_ci(code)` — —
- `analyze_apache(code)` — Analyze Apache configuration for common issues.
- `analyze_makefile(code)` — Analyze Makefile for common issues.
- `analyze_sql(code)` — Analyze SQL.
- `analyze_jenkinsfile(code)` — —
- `analyze_dockerfile(code)` — Analyze Dockerfile.
- `analyze_nginx(code)` — Analyze nginx config.
- `analyze_toml(code)` — Analyze TOML for common issues.
- `analyze_ansible(code)` — Analyze Ansible playbook.
- `analyze_javascript(code, is_nodejs)` — Analyze JavaScript/Node.js code.
- `analyze_php(code)` — Analyze PHP code.
- `analyze_csharp(code)` — Analyze C# code for common issues.
- `analyze_systemd(code)` — Analyze systemd unit file for common issues.
- `analyze_java(code)` — Analyze Java code for common issues.
- `analyze_css(code)` — Analyze CSS for common issues.
- `analyze_typescript(code)` — Analyze TypeScript code for common issues.
- `apply_brace_fixes(code)` — —
- `run_shellcheck(code)` — Run ShellCheck on the code and return parsed results.
- `analyze_with_builtin(code)` — Built-in analysis when ShellCheck is not available.
- `apply_fixes(code, issues)` — Apply automatic fixes based on ShellCheck issues.
- `analyze_code(code)` — Main analysis function combining ShellCheck and built-in checks.
- `add_fix_comments(code, fixes)` — Add comments explaining fixes to the code.
- `batch_analyze_directory(root, max_files, max_bytes, include_hidden)` — —
- `analyze_python_code(code)` — Analyze Python code for common issues.
- `analyze_php_code(code)` — Analyze PHP code for common issues.
- `analyze_javascript_code(code)` — Analyze JavaScript/Node.js code for common issues.
- `analyze_dockerfile(code)` — Analyze Dockerfile for common issues and best practices.
- `analyze_docker_compose(code)` — Analyze docker-compose.yml for common issues.
- `analyze_sql(code)` — Analyze SQL for common issues and security problems.
- `analyze_terraform(code)` — Analyze Terraform/HCL for common issues.
- `analyze_kubernetes(code)` — Analyze Kubernetes YAML for common issues.
- `analyze_nginx_config(code)` — Analyze nginx configuration for common issues.
- `analyze_github_actions(code)` — Analyze GitHub Actions workflow for common issues.
- `analyze_ansible(code)` — Analyze Ansible playbook for common issues.
- `analyze_markdown(code)` — Analyze Markdown by extracting fenced code blocks and analyzing each block.
- `detect_language(code, filename)` — Detect the programming language of the code.
- `analyze_code_multi(code, force_language, filename)` — Analyze code with automatic language detection.
- `add_fix_comments_lang(code, fixes, comment_char)` — Add comments explaining fixes to the code with language-specific comment style.
- `main()` — Start the debug server.
- `analyze_terraform(code)` — —
- `analyze_markpact(code)` — Analyze a markpact file by inspecting each markpact:* codeblock.
- `analyze_yaml(code)` — Analyze YAML for common issues.
- `detect_language(code, filename)` — Detect the language/format of the code.
- `add_fix_comments(result)` — —
- `analyze_code(code, filename, force_language)` — Main entry point for code analysis.


## Project Structure

📄 `e2e.app.spec` (77 functions)
📄 `examples.bash.faulty`
📄 `examples.bash.fixed`
📄 `examples.bash.fixed.fixed_faulty`
📄 `examples.bash.fixed.fixed_fixed`
📄 `examples.javascript.faulty` (5 functions)
📄 `examples.javascript.fixed` (5 functions)
📄 `examples.javascript.fixed.fixed_faulty` (5 functions)
📄 `examples.javascript.fixed.fixed_fixed` (5 functions)
📄 `examples.nodejs.faulty` (8 functions)
📄 `examples.nodejs.fixed` (8 functions)
📄 `examples.nodejs.fixed.fixed_faulty` (8 functions)
📄 `examples.nodejs.fixed.fixed_fixed` (8 functions)
📄 `examples.php.faulty` (1 functions)
📄 `examples.php.fixed` (1 functions)
📄 `examples.php.fixed.fixed_faulty` (1 functions)
📄 `examples.php.fixed.fixed_fixed` (1 functions)
📄 `examples.python.fixed` (2 functions)
📄 `examples.python.fixed.fixed_faulty` (2 functions)
📄 `examples.python.fixed.fixed_fixed` (2 functions)
📄 `examples.python.fixed_js` (2 functions)
📄 `output` (2 functions)
📄 `pactfix-py.dockerfiles.Dockerfile`
📦 `pactfix-py.pactfix`
📄 `pactfix-py.pactfix.__main__`
📄 `pactfix-py.pactfix.analyzer` (5 functions, 3 classes)
📦 `pactfix-py.pactfix.analyzers`
📄 `pactfix-py.pactfix.analyzers.ansible` (1 functions)
📄 `pactfix-py.pactfix.analyzers.apache` (1 functions)
📄 `pactfix-py.pactfix.analyzers.bash` (3 functions)
📄 `pactfix-py.pactfix.analyzers.csharp` (1 functions)
📄 `pactfix-py.pactfix.analyzers.css` (1 functions)
📄 `pactfix-py.pactfix.analyzers.docker_compose` (1 functions)
📄 `pactfix-py.pactfix.analyzers.dockerfile` (1 functions)
📄 `pactfix-py.pactfix.analyzers.github_actions` (1 functions)
📄 `pactfix-py.pactfix.analyzers.gitlab_ci` (1 functions)
📄 `pactfix-py.pactfix.analyzers.go` (1 functions)
📄 `pactfix-py.pactfix.analyzers.helm` (1 functions)
📄 `pactfix-py.pactfix.analyzers.html` (1 functions)
📄 `pactfix-py.pactfix.analyzers.ini_generic` (1 functions)
📄 `pactfix-py.pactfix.analyzers.java` (1 functions)
📄 `pactfix-py.pactfix.analyzers.javascript` (1 functions)
📄 `pactfix-py.pactfix.analyzers.jenkinsfile` (1 functions)
📄 `pactfix-py.pactfix.analyzers.json_generic` (3 functions)
📄 `pactfix-py.pactfix.analyzers.kubernetes` (6 functions)
📄 `pactfix-py.pactfix.analyzers.makefile` (1 functions)
📄 `pactfix-py.pactfix.analyzers.markdown` (1 functions)
📄 `pactfix-py.pactfix.analyzers.markpact` (3 functions)
📄 `pactfix-py.pactfix.analyzers.nginx` (1 functions)
📄 `pactfix-py.pactfix.analyzers.php` (1 functions)
📄 `pactfix-py.pactfix.analyzers.python_lang` (2 functions)
📄 `pactfix-py.pactfix.analyzers.ruby` (1 functions)
📄 `pactfix-py.pactfix.analyzers.rust` (1 functions)
📄 `pactfix-py.pactfix.analyzers.sql` (1 functions)
📄 `pactfix-py.pactfix.analyzers.systemd` (1 functions)
📄 `pactfix-py.pactfix.analyzers.terraform` (1 functions)
📄 `pactfix-py.pactfix.analyzers.toml_generic` (1 functions)
📄 `pactfix-py.pactfix.analyzers.typescript` (1 functions)
📄 `pactfix-py.pactfix.analyzers.yaml_generic` (1 functions)
📄 `pactfix-py.pactfix.cli` (8 functions)
📄 `pactfix-py.pactfix.sandbox` (12 functions, 1 classes)
📄 `pactfix-py.pactfix.server` (6 functions)
📦 `pactown-js.src`
📄 `pactown-js.src.analyzer` (33 functions)
📄 `playwright.config` (1 functions)
📄 `project`
📄 `scripts.git_commit_helper` (8 functions)
📄 `server` (37 functions, 1 classes)

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Please see [CONTRIBUTING.md](https://github.com/wronai/pactfix/blob/main/CONTRIBUTING.md) for guidelines.

# Clone the repository
git clone https://github.com/wronai/pactown-debug
cd pactfix

# Install in development mode
pip install -e ".[dev]"

## Documentation

- 📖 [Full Documentation](https://github.com/wronai/pactown-debug/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/wronai/pactown-debug/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/wronai/pactown-debug/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/wronai/pactown-debug/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](https://github.com/wronai/pactfix/blob/main/docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](https://github.com/wronai/pactfix/blob/main/docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](https://github.com/wronai/pactfix/blob/main/docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](https://github.com/wronai/pactfix/blob/main/docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](https://github.com/wronai/pactfix/blob/main/docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](https://github.com/wronai/pactfix/blob/main/docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](https://github.com/wronai/pactfix/blob/main/docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](https://github.com/wronai/pactfix/blob/main/docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](https://github.com/wronai/pactfix/blob/main/CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->