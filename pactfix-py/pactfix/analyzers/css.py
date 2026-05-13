"""CSS analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


def _check_important(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "!important" in stripped:
        warnings.append(
            Issue(i, 1, "CSS001", "!important - rozważ zwiększenie specyficzności")
        )


def _check_id_selector(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^#\w+\s*\{", stripped):
        warnings.append(
            Issue(i, 1, "CSS002", "ID selector - rozważ klasę dla reużywalności")
        )


def _check_vendor_prefix(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    for prefix in ["-webkit-", "-moz-", "-ms-", "-o-"]:
        if prefix in stripped:
            prop = stripped.split(":")[0].replace(prefix, "").strip()
            if prop + ":" not in "\n".join(lines[max(0, i - 3) : i + 3]):
                warnings.append(
                    Issue(
                        i,
                        1,
                        "CSS003",
                        f"Vendor prefix bez standardowej właściwości: {prop}",
                    )
                )


def _check_hardcoded_color(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"#[0-9a-fA-F]{3,8}", stripped) and "var(--" not in stripped:
        warnings.append(Issue(i, 1, "CSS004", "Hardcoded kolor - rozważ CSS variable"))


def _check_font_size_px(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "font-size:" in stripped and "px" in stripped:
        warnings.append(Issue(i, 1, "CSS005", "font-size w px - rozważ rem lub em"))


def _check_zero_with_unit(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if re.search(r":\s*0(px|em|rem|%)", stripped):
        warnings.append(Issue(i, 1, "CSS006", "0 z jednostką - jednostka niepotrzebna"))
        fixed = re.sub(r":\s*0(px|em|rem|%)", ": 0", stripped)
        fixes.append(Fix(i, "Usunięto jednostkę przy 0", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_universal_selector(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.match(r"^\*\s*\{", stripped) or re.search(r"\s+\*\s*\{", stripped):
        warnings.append(
            Issue(i, 1, "CSS007", "Universal selector (*) - może wpływać na wydajność")
        )


def _check_empty_rule(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"\{\s*\}", stripped):
        warnings.append(Issue(i, 1, "CSS008", "Pusta reguła CSS"))


def _check_duplicate_property(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if ":" in stripped:
        prop = stripped.split(":")[0].strip()
        prev_lines = "\n".join(lines[max(0, i - 10) : i - 1])
        if f"{prop}:" in prev_lines and "{" not in prev_lines.split(f"{prop}:")[1][:20]:
            warnings.append(Issue(i, 1, "CSS009", f"Duplikat właściwości: {prop}"))


def _check_float(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "float:" in stripped:
        warnings.append(Issue(i, 1, "CSS010", "float - rozważ Flexbox lub Grid"))


def _check_outline_none(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "outline: none" in stripped or "outline:none" in stripped:
        warnings.append(
            Issue(
                i, 1, "CSS011", "outline: none - zapewnij alternatywny focus indicator"
            )
        )


def _check_high_z_index(stripped: str, i: int, warnings: List[Issue]) -> None:
    z_match = re.search(r"z-index:\s*(\d+)", stripped)
    if z_match and int(z_match.group(1)) > 100:
        warnings.append(
            Issue(
                i,
                1,
                "CSS012",
                f"Wysoki z-index: {z_match.group(1)} - rozważ mniejszą wartość",
            )
        )


def _check_calc_units(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "calc(" in stripped:
        calc_content = re.search(r"calc\(([^)]+)\)", stripped)
        if calc_content:
            units = re.findall(r"\d+(px|em|rem|%|vh|vw)", calc_content.group(1))
            if len(set(units)) > 2:
                warnings.append(
                    Issue(i, 1, "CSS013", "calc() z wieloma jednostkami - sprawdź")
                )


def _check_deprecated_props(stripped: str, i: int, warnings: List[Issue]) -> None:
    for prop in ["clip:", "zoom:"]:
        if prop in stripped:
            warnings.append(
                Issue(i, 1, "CSS014", f"Przestarzała właściwość: {prop[:-1]}")
            )


def _check_text_transform(stripped: str, i: int, warnings: List[Issue]) -> None:
    if (
        "text-transform: uppercase" in stripped
        or "text-transform:uppercase" in stripped
    ):
        warnings.append(
            Issue(
                i, 1, "CSS015", "text-transform: uppercase może mieć problemy z locale"
            )
        )


def analyze_css(code: str) -> AnalysisResult:
    """Analyze CSS for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent_str = line[: len(line) - len(line.lstrip())]

        if not stripped or stripped.startswith("/*") or stripped.startswith("*"):
            continue

        _check_important(stripped, i, warnings)
        _check_id_selector(stripped, i, warnings)
        _check_vendor_prefix(stripped, i, lines, warnings)
        _check_hardcoded_color(stripped, i, warnings)
        _check_font_size_px(stripped, i, warnings)
        _check_zero_with_unit(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_universal_selector(stripped, i, warnings)
        _check_empty_rule(stripped, i, warnings)
        _check_duplicate_property(stripped, i, lines, warnings)
        _check_float(stripped, i, warnings)
        _check_outline_none(stripped, i, warnings)
        _check_high_z_index(stripped, i, warnings)
        _check_calc_units(stripped, i, warnings)
        _check_deprecated_props(stripped, i, warnings)
        _check_text_transform(stripped, i, warnings)

    return AnalysisResult("css", code, "\n".join(fixed_lines), errors, warnings, fixes)
