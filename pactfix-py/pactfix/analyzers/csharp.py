"""C# code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_string_comparison(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r'==\s*"', stripped) and "nameof" not in stripped:
        warnings.append(
            Issue(i, 1, "CS001", "Rozważ String.Equals() z StringComparison")
        )


def _check_generic_exception(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\s*catch\s*\(\s*Exception\s*", stripped):
        warnings.append(
            Issue(i, 1, "CS002", "Łapanie ogólnego Exception - złap konkretny wyjątek")
        )


def _check_empty_catch(
    stripped: str, i: int, lines: List[str], errors: List[Issue]
) -> None:
    if "catch" in stripped:
        next_lines = "\n".join(lines[i : i + 3])
        if re.search(r"\{\s*\}", next_lines):
            errors.append(Issue(i, 1, "CS003", "Pusty blok catch"))


def _check_console_write(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "Console.Write" in stripped:
        warnings.append(Issue(i, 1, "CS004", "Użyj ILogger zamiast Console.Write"))


def _check_hardcoded_credentials(stripped: str, i: int, errors: List[Issue]) -> None:
    for pattern in ["password", "secret", "apiKey", "connectionString"]:
        if re.search(rf'{pattern}\s*=\s*"[^"]+', stripped, re.I):
            errors.append(Issue(i, 1, "CS005", f"Hardcoded {pattern}"))


def _check_var_unclear(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\s*var\s+\w+\s*=\s*\w+\.\w+\(", stripped):
        warnings.append(
            Issue(i, 1, "CS006", "var z niejasnym typem - rozważ explicit type")
        )


def _check_public_field(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\s*public\s+\w+\s+\w+\s*;", stripped) and "const" not in stripped:
        warnings.append(Issue(i, 1, "CS007", "Publiczne pole - użyj property"))


def _check_async_void(stripped: str, i: int, errors: List[Issue]) -> None:
    if re.match(r"^\s*(public|private|protected)?\s*async\s+void\s+", stripped):
        if "EventHandler" not in stripped:
            errors.append(Issue(i, 1, "CS008", "async void - użyj async Task"))


def _check_unawaited_async(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "Async(" in stripped and "await" not in stripped and "Task" not in stripped:
        warnings.append(Issue(i, 1, "CS009", "Wywołanie async bez await"))


def _check_lock_this(stripped: str, i: int, errors: List[Issue]) -> None:
    if "lock(this)" in stripped or "lock (this)" in stripped:
        errors.append(
            Issue(
                i, 1, "CS010", "lock(this) jest niebezpieczne - użyj prywatnego obiektu"
            )
        )


def _check_string_concat(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r'"\s*\+\s*\w+\s*\+\s*"', stripped):
        warnings.append(
            Issue(i, 1, "CS011", 'Konkatenacja stringów - użyj interpolacji $""')
        )


def _check_idisposable(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "new " in stripped and any(
        x in stripped for x in ["Stream", "Reader", "Writer", "Connection"]
    ):
        if "using" not in stripped and "using" not in (lines[i - 2] if i > 1 else ""):
            warnings.append(Issue(i, 1, "CS012", "IDisposable bez using"))


def _check_sql_injection(stripped: str, i: int, errors: List[Issue]) -> None:
    if "SqlCommand" in stripped or "ExecuteReader" in stripped:
        if "+" in stripped or "String.Format" in stripped:
            errors.append(
                Issue(i, 1, "CS013", "Potencjalny SQL injection - użyj parametrów")
            )


def _check_thread_sleep(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "Thread.Sleep" in stripped:
        warnings.append(Issue(i, 1, "CS014", "Thread.Sleep - użyj await Task.Delay"))


def _check_datetime_now(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "DateTime.Now" in stripped or "DateTime.Today" in stripped:
        warnings.append(
            Issue(i, 1, "CS016", "Rozważ DateTimeOffset lub DateTime.UtcNow")
        )


def _check_magic_numbers(stripped: str, i: int, warnings: List[Issue]) -> None:
    if (
        re.search(r"[=<>]\s*\d{2,}", stripped)
        and "const" not in stripped
        and "//" not in stripped
    ):
        warnings.append(Issue(i, 1, "CS017", "Magic number - użyj stałej z nazwą"))


def analyze_csharp(code: str) -> AnalysisResult:
    """Analyze C# code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_string_comparison(stripped, i, warnings)
        _check_generic_exception(stripped, i, warnings)
        _check_empty_catch(stripped, i, lines, errors)
        _check_console_write(stripped, i, warnings)
        _check_hardcoded_credentials(stripped, i, errors)
        _check_var_unclear(stripped, i, warnings)
        _check_public_field(stripped, i, warnings)
        _check_async_void(stripped, i, errors)
        _check_unawaited_async(stripped, i, warnings)
        _check_lock_this(stripped, i, errors)
        _check_string_concat(stripped, i, warnings)
        _check_idisposable(stripped, i, lines, warnings)
        _check_sql_injection(stripped, i, errors)
        _check_thread_sleep(stripped, i, warnings)
        _check_datetime_now(stripped, i, warnings)
        _check_magic_numbers(stripped, i, warnings)

    return AnalysisResult(
        "csharp", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
