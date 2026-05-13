import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def _check_tabs(
    current: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> str:
    if "\t" in current:
        warnings.append(
            Issue(i, 1, "JEN001", "Tabulatory mogą psuć formatowanie Jenkinsfile")
        )
        fixed = current.replace("\t", "    ")
        fixes.append(
            Fix(
                i,
                "Zamieniono tabulatory na spacje",
                current.rstrip("\n"),
                fixed.rstrip("\n"),
            )
        )
        fixed_lines[i - 1] = fixed
        return fixed
    return current


def _check_trailing_whitespace(
    current: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> str:
    if current.rstrip() != current:
        warnings.append(Issue(i, 1, "JEN002", "Trailing whitespace"))
        fixed = current.rstrip()
        fixes.append(Fix(i, "Usunięto trailing whitespace", current, fixed))
        fixed_lines[i - 1] = fixed
        return fixed
    return current


def _check_unversioned_image(
    current: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> str:
    m = re.search(r"\bimage\s*['\"](?P<img>[^'\"]+)['\"]", current)
    if not m:
        return current
    img = m.group("img")
    if not (":latest" in img or ":" not in img):
        return current
    warnings.append(
        Issue(i, 1, "JEN003", "Użyj konkretnej wersji image zamiast latest/braku tagu")
    )
    if img.startswith("alpine"):
        replacement = "alpine:3.19"
    elif img.startswith("python"):
        replacement = "python:3.11"
    elif img.startswith("node"):
        replacement = "node:20"
    elif img.endswith(":latest"):
        replacement = img[: -len(":latest")] + ":1.0.0"
    else:
        replacement = img + ":1.0.0"
    fixed = current.replace(img, replacement)
    fixes.append(
        Fix(i, "Zmieniono image na wersjonowany tag", current.rstrip(), fixed.rstrip())
    )
    fixed_lines[i - 1] = fixed
    return fixed


def _check_pipe_to_shell(
    current: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> str:
    if (
        re.search(r"\b(curl|wget)\b", current)
        and "|" in current
        and re.search(r"\b(bash|sh)\b", current)
    ):
        warnings.append(
            Issue(i, 1, "JEN004", "Pipe do bash/sh w pipeline może być niebezpieczny")
        )
        if "curl" in current and "| bash" in current:
            fixed = re.sub(
                r"curl\s+([^|]+)\|\s*bash",
                r"curl \1-o /tmp/script.sh && bash /tmp/script.sh",
                current,
            )
            if fixed != current:
                fixes.append(
                    Fix(
                        i,
                        "Zamieniono curl|bash na zapis pliku + uruchomienie",
                        current.rstrip(),
                        fixed.rstrip(),
                    )
                )
                fixed_lines[i - 1] = fixed
                return fixed
    return current


def _check_hardcoded_secret(current: str, i: int, errors: List[Issue]) -> None:
    if re.search(
        r"(?i)\b(password|token|secret|key)\b\s*[=:]\s*[\"\'][^\"\']+[\"\']", current
    ):
        errors.append(Issue(i, 1, "JEN005", "Hardcoded secret w Jenkinsfile"))


def analyze_jenkinsfile(code: str) -> AnalysisResult:
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    lines = code.splitlines()
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        current = fixed_lines[i - 1]
        current = _check_tabs(current, i, warnings, fixes, fixed_lines)
        current = _check_trailing_whitespace(current, i, warnings, fixes, fixed_lines)
        current = _check_unversioned_image(current, i, warnings, fixes, fixed_lines)
        current = _check_pipe_to_shell(current, i, warnings, fixes, fixed_lines)
        _check_hardcoded_secret(current, i, errors)

    return AnalysisResult(
        "jenkinsfile", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
