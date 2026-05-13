"""Rust code analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_unwrap(stripped: str, i: int, warnings: List[Issue]) -> None:
    if ".unwrap()" in stripped:
        warnings.append(
            Issue(i, 1, "RUST001", "unwrap() może spowodować panic - użyj ? lub match")
        )


def _check_expect(stripped: str, i: int, warnings: List[Issue]) -> None:
    if '.expect("' in stripped:
        match = re.search(r'\.expect\("([^"]*)"\)', stripped)
        if match and len(match.group(1)) < 10:
            warnings.append(
                Issue(
                    i,
                    1,
                    "RUST002",
                    "expect() z krótkim opisem - dodaj szczegółową wiadomość",
                )
            )


def _check_clone(stripped: str, i: int, warnings: List[Issue]) -> None:
    if ".clone()" in stripped:
        warnings.append(
            Issue(i, 1, "RUST003", "clone() może być kosztowne - rozważ borrowing")
        )


def _check_panic(stripped: str, i: int, code: str, warnings: List[Issue]) -> None:
    if "panic!" in stripped and "fn main" not in code[: code.find(stripped)]:
        warnings.append(
            Issue(i, 1, "RUST004", "panic! w kodzie biblioteki - zwróć Result")
        )


def _check_unnecessary_mut(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "let mut " in stripped:
        var_match = re.search(r"let mut (\w+)", stripped)
        if var_match:
            var_name = var_match.group(1)
            rest_of_code = "\n".join(lines[i:])
            if (
                f"{var_name} =" not in rest_of_code
                and f"{var_name}." not in rest_of_code
            ):
                warnings.append(
                    Issue(i, 1, "RUST005", f"Niepotrzebny mut dla {var_name}")
                )


def _check_string_param(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"fn\s+\w+\([^)]*:\s*String[,)]", stripped):
        warnings.append(
            Issue(i, 1, "RUST006", "Rozważ &str zamiast String w parametrach funkcji")
        )


def _check_box_error(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "Box<dyn Error>" in stripped and "Send" not in stripped:
        warnings.append(
            Issue(i, 1, "RUST007", "Box<dyn Error> - rozważ dodanie Send + Sync")
        )


def _check_println(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "println!" in stripped and "debug" not in stripped.lower():
        warnings.append(
            Issue(i, 1, "RUST008", "println! zamiast log/tracing - użyj proper logging")
        )


def _check_hardcoded_secrets(stripped: str, i: int, errors: List[Issue]) -> None:
    for pattern in ["password", "secret", "api_key", "token"]:
        if re.search(rf'{pattern}\s*=\s*"[^"]+', stripped, re.I):
            errors.append(Issue(i, 1, "RUST009", f"Hardcoded {pattern}"))


def _check_unsafe(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "unsafe {" in stripped or "unsafe fn" in stripped:
        prev_line = lines[i - 2].strip() if i > 1 else ""
        if not prev_line.startswith("//") and "SAFETY:" not in prev_line:
            warnings.append(Issue(i, 1, "RUST010", "unsafe bez komentarza SAFETY:"))


def _check_empty_match(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "=> {}" in stripped or "=> ()" in stripped:
        warnings.append(
            Issue(i, 1, "RUST011", "Pusty match arm - dodaj komentarz lub obsługę")
        )


def _check_to_string(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r'"[^"]*"\.to_string\(\)', stripped):
        warnings.append(
            Issue(
                i,
                1,
                "RUST012",
                'Użyj String::from() lub .into() zamiast "".to_string()',
            )
        )


def _check_redundant_closure(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"\|\w+\|\s+\w+\(\w+\)", stripped):
        warnings.append(
            Issue(
                i,
                1,
                "RUST013",
                "Zbędna closure - możesz przekazać funkcję bezpośrednio",
            )
        )


def _check_must_use(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if stripped.startswith("pub fn") and "-> Result" in stripped:
        prev_lines = "\n".join(lines[max(0, i - 3) : i - 1])
        if "#[must_use]" not in prev_lines:
            warnings.append(
                Issue(
                    i, 1, "RUST014", "Rozważ #[must_use] dla funkcji zwracającej Result"
                )
            )


def analyze_rust(code: str) -> AnalysisResult:
    """Analyze Rust code for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_unwrap(stripped, i, warnings)
        _check_expect(stripped, i, warnings)
        _check_clone(stripped, i, warnings)
        _check_panic(stripped, i, code, warnings)
        _check_unnecessary_mut(stripped, i, lines, warnings)
        _check_string_param(stripped, i, warnings)
        _check_box_error(stripped, i, warnings)
        _check_println(stripped, i, warnings)
        _check_hardcoded_secrets(stripped, i, errors)
        _check_unsafe(stripped, i, lines, warnings)
        _check_empty_match(stripped, i, warnings)
        _check_to_string(stripped, i, warnings)
        _check_redundant_closure(stripped, i, warnings)
        _check_must_use(stripped, i, lines, warnings)

    return AnalysisResult("rust", code, "\n".join(fixed_lines), errors, warnings, fixes)
