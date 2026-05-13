from typing import List, Optional, Set

from ..analyzer import Issue, Fix, AnalysisResult


class _DockerState:
    __slots__ = ["has_user", "has_healthcheck", "base_image", "env_vars"]

    def __init__(self) -> None:
        self.has_user = False
        self.has_healthcheck = False
        self.base_image: Optional[str] = None
        self.env_vars: Set[str] = set()


def _check_from(
    stripped: str,
    upper: str,
    i: int,
    state: _DockerState,
    warnings: List[Issue],
    fixes: List[Fix],
) -> None:
    if upper.startswith("FROM "):
        state.base_image = stripped[5:].strip().split()[0]
        if ":latest" in state.base_image or (
            ":" not in state.base_image and "@" not in state.base_image
        ):
            warnings.append(
                Issue(
                    i,
                    1,
                    "DOCKER001",
                    f"Użyj konkretnego tagu zamiast :latest dla {state.base_image}",
                )
            )
            if ":" not in state.base_image:
                fixed = stripped + ":latest  # TODO: specify version"
                fixes.append(Fix(i, "Dodano placeholder dla wersji", stripped, fixed))


def _collect_user(upper: str, state: _DockerState) -> None:
    if upper.startswith("USER "):
        state.has_user = True


def _collect_healthcheck(upper: str, state: _DockerState) -> None:
    if upper.startswith("HEALTHCHECK "):
        state.has_healthcheck = True


def _collect_env(stripped: str, upper: str, state: _DockerState) -> None:
    if upper.startswith("ENV "):
        parts = stripped[4:].split("=")
        if parts:
            state.env_vars.add(parts[0].strip())


def _check_apt_get(stripped: str, upper: str, i: int, warnings: List[Issue]) -> None:
    if upper.startswith("RUN ") and "apt-get install" in stripped:
        if "rm -rf /var/lib/apt/lists" not in stripped and "&&" not in stripped:
            warnings.append(
                Issue(i, 1, "DOCKER002", "apt-get install bez czyszczenia cache")
            )
        if "apt-get update" not in stripped:
            warnings.append(
                Issue(
                    i, 1, "DOCKER003", "apt-get install bez update w tej samej warstwie"
                )
            )


def _check_add_vs_copy(
    stripped: str,
    line: str,
    upper: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if upper.startswith("ADD ") and "http" not in stripped and ".tar" not in stripped:
        warnings.append(
            Issue(i, 1, "DOCKER004", "Użyj COPY zamiast ADD dla lokalnych plików")
        )
        fixed = "COPY" + stripped[3:]
        fixes.append(Fix(i, "Zamieniono ADD na COPY", stripped, fixed))
        fixed_lines[i - 1] = line.replace(stripped, fixed)


def _check_workdir(
    stripped: str,
    line: str,
    upper: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if upper.startswith("WORKDIR ") and not stripped[8:].strip().startswith("/"):
        warnings.append(
            Issue(i, 1, "DOCKER008", "WORKDIR powinien używać ścieżki absolutnej")
        )
        fixed = "WORKDIR /" + stripped[8:].strip()
        fixes.append(Fix(i, "Dodano / do WORKDIR", stripped, fixed))
        fixed_lines[i - 1] = line.replace(stripped, fixed)


def _check_hardcoded_secret(
    stripped: str, upper: str, i: int, errors: List[Issue]
) -> None:
    for pattern in ["PASSWORD=", "SECRET=", "API_KEY=", "TOKEN="]:
        if pattern in upper and "ARG" not in upper:
            errors.append(
                Issue(
                    i, 1, "DOCKER007", "Hardcoded secret - użyj build args lub secrets"
                )
            )


def _check_cmd_exec_form(
    stripped: str, upper: str, i: int, warnings: List[Issue]
) -> None:
    if (
        upper.startswith("CMD ") or upper.startswith("ENTRYPOINT ")
    ) and "[" not in stripped:
        warnings.append(
            Issue(i, 1, "DOCKER006", "Użyj formy exec (JSON array) dla CMD/ENTRYPOINT")
        )


def analyze_dockerfile(code: str) -> AnalysisResult:
    """Analyze Dockerfile."""
    errors, warnings, fixes = [], [], []
    lines = code.split("\n")
    fixed_lines = lines.copy()
    state = _DockerState()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        upper = stripped.upper()

        _check_from(stripped, upper, i, state, warnings, fixes)
        _collect_user(upper, state)
        _collect_healthcheck(upper, state)
        _collect_env(stripped, upper, state)
        _check_apt_get(stripped, upper, i, warnings)
        _check_add_vs_copy(stripped, line, upper, i, warnings, fixes, fixed_lines)
        _check_workdir(stripped, line, upper, i, warnings, fixes, fixed_lines)
        _check_hardcoded_secret(stripped, upper, i, errors)
        _check_cmd_exec_form(stripped, upper, i, warnings)

    if not state.has_user:
        warnings.append(
            Issue(1, 1, "DOCKER009", "Brak USER - kontener będzie działał jako root")
        )
    if not state.has_healthcheck and state.base_image:
        warnings.append(Issue(1, 1, "DOCKER010", "Brak HEALTHCHECK"))

    context = {"base_image": state.base_image, "env_vars": list(state.env_vars)}
    return AnalysisResult(
        "dockerfile", code, "\n".join(fixed_lines), errors, warnings, fixes, context
    )
