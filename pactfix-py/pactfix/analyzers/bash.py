import re
from typing import List

from ..analyzer import Issue, Fix, AnalysisResult


def _brace_unbraced_bash_vars(line: str) -> str:
    out = []
    i = 0
    in_single = False
    in_double = False
    escaped = False
    while i < len(line):
        ch = line[i]
        if escaped:
            out.append(ch)
            escaped = False
            i += 1
            continue
        if ch == "\\":
            out.append(ch)
            escaped = True
            i += 1
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            out.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
            i += 1
            continue
        if ch == "$" and not in_single:
            if i + 1 < len(line) and line[i + 1] == "{":
                out.append(ch)
                i += 1
                continue
            if i + 1 < len(line) and re.match(r"[A-Za-z_]", line[i + 1]):
                j = i + 2
                while j < len(line) and re.match(r"[A-Za-z0-9_]", line[j]):
                    j += 1
                name = line[i + 1 : j]
                out.append("${" + name + "}")
                i = j
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def _split_bash_comment(line: str) -> tuple[str, str]:
    in_single = False
    in_double = False
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == "#" and not in_single and not in_double:
            return line[:i], line[i:]
    return line, ""


def _check_unbraced_vars(
    current_line: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
) -> str:
    stripped = current_line.strip()
    if (
        not stripped.startswith("#")
        and "$" in current_line
        and re.search(r"\$[A-Za-z_][A-Za-z0-9_]*", current_line)
    ):
        code_part, comment_part = _split_bash_comment(current_line)
        braced_code_part = _brace_unbraced_bash_vars(code_part)
        if braced_code_part != code_part:
            new_line = braced_code_part + comment_part
            warnings.append(
                Issue(
                    i,
                    1,
                    "BASH001",
                    "Zmienne bez klamerek: użyj składni ${VAR} (np. ${OUTPUT}/${HOST})",
                )
            )
            fixes.append(
                Fix(
                    i,
                    "Dodano klamerki do zmiennych",
                    current_line.strip(),
                    new_line.strip(),
                )
            )
            return new_line
    return current_line


def _check_cd_no_error_handling(
    current_line: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
) -> str:
    stripped = current_line.strip()
    if re.match(r"^cd\s+", stripped) and "||" not in stripped and "&&" not in stripped:
        warnings.append(
            Issue(i, 1, "SC2164", "cd bez obsługi błędów - użyj cd ... || exit")
        )
        fix_line = stripped + " || exit 1"
        fixes.append(Fix(i, "Dodano obsługę błędów dla cd", stripped, fix_line))
        return current_line.replace(stripped, fix_line)
    return current_line


def _check_read_without_r(current_line: str, i: int, warnings: List[Issue]) -> None:
    stripped = current_line.strip()
    if re.match(r"^read\s+", stripped) and "-r" not in stripped:
        warnings.append(
            Issue(i, 1, "SC2162", "read bez -r może interpretować backslashe")
        )


def _check_misplaced_quotes(
    current_line: str,
    i: int,
    errors: List[Issue],
    fixes: List[Fix],
) -> str:
    stripped = current_line.strip()
    quote_match = re.search(r'(\w+)="([^"]*)"(\w+)', stripped)
    if quote_match:
        errors.append(Issue(i, 1, "SC1073", "Błędne umiejscowienie cudzysłowów"))
        fixed = f'{quote_match.group(1)}="{quote_match.group(2)}{quote_match.group(3)}"'
        fixes.append(Fix(i, "Poprawiono cudzysłowy", quote_match.group(0), fixed))
        current_line = current_line.replace(quote_match.group(0), fixed)
        stripped = current_line.strip()
    if re.search(r'\$\([^)]*"[^)]*\)', stripped):
        errors.append(
            Issue(
                i,
                1,
                "SC1073",
                "Błędnie umieszczony cudzysłów wewnątrz podstawienia polecenia",
            )
        )
        fixed = re.sub(r'\$\(([^)]*)"([^)]*)\)', r'$(\1\2)"', stripped)
        fixes.append(Fix(i, "Poprawiono cudzysłów w podstawieniu", stripped, fixed))
        current_line = current_line.replace(stripped, fixed)
    return current_line


def analyze_bash(code: str) -> AnalysisResult:
    """Analyze Bash script."""
    errors, warnings, fixes = [], [], []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        current_line = fixed_lines[i - 1]
        current_line = _check_unbraced_vars(current_line, i, warnings, fixes)
        current_line = _check_cd_no_error_handling(current_line, i, warnings, fixes)
        _check_read_without_r(current_line, i, warnings)
        current_line = _check_misplaced_quotes(current_line, i, errors, fixes)
        fixed_lines[i - 1] = current_line

    return AnalysisResult("bash", code, "\n".join(fixed_lines), errors, warnings, fixes)
