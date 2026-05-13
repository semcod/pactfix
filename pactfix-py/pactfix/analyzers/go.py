"""Go code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_unchecked_error(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if ", err :=" in stripped or ", err =" in stripped:
        next_lines = "\n".join(lines[i : i + 3])
        if "if err != nil" not in next_lines and "_ = err" not in next_lines:
            warnings.append(
                Issue(i, 1, "GO001", "Błąd nie jest sprawdzany - dodaj if err != nil")
            )


def _check_panic(stripped: str, i: int, code: str, warnings: List[Issue]) -> None:
    if "panic(" in stripped and "func main" not in code[: code.find(stripped)]:
        warnings.append(
            Issue(i, 1, "GO002", "panic() w kodzie biblioteki - użyj error")
        )


def _check_empty_error_msg(stripped: str, i: int, errors: List[Issue]) -> None:
    if 'errors.New("")' in stripped or "errors.New('')" in stripped:
        errors.append(Issue(i, 1, "GO003", "Pusty komunikat błędu"))


def _check_sprintf_no_args(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "fmt.Sprintf(" in stripped and "%" not in stripped:
        warnings.append(
            Issue(
                i,
                1,
                "GO004",
                "fmt.Sprintf bez argumentów formatowania - użyj zwykłego stringa",
            )
        )


def _check_goroutine_no_sync(
    stripped: str, i: int, code: str, warnings: List[Issue]
) -> None:
    if "go func()" in stripped or re.search(r"go\s+\w+\(", stripped):
        if "sync." not in code and "chan " not in code and "<-" not in code:
            warnings.append(Issue(i, 1, "GO005", "Goroutine bez synchronizacji"))


def _check_slice_equality(stripped: str, i: int, errors: List[Issue]) -> None:
    if re.search(r"\[\].*==\s*nil", stripped) is None and re.search(
        r"==\s*\[\]", stripped
    ):
        errors.append(Issue(i, 1, "GO006", "Nie można porównywać slice'ów przez =="))


def _check_defer_in_loop(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if stripped.startswith("defer ") and any(
        "for " in lines[j] for j in range(max(0, i - 10), i)
    ):
        warnings.append(
            Issue(i, 1, "GO007", "defer w pętli - może prowadzić do wycieków zasobów")
        )


def _check_time_sleep(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "time.Sleep" in stripped:
        warnings.append(
            Issue(
                i,
                1,
                "GO008",
                "time.Sleep w kodzie produkcyjnym - rozważ context.WithTimeout",
            )
        )


def _check_hardcoded_credentials(stripped: str, i: int, errors: List[Issue]) -> None:
    for pattern in ["password", "secret", "apikey", "api_key", "token"]:
        if re.search(rf'{pattern}\s*[:=]\s*["\'][^"\']+["\']', stripped, re.I):
            errors.append(
                Issue(
                    i,
                    1,
                    "GO009",
                    f"Hardcoded {pattern} - użyj zmiennych środowiskowych",
                )
            )


def _check_sql_injection(stripped: str, i: int, errors: List[Issue]) -> None:
    if "db.Query(" in stripped or "db.Exec(" in stripped:
        if "+" in stripped or "fmt.Sprintf" in stripped:
            errors.append(
                Issue(
                    i,
                    1,
                    "GO010",
                    "Potencjalny SQL injection - użyj prepared statements",
                )
            )


def _check_context_struct(
    stripped: str, i: int, code: str, warnings: List[Issue]
) -> None:
    if "context.Context" in stripped and "struct" in code[: code.find(stripped)]:
        warnings.append(
            Issue(i, 1, "GO011", "Context nie powinien być polem struktury")
        )


def _check_init_func(stripped: str, i: int, warnings: List[Issue]) -> None:
    if stripped.startswith("func init()"):
        warnings.append(Issue(i, 1, "GO012", "Unikaj init() - utrudnia testowanie"))


def _check_package_comment(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if stripped.startswith("package ") and i == 1:
        if not lines[0].strip().startswith("//"):
            warnings.append(Issue(i, 1, "GO013", "Brak komentarza pakietu"))


def _check_interface_any(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "interface{}" in stripped:
        warnings.append(Issue(i, 1, "GO014", "Użyj any zamiast interface{} (Go 1.18+)"))
        fixed = stripped.replace("interface{}", "any")
        fixes.append(Fix(i, "Zamieniono interface{} na any", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def analyze_go(code: str) -> AnalysisResult:
    """Analyze Go code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent_str = line[: len(line) - len(line.lstrip())]

        _check_unchecked_error(stripped, i, lines, warnings)
        _check_panic(stripped, i, code, warnings)
        _check_empty_error_msg(stripped, i, errors)
        _check_sprintf_no_args(stripped, i, warnings)
        _check_goroutine_no_sync(stripped, i, code, warnings)
        _check_slice_equality(stripped, i, errors)
        _check_defer_in_loop(stripped, i, lines, warnings)
        _check_time_sleep(stripped, i, warnings)
        _check_hardcoded_credentials(stripped, i, errors)
        _check_sql_injection(stripped, i, errors)
        _check_context_struct(stripped, i, code, warnings)
        _check_init_func(stripped, i, warnings)
        _check_package_comment(stripped, i, lines, warnings)
        _check_interface_any(stripped, i, indent_str, warnings, fixes, fixed_lines)

    return AnalysisResult("go", code, "\n".join(fixed_lines), errors, warnings, fixes)
