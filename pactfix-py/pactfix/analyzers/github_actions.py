import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def _check_unpinned_action(
    stripped: str,
    line: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "uses:" in stripped and ("@master" in stripped or "@main" in stripped):
        warnings.append(Issue(i, 1, "GHA001", "Użyj wersji/SHA zamiast @master"))
        fixed = re.sub(r"@(master|main)$", "@v4", stripped)
        fixes.append(Fix(i, "Zmieniono na wersję", stripped, fixed))
        fixed_lines[i - 1] = line.replace(stripped, fixed)


def _check_pull_request_target(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "pull_request_target" in stripped:
        warnings.append(
            Issue(i, 1, "GHA002", "pull_request_target może być niebezpieczne")
        )


def _check_hardcoded_secret(stripped: str, i: int, errors: List[Issue]) -> None:
    if re.search(
        r"(password|token|key|secret)\s*[:=]\s*(?!\$\{\{)(?!\$\{)(?!\$)\S+",
        stripped,
        re.I,
    ):
        errors.append(
            Issue(i, 1, "GHA003", "Hardcoded secret - użyj ${{ secrets.NAME }}")
        )


def _check_shell_injection(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "${{" in stripped and ("github.event." in stripped or "inputs." in stripped):
        if "run:" in stripped:
            warnings.append(Issue(i, 1, "GHA004", "Możliwy shell injection"))


def _check_missing_permissions(stripped: str, i: int, warnings: List[Issue]) -> None:
    if stripped.startswith("jobs:"):
        warnings.append(Issue(i, 1, "GHA005", "Ustaw minimalne permissions"))


def analyze_github_actions(code: str) -> AnalysisResult:
    """Analyze GitHub Actions workflow."""
    errors, warnings, fixes = [], [], []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_unpinned_action(stripped, line, i, warnings, fixes, fixed_lines)
        _check_pull_request_target(stripped, i, warnings)
        _check_hardcoded_secret(stripped, i, errors)
        _check_shell_injection(stripped, i, warnings)
        _check_missing_permissions(stripped, i, warnings)

    return AnalysisResult(
        "github-actions", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
