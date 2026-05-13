"""Makefile analyzer."""

import re
from typing import List, Set
from ..analyzer import Issue, Fix, AnalysisResult


def _check_spaces_in_recipe(
    line: str,
    stripped: str,
    i: int,
    lines: List[str],
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if (
        i > 1
        and lines[i - 2].strip()
        and ":" in lines[i - 2]
        and not lines[i - 2].strip().startswith("#")
    ):
        if line.startswith(" ") and not line.startswith("\t") and stripped:
            if not stripped.startswith("#") and "=" not in stripped:
                errors.append(
                    Issue(i, 1, "MAKE001", "Użyj tabulatora zamiast spacji w recepcie")
                )
                fixed = "\t" + stripped
                fixes.append(Fix(i, "Zamieniono spacje na tabulator", line, fixed))
                fixed_lines[i - 1] = fixed


def _collect_target(stripped: str, targets: Set[str]) -> None:
    if (
        ":" in stripped
        and not stripped.startswith("#")
        and not stripped.startswith("\t")
    ):
        if "=" not in stripped and "::" not in stripped:
            target_match = re.match(r"^([a-zA-Z0-9_.-]+)\s*:", stripped)
            if target_match:
                targets.add(target_match.group(1))


def _collect_phony(stripped: str, phony_targets: Set[str]) -> None:
    if stripped.startswith(".PHONY:"):
        phony_targets.update(stripped.split(":")[1].strip().split())


def _check_hardcoded_path(stripped: str, i: int, warnings: List[Issue]) -> None:
    if re.search(r"/usr/local/|/home/\w+|C:\\", stripped):
        warnings.append(Issue(i, 1, "MAKE004", "Hardcoded path - użyj zmiennej"))


def _check_cd_no_and(stripped: str, i: int, warnings: List[Issue]) -> None:
    if stripped.startswith("\t") and "cd " in stripped and "&&" not in stripped:
        warnings.append(Issue(i, 1, "MAKE005", "cd bez && może kontynuować po błędzie"))


def _check_shell_simple(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "$(shell " in stripped and re.search(r"\$\(shell\s+(echo|cat|pwd)\s", stripped):
        warnings.append(
            Issue(i, 1, "MAKE006", "$(shell echo) - rozważ prostszą składnię")
        )


def _check_recursive_make(
    line: str,
    i: int,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "\tmake " in line and "$(MAKE)" not in line:
        warnings.append(
            Issue(i, 1, "MAKE007", "Użyj $(MAKE) zamiast make dla rekursji")
        )
        fixed = line.replace("\tmake ", "\t$(MAKE) ")
        fixes.append(Fix(i, "Zamieniono make na $(MAKE)", line, fixed))
        fixed_lines[i - 1] = fixed


def _check_rm_no_force(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "rm " in stripped and "-f" not in stripped and "-rf" not in stripped:
        warnings.append(
            Issue(i, 1, "MAKE011", "rm bez -f może przerwać na brakującym pliku")
        )


def _check_wildcard_prereqs(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "$(wildcard" in stripped and ":" in stripped:
        warnings.append(
            Issue(
                i, 1, "MAKE013", "$(wildcard) w prerequisites może być nieprzewidywalny"
            )
        )


def _check_double_colon(stripped: str, i: int, warnings: List[Issue]) -> None:
    if "::" in stripped and not stripped.startswith("#"):
        warnings.append(
            Issue(
                i, 1, "MAKE014", "Double-colon rule (::) - upewnij się że to zamierzone"
            )
        )


def analyze_makefile(code: str) -> AnalysisResult:
    """Analyze Makefile for common issues."""
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []
    lines = code.split("\n")
    fixed_lines = lines.copy()

    targets: Set[str] = set()
    phony_targets: Set[str] = set()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        _check_spaces_in_recipe(line, stripped, i, lines, errors, fixes, fixed_lines)
        _collect_target(stripped, targets)
        _collect_phony(stripped, phony_targets)
        _check_hardcoded_path(stripped, i, warnings)
        _check_cd_no_and(stripped, i, warnings)
        _check_shell_simple(stripped, i, warnings)
        _check_recursive_make(line, i, warnings, fixes, fixed_lines)
        _check_rm_no_force(stripped, i, warnings)
        _check_wildcard_prereqs(stripped, i, warnings)
        _check_double_colon(stripped, i, warnings)

        if "clean:" in stripped:
            targets.add("clean")

    phony_candidates = {
        "all",
        "clean",
        "install",
        "test",
        "build",
        "help",
        "check",
        "lint",
    }
    missing_phony = targets.intersection(phony_candidates) - phony_targets
    if missing_phony:
        warnings.append(
            Issue(
                1,
                1,
                "MAKE003",
                f".PHONY brakuje dla: {', '.join(sorted(missing_phony))}",
            )
        )

    if "clean" not in targets:
        warnings.append(Issue(1, 1, "MAKE012", "Brak targetu clean"))

    return AnalysisResult(
        "makefile", code, "\n".join(fixed_lines), errors, warnings, fixes
    )
