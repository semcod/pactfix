import re
from typing import List, Dict, Optional, Set

from ..analyzer import Issue, Fix, AnalysisResult


class _TerraformState:
    __slots__ = [
        "current_resource",
        "resource_start_line",
        "resources",
        "variables_defined",
        "variables_used",
        "providers",
    ]

    def __init__(self) -> None:
        self.current_resource: Optional[Dict[str, str]] = None
        self.resource_start_line: int = 0
        self.resources: List[Dict[str, str]] = []
        self.variables_defined: Set[str] = set()
        self.variables_used: Set[str] = set()
        self.providers: List[str] = []


def _collect_resource_start(stripped: str, i: int, state: _TerraformState) -> bool:
    if stripped.startswith('resource "'):
        m = re.search(r'resource\s+"([^"]+)"\s+"([^"]+)"', stripped)
        if m:
            state.current_resource = {
                "type": m.group(1),
                "name": m.group(2),
                "start_line": str(i),
            }
            state.resources.append(state.current_resource)
            state.resource_start_line = i
        return True
    return False


def _collect_resource_end(stripped: str, i: int, state: _TerraformState) -> None:
    if state.current_resource and stripped == "}" and i > state.resource_start_line:
        state.current_resource = None


def _collect_variable(stripped: str, state: _TerraformState) -> None:
    if stripped.startswith('variable "'):
        m = re.search(r'variable\s+"([^"]+)"', stripped)
        if m:
            state.variables_defined.add(m.group(1))


def _collect_variable_usage(stripped: str, state: _TerraformState) -> None:
    for m in re.finditer(r"var\.(\w+)", stripped):
        state.variables_used.add(m.group(1))


def _collect_provider(stripped: str, state: _TerraformState) -> None:
    if stripped.startswith('provider "'):
        m = re.search(r'provider\s+"([^"]+)"', stripped)
        if m:
            state.providers.append(m.group(1))


def _check_hardcoded_credentials(
    stripped: str,
    line: str,
    i: int,
    state: _TerraformState,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
    total_lines: int,
) -> None:
    credential_patterns = [
        (r'(access_key)\s*=\s*"([^"$]+)"', "access_key"),
        (r'(secret_key)\s*=\s*"([^"$]+)"', "secret_key"),
        (r'(password)\s*=\s*"([^"$]+)"', "password"),
        (r'(token)\s*=\s*"([^"$]+)"', "token"),
        (r'(api_key)\s*=\s*"([^"$]+)"', "api_key"),
    ]
    for pattern, cred_type in credential_patterns:
        m = re.search(pattern, stripped, re.I)
        if m:
            errors.append(Issue(i, 1, "TF001", f"Hardcoded {cred_type}"))
            var_name = (
                f"{state.current_resource['type']}_{state.current_resource['name']}_{cred_type}"
                if state.current_resource
                else f"{cred_type}_var"
            )
            fixed_line = re.sub(pattern, f"{cred_type} = var.{var_name}", stripped)
            fixed_lines[i - 1] = line.replace(stripped, fixed_line)
            fixes.append(
                Fix(
                    i,
                    f"Zamieniono {cred_type} na zmienną",
                    m.group(0),
                    f"{cred_type} = var.{var_name}",
                )
            )
            resource_type = (
                state.current_resource["type"] if state.current_resource else "general"
            )
            var_def = f'\nvariable "{var_name}" {{\n  description = "{cred_type} for {resource_type}"\n  type        = string\n  sensitive   = true\n}}\n'
            fixed_lines.append(var_def)
            fixes.append(
                Fix(total_lines + 1, f"Dodano zmienną {var_name}", "", var_def.strip())
            )


def _check_open_cidr(
    stripped: str,
    line: str,
    i: int,
    state: _TerraformState,
    warnings: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "cidr_blocks" in stripped and "0.0.0.0/0" in stripped:
        warnings.append(Issue(i, 1, "TF002", "0.0.0.0/0 otwiera dostęp z internetu"))
        if "aws_security_group" in (
            state.current_resource.get("type") if state.current_resource else ""
        ):
            fixed_line = stripped.replace("0.0.0.0/0", "10.0.0.0/8")
            fixed_lines[i - 1] = line.replace(stripped, fixed_line)
            fixes.append(
                Fix(i, "Zamieniono 0.0.0.0/0 na 10.0.0.0/8", "0.0.0.0/0", "10.0.0.0/8")
            )


def _check_disabled_encryption(
    stripped: str,
    line: str,
    i: int,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    encryption_patterns = [
        (r"encrypted\s*=\s*false", "encrypted = false"),
        (r"encryption_at_rest\s*=\s*false", "encryption_at_rest = false"),
        (r"storage_encrypted\s*=\s*false", "storage_encrypted = false"),
        (r'kms_key_id\s*=\s*""', 'kms_key_id = ""'),
    ]
    for pattern, text in encryption_patterns:
        if pattern in stripped.lower():
            errors.append(Issue(i, 1, "TF003", "Wyłączone szyfrowanie"))
            if "kms_key_id" in text.lower():
                fixed_line = stripped.replace('""', '"alias/aws/ebs"')
            else:
                fixed_line = stripped.replace("false", "true")
            fixed_lines[i - 1] = line.replace(stripped, fixed_line)
            fixes.append(Fix(i, "Włączono szyfrowanie", text, fixed_line))


def _check_public_s3(
    stripped: str,
    line: str,
    i: int,
    errors: List[Issue],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if "acl" in stripped and (
        "public-read" in stripped or "public-read-write" in stripped
    ):
        errors.append(Issue(i, 1, "TF004", "Publiczny bucket S3"))
        fixed_line = re.sub(r'acl\s*=\s*"[^"]*"', 'acl = "private"', stripped)
        fixed_lines[i - 1] = line.replace(stripped, fixed_line)
        fixes.append(Fix(i, "Zmieniono ACL na private", stripped, fixed_line))


def _check_missing_tags(
    stripped: str,
    line: str,
    i: int,
    lines: List[str],
    state: _TerraformState,
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if (
        state.current_resource
        and state.current_resource["type"].startswith("aws_")
        and stripped == "}"
    ):
        has_tags = False
        for j in range(i, min(i + 20, len(lines))):
            if "tags" in lines[j] and "=" not in lines[j]:
                has_tags = True
                break
            if lines[j].strip() == "}":
                break
        if not has_tags:
            indent = line[: len(line) - len(line.lstrip())]
            tags_block = [
                f"{indent}  tags = {{",
                f"{indent}    Environment = var.environment",
                f"{indent}    Project     = var.project_name",
                f'{indent}    ManagedBy   = "terraform"',
                f"{indent}  }}",
                line,
            ]
            fixed_lines[i - 1 : i] = tags_block
            fixes.append(Fix(i, "Dodano blok tags", "", "tags = { ... }"))


def _check_terraform_required_version(
    stripped: str,
    line: str,
    i: int,
    lines: List[str],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith("terraform {"):
        has_version = False
        for j in range(i, min(i + 10, len(lines))):
            if "required_version" in lines[j]:
                has_version = True
                break
            if lines[j].strip() == "}":
                break
        if not has_version and stripped == "}":
            indent = line[: len(line) - len(line.lstrip())]
            version_line = f'{indent}  required_version = ">= 1.0"'
            fixed_lines[i - 1 : i] = [version_line, line]
            fixes.append(
                Fix(i, "Dodano required_version", "", 'required_version = ">= 1.0"')
            )


def _check_provider_version(
    stripped: str,
    i: int,
    lines: List[str],
    fixes: List[Fix],
    fixed_lines: List[str],
) -> None:
    if stripped.startswith('provider "') and not any(
        "version" in lines[j]
        for j in range(i, min(i + 10, len(lines)))
        if "}" not in lines[j]
    ):
        provider_name = re.search(r'provider\s+"([^"]+)"', stripped).group(1)
        brace_line = i
        for j in range(i, min(i + 20, len(lines))):
            if lines[j].strip() == "}":
                brace_line = j
                break
        if brace_line > i:
            indent = lines[brace_line - 1][
                : len(lines[brace_line - 1]) - len(lines[brace_line - 1].lstrip())
            ]
            version_line = f'{indent}  version = "~> 5.0"'
            fixed_lines[brace_line - 1 : brace_line - 1] = [version_line]
            fixes.append(
                Fix(
                    brace_line,
                    f"Dodano wersję providera {provider_name}",
                    "",
                    'version = "~> 5.0"',
                )
            )


def analyze_terraform(code: str) -> AnalysisResult:
    errors: List[Issue] = []
    warnings: List[Issue] = []
    fixes: List[Fix] = []

    lines = code.splitlines()
    fixed_lines = lines.copy()
    state = _TerraformState()

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if _collect_resource_start(stripped, i, state):
            continue

        _collect_resource_end(stripped, i, state)
        _collect_variable(stripped, state)
        _collect_variable_usage(stripped, state)
        _collect_provider(stripped, state)
        _check_hardcoded_credentials(
            stripped, line, i, state, errors, fixes, fixed_lines, len(lines)
        )
        _check_open_cidr(stripped, line, i, state, warnings, fixes, fixed_lines)
        _check_disabled_encryption(stripped, line, i, errors, fixes, fixed_lines)
        _check_public_s3(stripped, line, i, errors, fixes, fixed_lines)
        _check_missing_tags(stripped, line, i, lines, state, fixes, fixed_lines)
        _check_terraform_required_version(stripped, line, i, lines, fixes, fixed_lines)
        _check_provider_version(stripped, i, lines, fixes, fixed_lines)

    undefined = state.variables_used - state.variables_defined
    for var in undefined:
        warnings.append(
            Issue(1, 1, "TF005", f"Zmienna var.{var} nie jest zdefiniowana")
        )
        var_def = f'\nvariable "{var}" {{\n  description = "TODO: Add description"\n  type        = string\n}}\n'
        fixed_lines.append(var_def)
        fixes.append(Fix(len(lines) + 1, f"Dodano zmienną {var}", "", var_def.strip()))

    context = {
        "resources": state.resources,
        "providers": state.providers,
        "undefined_variables": list(undefined),
        "total_variables_defined": len(state.variables_defined),
        "total_variables_used": len(state.variables_used),
    }
    return AnalysisResult(
        "terraform", code, "\n".join(fixed_lines), errors, warnings, fixes, context
    )
