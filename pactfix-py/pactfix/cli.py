import sys
from pathlib import Path
from typing import Any, Dict, Tuple
from .analyzer import analyze_code, add_fix_comments
from .sandbox import detect_project_language


def get_files_to_process(path: Path) -> list[Path]:
    extensions = [
        ".sh",
        ".py",
        ".php",
        ".js",
        ".ts",
        ".sql",
        ".tf",
        ".yml",
        ".yaml",
        ".conf",
        ".go",
        ".rs",
        ".java",
        ".cs",
        ".rb",
        ".html",
        ".css",
        ".json",
        ".jsonc",
        ".toml",
        ".ini",
        ".cfg",
        ".tpl",
        ".gotmpl",
    ]
    files = []
    for ext in extensions:
        files.extend(path.rglob(f"*{ext}"))
    for special in [
        "Dockerfile",
        "Makefile",
        "Jenkinsfile",
        ".gitlab-ci.yml",
        ".gitlab-ci.yaml",
    ]:
        files.extend(path.rglob(special))
    exclude_dirs = {
        ".git",
        ".pactfix",
        "_fixtures",
        "node_modules",
        "__pycache__",
        "venv",
        ".venv",
        "vendor",
        "target",
        "build",
        "dist",
        ".idea",
        ".vscode",
    }
    return [
        f
        for f in files
        if not any(excl in f.parts for excl in exclude_dirs) and f.is_file()
    ]


def save_fixed_file(
    file_path: Path, content: str, sandbox: bool, pactfix_dir: Path, rel_path: Path
) -> None:
    if sandbox:
        fixed_dir = pactfix_dir / "fixed"
        fixed_file_path = fixed_dir / rel_path
        fixed_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(fixed_file_path, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


def process_single_file(
    file_path: Path,
    project_path: Path,
    comment: bool,
    sandbox: bool,
    pactfix_dir: Path | None,
    verbose: bool,
) -> Tuple[Dict[str, Any] | None, int, int, int, str | None, str | None]:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()
    result = analyze_code(code, str(file_path))
    if comment and result.fixes:
        result.fixed_code = add_fix_comments(result)

    rel_path = file_path.relative_to(project_path)
    if result.fixed_code != code:
        save_fixed_file(file_path, result.fixed_code, sandbox, pactfix_dir, rel_path)

    res_dict = {
        "file": str(rel_path),
        "language": result.language,
        "errors": len(result.errors),
        "warnings": len(result.warnings),
        "fixes": len(result.fixes),
    }
    return (
        res_dict,
        len(result.errors),
        len(result.warnings),
        len(result.fixes),
        str(rel_path),
        result.fixed_code if result.fixed_code != code else None,
    )


def process_project(
    project_path: str,
    comment: bool = False,
    sandbox: bool = False,
    run_tests: bool = False,
    verbose: bool = False,
) -> int:
    path = Path(project_path).resolve()
    if not path.exists():
        print(f"❌ Path does not exist: {path}", file=sys.stderr)
        return 1
    language, stats = detect_project_language(path)
    files_to_process = get_files_to_process(path)
    if not files_to_process:
        print(f"⚠️  No files found to analyze in: {path}")
        return 0
    results, fixed_files, files_modified = [], {}, []
    total_errors = total_warnings = total_fixes = 0
    pactfix_dir = path / ".pactfix" if sandbox else None
    for file_path in sorted(set(files_to_process)):
        try:
            res, errs, warns, fixes, rel_path, fixed_code = process_single_file(
                file_path, path, comment, sandbox, pactfix_dir, verbose
            )
            total_errors += errs
            total_warnings += warns
            total_fixes += fixes
            results.append(res)
            if fixed_code:
                if sandbox:
                    fixed_files[rel_path] = fixed_code
                else:
                    files_modified.append(rel_path)
        except Exception as e:
            if verbose:
                print(f"❌ {file_path}: {e}")
    if sandbox:
        run_sandbox_environment(
            path,
            language,
            results,
            total_errors,
            total_warnings,
            total_fixes,
            fixed_files,
            comment,
            run_tests,
            pactfix_dir,
        )
    return 0
