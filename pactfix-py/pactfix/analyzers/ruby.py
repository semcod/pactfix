"""Ruby code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_nil_comparison(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "== nil" in stripped:
        warnings.append(Issue(i, 1, "RUBY001", "Użyj .nil? zamiast == nil"))
        fixed = stripped.replace("== nil", ".nil?")
        fixes.append(Fix(i, "Zamieniono == nil na .nil?", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_bare_rescue(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\s*rescue\s*$", stripped):
        warnings.append(
            Issue(i, 1, "RUBY002", "rescue bez klasy wyjątku łapie StandardError")
        )


def _check_rescue_exception(stripped: str, i: int, errors: List[Issue]) -> None:
    if "rescue Exception" in stripped:
        errors.append(
            Issue(
                i, 1, "RUBY003", "rescue Exception łapie także SystemExit i Interrupt"
            )
        )


def _check_puts_print(stripped: str, i: int, warnings: List[Issue]) -> None:
    if stripped.startswith("puts ") or stripped.startswith("print "):
        warnings.append(Issue(i, 1, "RUBY004", "puts/print - użyj Loggera"))


def _check_hardcoded_credentials(stripped: str, i: int, errors: List[Issue]) -> None:
    for pattern in ["password", "secret", "api_key", "token"]:
        if re.search(rf'{pattern}\s*=\s*["\'][^"\']+["\']', stripped, re.I):
            errors.append(Issue(i, 1, "RUBY005", f"Hardcoded {pattern}"))


def _check_eval(stripped: str, i: int, errors: List[Issue]) -> None:
    if "eval(" in stripped or "eval " in stripped:
        errors.append(Issue(i, 1, "RUBY006", "eval() jest niebezpieczne"))


def _check_send(stripped: str, i: int, warnings: List[Issue]) -> None:
    if ".send(" in stripped:
        warnings.append(
            Issue(
                i, 1, "RUBY007", "send() z zewnętrznym inputem może być niebezpieczne"
            )
        )


def _check_sql_injection(stripped: str, i: int, errors: List[Issue]) -> None:
    if ".where(" in stripped or ".find_by_sql" in stripped:
        if "#{" in stripped or "+" in stripped:
            errors.append(
                Issue(i, 1, "RUBY008", "Potencjalny SQL injection - użyj placeholderów")
            )


def _check_class_variables(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "@@" in stripped:
        warnings.append(
            Issue(
                i, 1, "RUBY009", "Zmienne klasowe @@ - rozważ class instance variables"
            )
        )


def _check_unfreeze_constant(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if re.match(r'^[A-Z_]+\s*=\s*["\']', stripped) and ".freeze" not in stripped:
        warnings.append(Issue(i, 1, "RUBY010", "String constant bez .freeze"))
        fixed = stripped.rstrip() + ".freeze"
        fixes.append(Fix(i, "Dodano .freeze do stałej", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_proc_return(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "proc" in "\n".join(lines[max(0, i - 5) : i]).lower() and "return " in stripped:
        warnings.append(
            Issue(
                i, 1, "RUBY011", "return w Proc może powodować problemy - użyj lambda"
            )
        )


def _check_method_length(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if stripped.startswith("def "):
        end_count = 0
        for j in range(i, min(i + 50, len(lines))):
            if lines[j].strip() == "end":
                end_count = j - i
                break
        if end_count > 20:
            warnings.append(
                Issue(i, 1, "RUBY012", "Metoda zbyt długa - rozważ refactoring")
            )


def _check_begin_rescue(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "begin" in stripped and "rescue" in "\n".join(lines[i : i + 5]):
        warnings.append(
            Issue(i, 1, "RUBY013", "begin/rescue do kontroli przepływu - użyj warunku")
        )


def _check_double_negation(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "!!" in stripped:
        warnings.append(
            Issue(i, 1, "RUBY014", "Podwójna negacja - użyj .present? lub !!var")
        )


def analyze_ruby(code: str) -> AnalysisResult:
    """Analyze Ruby code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent_str = line[: len(line) - len(line.lstrip())]

        _check_nil_comparison(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_bare_rescue(stripped, i, warnings)
        _check_rescue_exception(stripped, i, errors)
        _check_puts_print(stripped, i, warnings)
        _check_hardcoded_credentials(stripped, i, errors)
        _check_eval(stripped, i, errors)
        _check_send(stripped, i, warnings)
        _check_sql_injection(stripped, i, errors)
        _check_class_variables(stripped, i, warnings)
        _check_unfreeze_constant(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_proc_return(stripped, i, lines, warnings)
        _check_method_length(stripped, i, lines, warnings)
        _check_begin_rescue(stripped, i, lines, warnings)
        _check_double_negation(stripped, i, warnings)

    return AnalysisResult("ruby", code, "\n".join(fixed_lines), errors, warnings, fixes)
