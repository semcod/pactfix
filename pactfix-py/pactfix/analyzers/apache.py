"""Apache config analyzer."""

import re
from typing import List
from ..analyzer import Issue, Fix, AnalysisResult


class _ApacheState:
    __slots__ = [
        "has_ssl",
        "has_security_headers",
        "server_tokens_set",
        "directory_listing",
    ]

    def __init__(self) -> None:
        self.has_ssl = False
        self.has_security_headers = False
        self.server_tokens_set = False
        self.directory_listing = False


def _check_server_tokens(
    stripped: str,
    i: int,
    indent_str: str,
    state: _ApacheState,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.lower().startswith("servertokens"):
        state.server_tokens_set = True
        if "Prod" not in stripped and "ProductOnly" not in stripped:
            warnings.append(
                Issue(i, 1, "APACHE001", "ServerTokens powinien być ustawiony na Prod")
            )
            fixed = "ServerTokens Prod"
            fixes.append(Fix(i, "Ustawiono ServerTokens na Prod", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_server_signature(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.lower().startswith("serversignature") and "Off" not in stripped:
        warnings.append(Issue(i, 1, "APACHE002", "ServerSignature powinien być Off"))
        fixed = "ServerSignature Off"
        fixes.append(Fix(i, "Ustawiono ServerSignature na Off", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_trace_enable(
    stripped: str,
    i: int,
    indent_str: str,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.lower().startswith("traceenable") and "Off" not in stripped:
        errors.append(
            Issue(i, 1, "APACHE003", "TraceEnable powinien być Off (TRACE attack)")
        )
        fixed = "TraceEnable Off"
        fixes.append(Fix(i, "Ustawiono TraceEnable na Off", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_directory_indexes(
    stripped: str,
    i: int,
    indent_str: str,
    state: _ApacheState,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "Options" in stripped and "+Indexes" in stripped:
        state.directory_listing = True
        warnings.append(
            Issue(i, 1, "APACHE004", "Directory listing włączony - usuń +Indexes")
        )
        fixed = stripped.replace("+Indexes", "").replace("  ", " ").strip()
        fixes.append(Fix(i, "Usunięto +Indexes z Options", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_allow_override(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.lower().startswith("allowoverride") and "All" in stripped:
        warnings.append(
            Issue(i, 1, "APACHE005", "AllowOverride All - rozważ bardziej restrykcyjne")
        )
        fixed = "AllowOverride None"
        fixes.append(Fix(i, "Ustawiono AllowOverride na None", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_ssl_engine(stripped: str, state: _ApacheState) -> None:
    if "SSLEngine" in stripped and "on" in stripped.lower():
        state.has_ssl = True


def _check_weak_ssl_protocols(
    stripped: str,
    i: int,
    indent_str: str,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "SSLProtocol" in stripped:
        if "SSLv2" in stripped or "SSLv3" in stripped or "TLSv1 " in stripped:
            errors.append(
                Issue(i, 1, "APACHE007", "Słabe protokoły SSL - użyj TLSv1.2+")
            )
            fixed = "SSLProtocol -all +TLSv1.2 +TLSv1.3"
            fixes.append(Fix(i, "Ustawiono bezpieczne SSLProtocol", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_weak_ciphers(
    stripped: str,
    i: int,
    indent_str: str,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "SSLCipherSuite" in stripped:
        if any(c in stripped.upper() for c in ["RC4", "MD5", "DES", "EXPORT", "NULL"]):
            errors.append(Issue(i, 1, "APACHE008", "Słabe szyfry w SSLCipherSuite"))
            fixed = "SSLCipherSuite HIGH:!aNULL:!MD5:!3DES:!RC4"
            fixes.append(Fix(i, "Ustawiono bezpieczne SSLCipherSuite", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_security_headers(stripped: str, state: _ApacheState) -> None:
    if "Header" in stripped:
        state.has_security_headers = True


def _check_document_root(stripped: str, i: int, warnings: List[Issue]) -> None:
    if stripped.lower().startswith("documentroot"):
        path = stripped.split()[1] if len(stripped.split()) > 1 else ""
        if path and not path.startswith("/var/www") and not path.startswith("/srv"):
            warnings.append(
                Issue(i, 1, "APACHE010", "DocumentRoot w niestandardowej lokalizacji")
            )


def _check_timeout(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.lower().startswith("timeout"):
        timeout_val = re.search(r"\d+", stripped)
        if timeout_val and int(timeout_val.group()) > 300:
            warnings.append(
                Issue(i, 1, "APACHE011", "Timeout > 300s - może powodować DoS")
            )
            fixed = "Timeout 60"
            fixes.append(Fix(i, "Ustawiono Timeout na 60", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_keepalive(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.lower().startswith("keepalive") and "Off" in stripped:
        warnings.append(Issue(i, 1, "APACHE012", "KeepAlive Off - rozważ włączenie"))
        fixed = "KeepAlive On"
        fixes.append(Fix(i, "Ustawiono KeepAlive na On", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_x_powered_by(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "Header" in stripped and "X-Powered-By" in stripped:
        warnings.append(Issue(i, 1, "APACHE013", "X-Powered-By ujawnia technologię"))
        if stripped.lower().startswith("header") and "set" in stripped.lower():
            fixed = "Header unset X-Powered-By"
            fixes.append(
                Fix(i, "Zmieniono na Header unset X-Powered-By", stripped, fixed)
            )
            fixed_lines[i - 1] = indent_str + fixed


def _check_directory_require(
    stripped: str, i: int, lines: List[str], warnings: List[Issue]
) -> None:
    if "<Directory" in stripped and "Require" not in "\n".join(lines[i : i + 10]):
        warnings.append(Issue(i, 1, "APACHE014", "Directory bez Require directive"))


def _insert_directory_require(fixed_lines: List[str], fixes: List[Fix]) -> None:
    in_directory = False
    dir_start_idx = None
    dir_indent = ""
    for idx, line in enumerate(fixed_lines):
        stripped = line.strip()
        if stripped.startswith("<Directory"):
            in_directory = True
            dir_start_idx = idx
            m = re.match(r"^\s*", line)
            dir_indent = m.group(0) if m else ""
            continue
        if in_directory and stripped.startswith("</Directory"):
            block = (
                "\n".join(fixed_lines[dir_start_idx : idx + 1])
                if dir_start_idx is not None
                else ""
            )
            if "Require" not in block:
                insert_line = dir_indent + "    Require all granted"
                fixed_lines.insert(idx, insert_line)
                fixes.append(
                    Fix(
                        idx + 1,
                        "Dodano Require all granted w <Directory>",
                        "",
                        insert_line.strip(),
                    )
                )
            in_directory = False
            dir_start_idx = None
            dir_indent = ""


def _insert_ssl_vhost_headers(fixed_lines: List[str], fixes: List[Fix]) -> None:
    in_ssl_vhost = False
    ssl_vhost_indent = ""
    for idx, line in enumerate(fixed_lines):
        stripped = line.strip()
        if stripped.lower().startswith("<virtualhost") and ":443" in stripped:
            in_ssl_vhost = True
            m = re.match(r"^\s*", line)
            ssl_vhost_indent = m.group(0) if m else ""
            continue
        if in_ssl_vhost and stripped.lower().startswith("</virtualhost"):
            block = "\n".join(fixed_lines[max(0, idx - 80) : idx + 1])
            if "SSLHonorCipherOrder" not in block:
                insert_line = ssl_vhost_indent + "    SSLHonorCipherOrder on"
                fixed_lines.insert(idx, insert_line)
                fixes.append(
                    Fix(
                        idx + 1,
                        "Dodano SSLHonorCipherOrder on",
                        "",
                        insert_line.strip(),
                    )
                )
            if (
                "Header always set X-Frame-Options" not in block
                and "Header set X-Frame-Options" not in block
            ):
                insert_lines = [
                    ssl_vhost_indent
                    + '    Header always set X-Frame-Options "SAMEORIGIN"',
                    ssl_vhost_indent
                    + '    Header always set X-Content-Type-Options "nosniff"',
                    ssl_vhost_indent
                    + '    Header always set Referrer-Policy "strict-origin-when-cross-origin"',
                    ssl_vhost_indent
                    + '    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"',
                ]
                for j, ins in enumerate(insert_lines):
                    fixed_lines.insert(idx + j, ins)
                fixes.append(
                    Fix(
                        idx + 1,
                        "Dodano podstawowe security headers",
                        "",
                        "Header always set ...",
                    )
                )
            in_ssl_vhost = False
            ssl_vhost_indent = ""


def analyze_apache(code: str) -> AnalysisResult:
    """Analyze Apache configuration for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()
    state = _ApacheState()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent_str = line[: len(line) - len(line.lstrip())]

        if not stripped or stripped.startswith("#"):
            continue

        _check_server_tokens(
            stripped, i, indent_str, state, warnings, fixes, fixed_lines
        )
        _check_server_signature(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_trace_enable(stripped, i, indent_str, errors, fixes, fixed_lines)
        _check_directory_indexes(
            stripped, i, indent_str, state, warnings, fixes, fixed_lines
        )
        _check_allow_override(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_ssl_engine(stripped, state)
        _check_weak_ssl_protocols(stripped, i, indent_str, errors, fixes, fixed_lines)
        _check_weak_ciphers(stripped, i, indent_str, errors, fixes, fixed_lines)
        _check_security_headers(stripped, state)
        _check_document_root(stripped, i, warnings)
        _check_timeout(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_keepalive(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_x_powered_by(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_directory_require(stripped, i, lines, warnings)

    if not state.server_tokens_set:
        warnings.append(
            Issue(
                1,
                1,
                "APACHE001",
                "ServerTokens nie ustawiony - domyślnie ujawnia wersję",
            )
        )
    if state.has_ssl and not state.has_security_headers:
        warnings.append(
            Issue(1, 1, "APACHE009", "SSL włączone ale brak security headers")
        )

    _insert_directory_require(fixed_lines, fixes)
    _insert_ssl_vhost_headers(fixed_lines, fixes)

    return AnalysisResult(
        "apache", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
