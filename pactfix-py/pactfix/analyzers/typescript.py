"""TypeScript code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_any_type(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r":\s*any\b", stripped) or re.search(r"<any>", stripped):
        warnings.append(
            Issue(i, 1, "TS001", "Unikaj typu any - użyj unknown lub konkretnego typu")
        )


def _check_non_null_assertion(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "!" in stripped and re.search(r"\w+!\.", stripped):
        warnings.append(
            Issue(
                i,
                1,
                "TS002",
                "Nadużycie non-null assertion (!) - rozważ optional chaining",
            )
        )


def _check_var_keyword(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if re.search(r"\bvar\s+\w+", stripped):
        warnings.append(Issue(i, 1, "TS003", "Użyj let/const zamiast var"))
        fixed = re.sub(r"\bvar\b", "let", stripped)
        fixes.append(Fix(i, "Zamieniono var na let", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_loose_equality(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if re.search(r"[^=!]={2}[^=]", stripped) and "===" not in stripped:
        warnings.append(Issue(i, 1, "TS004", "Użyj === zamiast =="))
        fixed = re.sub(r"([^=!])={2}([^=])", r"\1===\2", stripped)
        fixes.append(Fix(i, "Zamieniono == na ===", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_console_log(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "console.log" in stripped:
        warnings.append(Issue(i, 1, "TS005", "console.log w kodzie produkcyjnym"))


def _check_eval(stripped: str, i: int, errors: List[Issue]) -> None:
    if "eval(" in stripped:
        errors.append(Issue(i, 1, "TS006", "eval() jest niebezpieczne - unikaj"))


def _check_ts_ignore(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "@ts-ignore" in stripped and "//" in stripped:
        if len(stripped.split("@ts-ignore")[1].strip()) < 5:
            warnings.append(Issue(i, 1, "TS007", "@ts-ignore bez wyjaśnienia"))


def _check_empty_interface(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\s*interface\s+\w+\s*\{\s*\}\s*$", stripped):
        warnings.append(
            Issue(
                i,
                1,
                "TS008",
                "Pusty interface - użyj type alias lub Record<string, never>",
            )
        )


def _check_missing_return_type(stripped: str, i: int, warnings: List[Issue]) -> None:
    if (
        re.search(r"function\s+\w+\s*\([^)]*\)\s*\{", stripped)
        and ":" not in stripped.split("{")[0]
    ):
        warnings.append(Issue(i, 1, "TS009", "Funkcja bez typu zwracanego"))


def _check_async_without_await(
    stripped: str, i: int, code: str, warnings: List[Issue]
) -> None:
    if "async " in stripped and "await" not in code:
        warnings.append(Issue(i, 1, "TS010", "Funkcja async bez await"))


def _check_promise_antipattern(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "new Promise" in stripped and "async" in stripped:
        warnings.append(Issue(i, 1, "TS011", "Niepotrzebny Promise w async function"))


def _check_object_type(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r":\s*Object\b", stripped):
        warnings.append(Issue(i, 1, "TS012", "Użyj object lub Record zamiast Object"))


def _check_wrapper_types(stripped: str, i: int, warnings: List[Issue]) -> None:
    for wrapper in ["String", "Number", "Boolean"]:
        if re.search(rf":\s*{wrapper}\b", stripped):
            warnings.append(
                Issue(i, 1, "TS013", f"Użyj {wrapper.lower()} zamiast {wrapper}")
            )


def _check_unused_imports(
    stripped: str, i: int, code: str, warnings: List[Issue]
) -> None:
    if stripped.startswith("import ") and " from " in stripped:
        match = re.search(r"import\s+\{([^}]+)\}", stripped)
        if match:
            imports = [x.strip() for x in match.group(1).split(",")]
            for imp in imports:
                if imp and imp not in code.replace(stripped, ""):
                    warnings.append(
                        Issue(i, 1, "TS014", f"Potencjalnie nieużywany import: {imp}")
                    )


def analyze_typescript(code: str) -> AnalysisResult:
    """Analyze TypeScript code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent_str = line[: len(line) - len(line.lstrip())]

        _check_any_type(stripped, i, warnings)
        _check_non_null_assertion(stripped, i, warnings)
        _check_var_keyword(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_loose_equality(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_console_log(stripped, i, warnings)
        _check_eval(stripped, i, errors)
        _check_ts_ignore(stripped, i, warnings)
        _check_empty_interface(stripped, i, warnings)
        _check_missing_return_type(stripped, i, warnings)
        _check_async_without_await(stripped, i, code, warnings)
        _check_promise_antipattern(stripped, i, warnings)
        _check_object_type(stripped, i, warnings)
        _check_wrapper_types(stripped, i, warnings)
        _check_unused_imports(stripped, i, code, warnings)

    return AnalysisResult(
        "typescript", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
