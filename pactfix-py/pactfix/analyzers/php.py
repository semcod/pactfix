import re
from typing import List

from ..analyzer import Issue, AnalysisResult


def _check_unvalidated_input(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"\$_(GET|POST|REQUEST|COOKIE)\[", stripped):
        if "htmlspecialchars" not in stripped and "filter_" not in stripped:
            warnings.append(
                Issue(
                    i,
                    1,
                    "PHP001",
                    "Niezwalidowane dane wejściowe - użyj filter_input lub htmlspecialchars",
                )
            )


def _check_loose_equality(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "==" in stripped and ("null" in stripped.lower() or "false" in stripped.lower()):
        warnings.append(Issue(i, 1, "PHP002", "Użyj === zamiast == dla porównań"))


def _check_deprecated_mysql(stripped: str, i: int, errors: List[Issue]) -> None:
    if re.search(r"\bmysql_(connect|query|fetch)", stripped):
        errors.append(
            Issue(i, 1, "PHP003", "Przestarzałe funkcje mysql_* - użyj PDO lub mysqli")
        )


def _check_extract(stripped: str, i: int, errors: List[Issue]) -> None:
    if "extract(" in stripped:
        errors.append(
            Issue(
                i,
                1,
                "PHP004",
                "extract() jest niebezpieczne - użyj jawnego przypisania",
            )
        )


def _check_error_suppression(stripped: str, i: int, warnings: List[Issue]) -> None:
    if stripped.startswith("@"):
        warnings.append(
            Issue(i, 1, "PHP005", "Operator @ tłumi błędy - obsłuż je prawidłowo")
        )


def _check_short_tags(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "<?=" in stripped or re.match(r"^<\?\s+", stripped):
        warnings.append(Issue(i, 1, "PHP006", "Użyj pełnego <?php zamiast short tags"))


def analyze_php(code: str) -> AnalysisResult:
    """Analyze PHP code."""
    errors, warnings, fixes = [], [], []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_unvalidated_input(stripped, i, warnings)
        _check_loose_equality(stripped, i, warnings)
        _check_deprecated_mysql(stripped, i, errors)
        _check_extract(stripped, i, errors)
        _check_error_suppression(stripped, i, warnings)
        _check_short_tags(stripped, i, warnings)

    return AnalysisResult("php", code, code, errors, warnings, fixes)
