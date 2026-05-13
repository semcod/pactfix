"""HTML analyzer."""

import re
from typing import List, Optional
from ..analyzer import Issue, Fix, AnalysisResult


class _HtmlState:
    __slots__ = [
        "has_doctype",
        "has_lang",
        "has_charset",
        "has_viewport",
        "has_title",
        "in_head",
        "in_body",
        "head_open_idx",
    ]

    def __init__(self) -> None:
        self.has_doctype = False
        self.has_lang = False
        self.has_charset = False
        self.has_viewport = False
        self.has_title = False
        self.in_head = False
        self.in_body = False
        self.head_open_idx: Optional[int] = None


def _check_doctype(
    lower: str, i: int, state: _HtmlState, warnings: List[Issue]
) -> None:
    if "<!doctype" in lower:
        state.has_doctype = True
        if "html" not in lower:
            warnings.append(Issue(i, 1, "HTML001", "Użyj <!DOCTYPE html> dla HTML5"))


def _track_sections(lower: str, i: int, state: _HtmlState) -> None:
    if "<head" in lower:
        state.in_head = True
        if state.head_open_idx is None:
            state.head_open_idx = i - 1
    if "</head" in lower:
        state.in_head = False
    if "<body" in lower:
        state.in_body = True
    if "</body" in lower:
        state.in_body = False


def _check_html_lang(
    stripped: str,
    line: str,
    lower: str,
    i: int,
    state: _HtmlState,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "<html" not in lower:
        return
    if "lang=" not in lower:
        warnings.append(Issue(i, 1, "HTML002", "Brak atrybutu lang na <html>"))
        if "<html" in stripped and ">" in stripped:
            fixed = re.sub(
                r"<html(\s[^>]*)?>",
                lambda m: (
                    (m.group(0)[:-1] + ' lang="en">')
                    if "lang=" not in m.group(0).lower()
                    else m.group(0)
                ),
                line,
                count=1,
                flags=re.I,
            )
            if fixed != line:
                fixes.append(
                    Fix(i, 'Dodano lang="en" do <html>', line.rstrip(), fixed.rstrip())
                )
                fixed_lines[i - 1] = fixed
    else:
        state.has_lang = True


def _check_charset(lower: str, state: _HtmlState) -> None:
    if "charset=" in lower or "content-type" in lower:
        state.has_charset = True


def _check_viewport(lower: str, state: _HtmlState) -> None:
    if "viewport" in lower:
        state.has_viewport = True


def _check_title(lower: str, i: int, state: _HtmlState, warnings: List[Issue]) -> None:
    if "<title>" in lower:
        state.has_title = True
        if "</title>" in lower:
            content = re.search(r"<title>([^<]*)</title>", lower)
            if content and len(content.group(1).strip()) < 3:
                warnings.append(Issue(i, 1, "HTML005", "Tytuł strony zbyt krótki"))


def _check_img_alt(
    stripped: str,
    line: str,
    lower: str,
    i: int,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "<img" in lower and "alt=" not in lower:
        errors.append(Issue(i, 1, "HTML006", "<img> bez atrybutu alt - accessibility"))
        if "<img" in stripped and ">" in stripped:
            fixed = re.sub(r"<img\b", '<img alt=""', line, count=1, flags=re.I)
            if fixed != line:
                fixes.append(
                    Fix(i, 'Dodano alt="" do <img>', line.rstrip(), fixed.rstrip())
                )
                fixed_lines[i - 1] = fixed


def _check_inline_style(lower: str, i: int, warnings: List[Issue]) -> None:
    if 'style="' in lower:
        warnings.append(Issue(i, 1, "HTML007", "Inline style - przenieś do CSS"))


def _check_inline_event_handlers(lower: str, i: int, warnings: List[Issue]) -> None:
    for handler in ["onclick=", "onmouseover=", "onsubmit=", "onload=", "onerror="]:
        if handler in lower:
            warnings.append(
                Issue(i, 1, "HTML008", f"Inline {handler[:-1]} - użyj addEventListener")
            )


def _check_deprecated_tags(lower: str, i: int, warnings: List[Issue]) -> None:
    for tag in ["<font", "<center", "<marquee", "<blink", "<b>", "<i>"]:
        if tag in lower:
            warnings.append(
                Issue(i, 1, "HTML009", f"Przestarzały tag {tag} - użyj CSS")
            )


def _check_form_action(lower: str, i: int, warnings: List[Issue]) -> None:
    if "<form" in lower and "action=" not in lower:
        warnings.append(Issue(i, 1, "HTML010", "<form> bez atrybutu action"))


def _check_input_label(lower: str, i: int, warnings: List[Issue]) -> None:
    if "<input" in lower and "type=" in lower:
        if 'type="hidden"' not in lower and 'type="submit"' not in lower:
            if "id=" not in lower and "aria-label" not in lower:
                warnings.append(
                    Issue(i, 1, "HTML011", "<input> bez id/aria-label dla label")
                )


def _check_blank_target(
    line: str,
    lower: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if (
        'target="_blank"' in lower or "target='_blank'" in lower
    ) and "rel=" not in lower:
        warnings.append(
            Issue(i, 1, "HTML012", 'target="_blank" bez rel="noopener noreferrer"')
        )
        fixed = re.sub(
            r'target="_blank"',
            'target="_blank" rel="noopener noreferrer"',
            line,
            flags=re.I,
        )
        fixed = re.sub(
            r"target='_blank'",
            "target='_blank' rel='noopener noreferrer'",
            fixed,
            flags=re.I,
        )
        if fixed != line:
            fixes.append(
                Fix(
                    i, 'Dodano rel="noopener noreferrer"', line.rstrip(), fixed.rstrip()
                )
            )
            fixed_lines[i - 1] = fixed


def _check_http_link(lower: str, i: int, warnings: List[Issue]) -> None:
    if (
        ('href="http://' in lower or "href='http://" in lower)
        and "localhost" not in lower
        and "127.0.0.1" not in lower
    ):
        warnings.append(Issue(i, 1, "HTML013", "HTTP link - rozważ HTTPS"))


def _check_empty_href(lower: str, i: int, warnings: List[Issue]) -> None:
    if 'href=""' in lower or "href=''" in lower or 'href="#"' in lower:
        warnings.append(
            Issue(i, 1, "HTML014", "Pusty href - użyj button lub prawidłowego linku")
        )


def _check_table_headers(
    lower: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "<table" in lower:
        if "<th" not in "\n".join(lines[i : i + 10]).lower():
            warnings.append(Issue(i, 1, "HTML015", "<table> bez <th> - accessibility"))


def analyze_html(code: str) -> AnalysisResult:
    """Analyze HTML for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()
    state = _HtmlState()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        lower = stripped.lower()

        _check_doctype(lower, i, state, warnings)
        _track_sections(lower, i, state)
        _check_html_lang(stripped, line, lower, i, state, warnings, fixes, fixed_lines)
        _check_charset(lower, state)
        _check_viewport(lower, state)
        _check_title(lower, i, state, warnings)
        _check_img_alt(stripped, line, lower, i, errors, fixes, fixed_lines)
        _check_inline_style(lower, i, warnings)
        _check_inline_event_handlers(lower, i, warnings)
        _check_deprecated_tags(lower, i, warnings)
        _check_form_action(lower, i, warnings)
        _check_input_label(lower, i, warnings)
        _check_blank_target(line, lower, i, warnings, fixes, fixed_lines)
        _check_http_link(lower, i, warnings)
        _check_empty_href(lower, i, warnings)
        _check_table_headers(lower, i, lines, warnings)

    if not state.has_doctype:
        errors.append(Issue(1, 1, "HTML001", "Brak <!DOCTYPE html>"))
        fixed_lines.insert(0, "<!DOCTYPE html>")
        fixes.append(Fix(1, "Dodano <!DOCTYPE html>", "", "<!DOCTYPE html>"))

    if not state.has_charset:
        warnings.append(Issue(1, 1, "HTML003", "Brak deklaracji charset"))
        insert_at = state.head_open_idx + 1 if state.head_open_idx is not None else 0
        fixed_lines.insert(insert_at, '    <meta charset="utf-8">')
        fixes.append(
            Fix(1, 'Dodano <meta charset="utf-8">', "", '<meta charset="utf-8">')
        )

    if not state.has_viewport:
        warnings.append(
            Issue(1, 1, "HTML004", "Brak meta viewport - problemy na mobile")
        )
        insert_at = state.head_open_idx + 2 if state.head_open_idx is not None else 0
        fixed_lines.insert(
            insert_at,
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        )
        fixes.append(
            Fix(
                1,
                "Dodano meta viewport",
                "",
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            )
        )

    if not state.has_title:
        warnings.append(Issue(1, 1, "HTML005", "Brak <title>"))
        insert_at = state.head_open_idx + 3 if state.head_open_idx is not None else 0
        fixed_lines.insert(insert_at, "    <title>Document</title>")
        fixes.append(
            Fix(1, "Dodano <title>Document</title>", "", "<title>Document</title>")
        )

    return AnalysisResult("html", code, "\n".join(fixed_lines), errors, warnings, fixes)
