"""Systemd unit file analyzer."""

from typing import List, Optional
from ..analyzer import Issue, Fix, AnalysisResult


class _SystemdState:
    __slots__ = [
        "current_section",
        "has_description",
        "has_after",
        "has_restart",
        "has_user",
        "service_type",
    ]

    def __init__(self) -> None:
        self.current_section: Optional[str] = None
        self.has_description = False
        self.has_after = False
        self.has_restart = False
        self.has_user = False
        self.service_type: Optional[str] = None


def _check_description(
    stripped: str,
    i: int,
    state: _SystemdState,
    warnings: List[Issue],
) -> None:
    if stripped.startswith("Description="):
        state.has_description = True
        if len(stripped.split("=")[1].strip()) < 3:
            warnings.append(Issue(i, 1, "SYSTEMD001", "Opis usługi zbyt krótki"))


def _check_after(stripped: str, state: _SystemdState) -> None:
    if stripped.startswith("After="):
        state.has_after = True


def _check_restart(
    stripped: str,
    i: int,
    indent_str: str,
    state: _SystemdState,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith("Restart="):
        state.has_restart = True
        if stripped.split("=")[1].strip() == "no":
            warnings.append(
                Issue(i, 1, "SYSTEMD003", "Restart=no - usługa nie będzie restartowana")
            )
            fixed = "Restart=on-failure"
            fixes.append(
                Fix(i, "Zmieniono Restart=no na Restart=on-failure", stripped, fixed)
            )
            fixed_lines[i - 1] = indent_str + fixed


def _check_user(
    stripped: str, i: int, state: _SystemdState, warnings: List[Issue]
) -> None:
    if stripped.startswith("User="):
        state.has_user = True
        if stripped.split("=")[1].strip() == "root":
            warnings.append(
                Issue(
                    i,
                    1,
                    "SYSTEMD004",
                    "Usługa jako root - rozważ dedykowanego użytkownika",
                )
            )


def _check_service_type(
    stripped: str,
    i: int,
    indent_str: str,
    state: _SystemdState,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith("Type="):
        state.service_type = stripped.split("=")[1].strip()
        if state.service_type not in [
            "simple",
            "forking",
            "oneshot",
            "dbus",
            "notify",
            "idle",
        ]:
            errors.append(
                Issue(i, 1, "SYSTEMD006", f"Nieprawidłowy Type: {state.service_type}")
            )
            fixed = "Type=simple"
            fixes.append(Fix(i, "Zmieniono Type na simple", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_exec_start(stripped: str, i: int, errors: List[Issue]) -> None:
    if stripped.startswith("ExecStart="):
        cmd = stripped.split("=")[1].strip()
        if cmd and not cmd.startswith("/") and not cmd.startswith("-/"):
            errors.append(
                Issue(i, 1, "SYSTEMD007", "ExecStart musi używać absolutnej ścieżki")
            )


def _check_environment_secrets(stripped: str, i: int, errors: List[Issue]) -> None:
    if stripped.startswith("Environment="):
        for pattern in ["PASSWORD", "SECRET", "API_KEY", "TOKEN"]:
            if pattern in stripped.upper() and "${" not in stripped:
                errors.append(
                    Issue(
                        i,
                        1,
                        "SYSTEMD008",
                        f"Hardcoded {pattern} - użyj EnvironmentFile",
                    )
                )


def _check_restart_sec(
    stripped: str,
    i: int,
    lines: List[str],
    state: _SystemdState,
    warnings: List[Issue],
) -> None:
    if (
        state.has_restart
        and stripped.startswith("Restart=")
        and "always" in stripped.lower()
    ):
        if "RestartSec=" not in "\n".join(lines[i : i + 5]):
            warnings.append(Issue(i, 1, "SYSTEMD009", "Restart=always bez RestartSec"))


def _check_private_tmp(
    stripped: str,
    i: int,
    indent_str: str,
    state: _SystemdState,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if state.current_section == "Service" and stripped.startswith("PrivateTmp="):
        if "false" in stripped.lower():
            warnings.append(
                Issue(
                    i,
                    1,
                    "SYSTEMD010",
                    "PrivateTmp=false - rozważ true dla bezpieczeństwa",
                )
            )
            fixed = "PrivateTmp=true"
            fixes.append(Fix(i, "Zmieniono PrivateTmp na true", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_protect_system(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith("ProtectSystem="):
        if stripped.split("=")[1].strip() not in ["full", "strict", "true"]:
            warnings.append(
                Issue(i, 1, "SYSTEMD011", "ProtectSystem - rozważ strict lub full")
            )
            fixed = "ProtectSystem=strict"
            fixes.append(Fix(i, "Zmieniono ProtectSystem na strict", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_no_new_privileges(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith("NoNewPrivileges=") and "false" in stripped.lower():
        warnings.append(
            Issue(i, 1, "SYSTEMD012", "NoNewPrivileges=false - rozważ true")
        )
        fixed = "NoNewPrivileges=true"
        fixes.append(Fix(i, "Zmieniono NoNewPrivileges na true", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def _check_timeout_infinity(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "Timeout" in stripped and "infinity" in stripped.lower():
        warnings.append(
            Issue(i, 1, "SYSTEMD013", "Timeout=infinity może blokować system")
        )
        if stripped.startswith("TimeoutStartSec="):
            fixed = "TimeoutStartSec=60"
            fixes.append(Fix(i, "Zmieniono TimeoutStartSec na 60", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed
        elif stripped.startswith("TimeoutStopSec="):
            fixed = "TimeoutStopSec=60"
            fixes.append(Fix(i, "Zmieniono TimeoutStopSec na 60", stripped, fixed))
            fixed_lines[i - 1] = indent_str + fixed


def _check_kill_mode(
    stripped: str,
    i: int,
    indent_str: str,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith("KillMode=") and "none" in stripped.lower():
        warnings.append(
            Issue(i, 1, "SYSTEMD015", "KillMode=none - procesy mogą nie być zabijane")
        )
        fixed = "KillMode=control-group"
        fixes.append(Fix(i, "Zmieniono KillMode na control-group", stripped, fixed))
        fixed_lines[i - 1] = indent_str + fixed


def analyze_systemd(code: str) -> AnalysisResult:
    """Analyze systemd unit file for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()
    state = _SystemdState()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        indent_str = line[: len(line) - len(line.lstrip())]

        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            state.current_section = stripped[1:-1]
            continue

        _check_description(stripped, i, state, warnings)
        _check_after(stripped, state)
        _check_restart(stripped, i, indent_str, state, warnings, fixes, fixed_lines)
        _check_user(stripped, i, state, warnings)
        _check_service_type(stripped, i, indent_str, state, errors, fixes, fixed_lines)
        _check_exec_start(stripped, i, errors)
        _check_environment_secrets(stripped, i, errors)
        _check_restart_sec(stripped, i, lines, state, warnings)
        _check_private_tmp(stripped, i, indent_str, state, warnings, fixes, fixed_lines)
        _check_protect_system(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_no_new_privileges(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_timeout_infinity(stripped, i, indent_str, warnings, fixes, fixed_lines)
        _check_kill_mode(stripped, i, indent_str, warnings, fixes, fixed_lines)

    if not state.has_description:
        warnings.append(Issue(1, 1, "SYSTEMD001", "Brak Description w sekcji [Unit]"))
    if not state.has_restart:
        warnings.append(Issue(1, 1, "SYSTEMD003", "Brak polityki Restart"))
    if not state.has_user:
        warnings.append(
            Issue(1, 1, "SYSTEMD004", "Brak User= - usługa będzie działać jako root")
        )

    return AnalysisResult(
        "systemd", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
