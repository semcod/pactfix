"""Java code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_string_equality(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r'==\s*"', stripped) or re.search(r'"\s*==', stripped):
        warnings.append(
            Issue(i, 1, "JAVA001", "Użyj .equals() zamiast == dla Stringów")
        )


def _check_generic_exception(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\s*catch\s*\(\s*Exception\s+", stripped):
        warnings.append(
            Issue(
                i, 1, "JAVA002", "Łapanie ogólnego Exception - złap konkretny wyjątek"
            )
        )


def _check_empty_catch(
    stripped: str, i: int, lines: List[str], errors: List[Issue]
) -> None:
    if "catch" in stripped:
        next_lines = "\n".join(lines[i : i + 3])
        if re.search(r"\{\s*\}", next_lines):
            errors.append(
                Issue(i, 1, "JAVA003", "Pusty blok catch - obsłuż lub zaloguj wyjątek")
            )


def _check_system_out(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "System.out.print" in stripped or "System.err.print" in stripped:
        warnings.append(Issue(i, 1, "JAVA004", "Użyj loggera zamiast System.out/err"))


def _check_hardcoded_credentials(stripped: str, i: int, errors: List[Issue]) -> None:
    for pattern in ["password", "secret", "apiKey", "api_key", "token"]:
        if re.search(rf'{pattern}\s*=\s*"[^"]+', stripped, re.I):
            errors.append(Issue(i, 1, "JAVA005", f"Hardcoded {pattern}"))


def _check_raw_types(stripped: str, i: int, warnings: List[Issue]) -> None:
    for rtype in ["List", "Map", "Set", "ArrayList", "HashMap", "HashSet"]:
        if re.search(rf"\b{rtype}\s+\w+\s*=", stripped) and "<" not in stripped:
            warnings.append(
                Issue(i, 1, "JAVA006", f"Raw type {rtype} - dodaj parametr typu")
            )


def _check_public_fields(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(
        r"^\s*public\s+(?!static|final|class|interface|enum)\w+\s+\w+\s*;", stripped
    ):
        warnings.append(
            Issue(i, 1, "JAVA007", "Publiczne pole - użyj private z getterem/setterem")
        )


def _check_missing_override(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if re.match(r"^\s*public\s+\w+\s+(equals|hashCode|toString)\s*\(", stripped):
        prev_line = lines[i - 2].strip() if i > 1 else ""
        if "@Override" not in prev_line:
            warnings.append(
                Issue(i, 1, "JAVA008", "Brak @Override dla nadpisywanej metody")
            )


def _check_string_concat_in_loop(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if (
        "+" in stripped
        and "String" in stripped
        and "for" in "\n".join(lines[max(0, i - 5) : i])
    ):
        warnings.append(
            Issue(i, 1, "JAVA009", "Konkatenacja Stringów w pętli - użyj StringBuilder")
        )


def _check_unclosed_resources(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "new FileInputStream" in stripped or "new BufferedReader" in stripped:
        if "try" not in stripped and "try" not in (lines[i - 2] if i > 1 else ""):
            warnings.append(Issue(i, 1, "JAVA010", "Zasób bez try-with-resources"))


def _check_thread_sleep(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "Thread.sleep" in stripped:
        warnings.append(
            Issue(i, 1, "JAVA011", "Thread.sleep - rozważ ScheduledExecutorService")
        )


def _check_synchronized_method(stripped: str, i: int, warnings: List[Issue]) -> None:
    if ("synchronized" in stripped and "void" in stripped) or (
        "synchronized" in stripped and re.search(r"\)\s*\{", stripped)
    ):
        warnings.append(
            Issue(
                i, 1, "JAVA012", "synchronized na metodzie - rozważ blok synchronized"
            )
        )


def _check_legacy_date(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "new Date()" in stripped or "java.util.Date" in stripped:
        warnings.append(Issue(i, 1, "JAVA013", "java.util.Date - użyj java.time API"))


def _check_sql_injection(stripped: str, i: int, errors: List[Issue]) -> None:
    if "executeQuery(" in stripped or "executeUpdate(" in stripped:
        if "+" in stripped or "String.format" in stripped:
            errors.append(
                Issue(
                    i,
                    1,
                    "JAVA014",
                    "Potencjalny SQL injection - użyj PreparedStatement",
                )
            )


def _check_null_deref(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if re.search(r"\w+\.\w+\(\)", stripped) and "null" in "\n".join(
        lines[max(0, i - 3) : i]
    ):
        warnings.append(
            Issue(i, 1, "JAVA015", "Potencjalny NullPointerException - sprawdź null")
        )


def analyze_java(code: str) -> AnalysisResult:
    """Analyze Java code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_string_equality(stripped, i, warnings)
        _check_generic_exception(stripped, i, warnings)
        _check_empty_catch(stripped, i, lines, errors)
        _check_system_out(stripped, i, warnings)
        _check_hardcoded_credentials(stripped, i, errors)
        _check_raw_types(stripped, i, warnings)
        _check_public_fields(stripped, i, warnings)
        _check_missing_override(stripped, i, lines, warnings)
        _check_string_concat_in_loop(stripped, i, lines, warnings)
        _check_unclosed_resources(stripped, i, lines, warnings)
        _check_thread_sleep(stripped, i, warnings)
        _check_synchronized_method(stripped, i, warnings)
        _check_legacy_date(stripped, i, warnings)
        _check_sql_injection(stripped, i, errors)
        _check_null_deref(stripped, i, lines, warnings)

    return AnalysisResult("java", code, "\n".join(fixed_lines), errors, warnings, fixes)
