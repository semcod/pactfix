import re
from typing import List, Set

from ..analyzer import Issue, Fix, AnalysisResult


def _collect_created_table(upper: str, tables_created: Set[str]) -> None:
    if "CREATE TABLE" in upper:
        m = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"\[]?(\w+)', upper)
        if m:
            tables_created.add(m.group(1).lower())


def _collect_referenced_tables(upper: str, tables_referenced: Set[str]) -> None:
    if any(kw in upper for kw in ["FROM ", "JOIN ", "INTO ", "UPDATE "]):
        for m in re.finditer(r'(?:FROM|JOIN|INTO|UPDATE)\s+[`"\[]?(\w+)', upper):
            tables_referenced.add(m.group(1).lower())


def _check_select_star(upper: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"\bSELECT\s+\*", upper):
        warnings.append(Issue(i, 1, "SQL001", "SELECT * - wymień konkretne kolumny"))


def _check_update_delete_without_where(
    stripped: str,
    upper: str,
    i: int,
    total_lines: int,
    errors: List[Issue],
) -> None:
    if ("UPDATE " in upper or "DELETE FROM" in upper) and "WHERE" not in upper:
        if ";" in stripped or i == total_lines:
            errors.append(Issue(i, 1, "SQL003", "UPDATE/DELETE bez WHERE!"))


def _check_drop_without_if_exists(
    stripped: str,
    line: str,
    upper: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "DROP " in upper and "IF EXISTS" not in upper:
        warnings.append(Issue(i, 1, "SQL004", "DROP bez IF EXISTS"))
        fixed = stripped.replace("DROP ", "DROP IF EXISTS ", 1)
        fixes.append(Fix(i, "Dodano IF EXISTS", stripped, fixed))
        fixed_lines[i - 1] = line.replace(stripped, fixed)


def _check_create_without_if_not_exists(
    upper: str, i: int, warnings: List[Issue]
) -> None:
    if "CREATE TABLE" in upper and "IF NOT EXISTS" not in upper:
        warnings.append(Issue(i, 1, "SQL005", "CREATE bez IF NOT EXISTS"))


def _check_grant_all(upper: str, i: int, warnings: List[Issue]) -> None:
    if "GRANT ALL" in upper:
        warnings.append(
            Issue(i, 1, "SQL007", "GRANT ALL - przyznaj tylko wymagane uprawnienia")
        )


def _check_plaintext_password(upper: str, i: int, errors: List[Issue]) -> None:
    if re.search(r"PASSWORD\s*[=:]\s*['\"][^'\"]+['\"]", upper):
        errors.append(Issue(i, 1, "SQL008", "Hasło w plain text"))


def analyze_sql(code: str) -> AnalysisResult:
    """Analyze SQL."""
    errors, warnings, fixes = [], [], []
    lines = code.split("\n")
    fixed_lines = lines.copy()
    tables_created: Set[str] = set()
    tables_referenced: Set[str] = set()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        upper = stripped.upper()

        _collect_created_table(upper, tables_created)
        _collect_referenced_tables(upper, tables_referenced)
        _check_select_star(upper, i, warnings)
        _check_update_delete_without_where(stripped, upper, i, len(lines), errors)
        _check_drop_without_if_exists(
            stripped, line, upper, i, warnings, fixes, fixed_lines
        )
        _check_create_without_if_not_exists(upper, i, warnings)
        _check_grant_all(upper, i, warnings)
        _check_plaintext_password(upper, i, errors)

    missing = tables_referenced - tables_created - {"dual", "information_schema"}
    context = {
        "tables_created": list(tables_created),
        "tables_referenced": list(tables_referenced),
        "potentially_missing": list(missing),
    }
    return AnalysisResult(
        "sql", code, "\n".join(fixed_lines), errors, warnings, fixes, context
    )
