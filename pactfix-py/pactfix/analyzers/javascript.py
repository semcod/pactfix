import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def _check_var_keyword(
    stripped: str,
    line: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if re.search(r"\bvar\s+\w+", stripped):
        warnings.append(Issue(i, 1, "JS001", "Użyj let/const zamiast var"))
        fixed = re.sub(r"\bvar\b", "let", stripped)
        fixes.append(Fix(i, "Zamieniono var na let", stripped, fixed))
        fixed_lines[i - 1] = line.replace(stripped, fixed)


def _check_loose_equality(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"[^=!]={2}[^=]", stripped) and "===" not in stripped:
        warnings.append(Issue(i, 1, "JS002", "Użyj === zamiast =="))


def _check_console_log(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "console.log" in stripped:
        warnings.append(Issue(i, 1, "JS003", "console.log w kodzie produkcyjnym"))


def _check_eval(stripped: str, i: int, errors: List[Issue]) -> None:
    if "eval(" in stripped:
        errors.append(Issue(i, 1, "JS004", "eval() jest niebezpieczne - unikaj"))


def _check_sync_io(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"\b(readFileSync|writeFileSync)\b", stripped):
        warnings.append(
            Issue(i, 1, "NODE002", "Sync I/O blokuje event loop - użyj async")
        )


def analyze_javascript(code: str, is_nodejs: bool = False) -> AnalysisResult:
    """Analyze JavaScript/Node.js code."""
    errors, warnings, fixes = [], [], []
    lines = code.split("\n")
    fixed_lines = lines.copy()
    lang = "nodejs" if is_nodejs else "javascript"

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_var_keyword(stripped, line, i, warnings, fixes, fixed_lines)
        _check_loose_equality(stripped, i, warnings)
        _check_console_log(stripped, i, warnings)
        _check_eval(stripped, i, errors)
        if is_nodejs:
            _check_sync_io(stripped, i, warnings)

    return AnalysisResult(lang, code, "\n".join(fixed_lines), errors, warnings, fixes)
