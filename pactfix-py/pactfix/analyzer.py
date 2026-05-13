import re
from pathlib import Path
from typing import Optional


def _detect_by_filename(code: str, filename: str) -> Optional[str]:
    fn_lower = filename.lower()
    fn_name = Path(filename).name.lower()
    if fn_name in _FILENAME_EXACT_MAP:
        lang = _FILENAME_EXACT_MAP[fn_name]
        if not (
            lang == "dockerfile"
            and "/" in fn_lower
            and not fn_lower.endswith("/dockerfile")
        ):
            return lang
    for pattern, lang in _PATH_PATTERNS:
        if re.search(pattern, fn_lower):
            return lang
    if fn_lower.endswith((".yml", ".yaml")):
        for pattern, lang in _YAML_PATH_PATTERNS:
            if re.search(pattern, fn_lower):
                return lang
        return "yaml"
    if fn_lower.endswith((".md", ".markdown", ".mdx")):
        return "markpact" if "markpact:" in code else "markdown"
    if fn_lower.endswith(".js"):
        return (
            "nodejs"
            if ("require(" in code or "module.exports" in code)
            else "javascript"
        )
    if fn_lower.endswith(".conf") and "apache" in fn_lower:
        return "apache"
    for ext, lang in _EXTENSION_MAP.items():
        if fn_lower.endswith(ext):
            return lang
    return None


def _detect_by_content(
    code: str, lines: list[str], first_line: str, filename: Optional[str]
) -> Optional[str]:
    if any(
        line.strip().upper().startswith(("FROM ", "RUN ", "COPY ", "ENTRYPOINT "))
        for line in lines[:20]
    ):
        if "FROM " in code.upper():
            return "dockerfile"
    if "services:" in code and ("image:" in code or "build:" in code):
        return "docker-compose"
    if "apiVersion:" in code and "kind:" in code:
        return "kubernetes"
    if 'resource "' in code or 'provider "' in code or 'variable "' in code:
        return "terraform"
    if any(
        kw in code.upper()
        for kw in ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "CREATE TABLE", "DROP "]
    ):
        return "sql"
    if (
        "on:" in code
        and ("push:" in code or "pull_request:" in code)
        and "jobs:" in code
    ):
        return "github-actions"
    if (
        "stages:" in code
        and "script:" in code
        and (".gitlab-ci" in (filename or "").lower() or "gitlab" in code.lower())
    ):
        return "gitlab-ci"
    if ("pipeline {" in code or "node {" in code) and (
        "stage(" in code or "stages {" in code
    ):
        return "jenkinsfile"
    if "- hosts:" in code or ("- name:" in code and "tasks:" in code):
        return "ansible"
    if (
        "{{" in code
        and "}}" in code
        and (".Values" in code or ".Release" in code or ".Chart" in code)
    ):
        return "helm"
    if "server {" in code or "location " in code:
        return "nginx"
    if "interface " in code and "{" in code and (":" in code or "export " in code):
        return "typescript"
    if "package " in code and ("func " in code or "import (" in code):
        return "go"
    if "fn " in code and ("let " in code or "use " in code) and "::" in code:
        return "rust"
    if ("public class " in code or "private class " in code) and "void " in code:
        return "java"
    if "namespace " in code and ("class " in code or "interface " in code):
        return "csharp"
    if "def " in code and "end" in code and ("class " in code or "module " in code):
        return "ruby"
    return None


def detect_language(code: str, filename: str = None) -> str:
    lines = code.strip().split("\n")
    first_line = lines[0] if lines else ""
    if filename:
        lang = _detect_by_filename(code, filename)
        if lang:
            return lang
    lang = _detect_by_content(code, lines, first_line, filename)
    if lang:
        return lang
    # ... (remaining logic for generic content detection) ...
    return "bash"
