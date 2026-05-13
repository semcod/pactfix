## Installation

```bash
pip install -e .
```

# With language specified
pactfix config.yaml -l kubernetes

# Directory
pactfix --batch ./configs

# Verbose output
pactfix file.py -v
```

# In-place with comments
pactfix --path ./project --comment

# To new file
pactfix input.yaml -o output.yaml

# With comments
pactfix input.yaml -o output.yaml --comment
```

# Create sandbox with fixes
pactfix --path ./project --sandbox

# With tests
pactfix --path ./project --sandbox --test
```

### Docker Compose

```bash
pactfix docker-compose.yml -l docker-compose --comment
```

Fixes:
- Image tags (latest → specific)
- Remove privileged: true
- Add networks block
- Flag hardcoded secrets

### Kubernetes

```bash
pactfix deployment.yaml -l kubernetes --comment
```

Fixes:
- Image tags
- Add resource limits
- Add probes (liveness/readiness)
- Add securityContext
- Remove privileged containers

### Terraform

```bash
pactfix main.tf -l terraform --comment
```

Fixes:
- Interpolate secrets to variables
- Enable encryption
- Fix CIDR blocks (0.0.0.0/0 → 10.0.0.0/8)
- Change public S3 ACLs to private
- Add resource tags
- Add version constraints

### Default Output

```
❌ file.py: 2 errors, 3 warnings, 2 fixes [python]
```

### Verbose Output

```
10:11:08 📋 Analyzing: file.py
10:11:08 ✅ Language detected: python
10:11:08 ❌ Errors: 2
10:11:08 ⚠️  Warnings: 3
10:11:08 ✅ Fixes applied: 2
10:11:08 ❌   Line 10: [PY001] Print statement used
10:11:08 📋   Line 10: Zmieniono print na print()
```

### JSON Output

```bash
pactfix file.py --json
```

## Common Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Detailed output |
| `--comment` | Add fix comments |
| `-o FILE` | Output file |
| `--json` | JSON format |
| `-l LANG` | Force language |
| `--batch DIR` | Process directory |
| `--path DIR` | Project mode |
| `--sandbox` | Docker sandbox |
| `--test` | Run tests in sandbox |

## Exit Codes

- `0` - Success (no errors)
- `1` - Errors found

### GitHub Actions

```yaml
- name: Security Scan
  run: |
    pip install pactfix
    pactfix . --batch --json > report.json
```

### GitLab CI

```yaml
security:
  script:
    - pip install pactfix
    - pactfix --path . --comment
```

## Tips

1. **Always review auto-fixes** - They're suggestions, not perfect
2. **Use `--comment`** - Keeps track of changes
3. **Test in sandbox first** - Use `--sandbox` before `--path`
4. **Combine with git** - Commit fixes separately
5. **Use in CI** - Prevent issues from reaching production

# Quick security scan
pactfix --batch . -v

# Fix Docker Compose
pactfix docker-compose.yml -l docker-compose --comment -o fixed.yml

# Secure Terraform
pactfix infra/ -l terraform --comment

# Kubernetes best practices
pactfix k8s/ -l kubernetes --batch --comment

# Generate security report
pactfix . --batch --json > security-report.json
```
