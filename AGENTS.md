# AGENTS.md

Instructions for AI coding agents (Claude Code, Cursor, Aider, Copilot) working on
this repo. Tool-agnostic — tooling-specific guidance lives in `.cursor/rules/` and
`.claude/` if and where it differs.

## What this repo is

A curated personal toolkit for managing macOS fleets via Jamf Pro: deployment
scripts, extension attributes, Terraform configuration, Claude skills, and
Python automations. It is **not** a packaged product. Most contents started in
a private MDM repository at a previous role and have been re-implemented or
generalized here.

The audience is Mac admins who want to copy patterns into their own setup, plus
recruiters / peers reviewing the work. Optimize for **legibility and copy-paste
friendliness**, not for runtime as a single application.

## Layout

```
components/
├── scripts/{shell,python,powershell}/   # deployment scripts grouped by language
├── xattrs/                               # Jamf extension attributes
├── configs/                              # content rendered into scripts via Terraform templatefile
└── vendor-provided/                      # third-party scripts kept under their original license

terraform/                                # Terraform config for Jamf Pro resources
packages/                                 # uv workspace; Python CLIs and shared library
├── common/                               # shared clients (Slack, Notion, Falcon, Jamf, GitHub) and Pydantic models
└── jamfy/                                # the primary CLI — exports, change tracking, app installer sync

exports/                                  # JSON exports of MDM resources, used for diff-based change tracking
tests/                                    # pytest unit tests for the Python packages
docs/                                     # git submodules of frequently-referenced macadmin tool wikis
.claude/skills/                           # Claude Code skills for everyday Mac admin work
.github/                                  # CODEOWNERS + workflows
```

## Required behavior: ground answers in `docs/`

When asked about an open-source mac admin tool used in or by this repo
(Installomator, swiftDialog, outset, dockutil, pymdm, etc.):

1. **Check `docs/<tool>/` first** before answering. The submodule is the source
   of truth for that tool's current behavior.
2. **If no submodule exists**, do not answer from training data. Ask the user
   to provide documentation, a link, or a man page.
3. **Never assume tool behavior without validation.** If the docs don't cover
   the specific question, say so explicitly before speculating.

This rule exists because mac admin tooling moves fast — flags get renamed and
behavior changes between versions. Stale model knowledge produces confidently
wrong answers that waste an admin's time at best and break a managed fleet at
worst.

The full rule with examples and anti-patterns is at
`.cursor/rules/docs-reference.mdc`. The same applies to Claude Code, Cursor,
or any other agent operating in this repo.

## Key pattern: Terraform `templatefile` for content delivery

The unifying pattern across this repo is **content lives in source files, scripts
deliver it**:

1. A markdown file (e.g. `components/configs/claudecode/CLAUDE.md`) is the source of truth.
2. A deployment script template (e.g. `components/scripts/shell/deploy_claude_md.sh.tftpl`) has a placeholder for the content.
3. A Terraform resource (e.g. `terraform/scripts.tf`) uses `templatefile()` to render the script with the content base64-encoded into it, and creates the corresponding Jamf script resource.
4. On change to the source markdown, Terraform detects the diff and re-deploys.

This means non-engineers (security team, IT) can PR changes to the markdown
without touching scripts or Terraform.

## Code style

### Python (under `packages/`)
- **uv workspace**. Root `pyproject.toml` declares members; each `packages/<name>/pyproject.toml` is its own project. Workspace siblings are referenced via `[tool.uv.sources] sibling = { workspace = true }`.
- **Ruff** for lint AND format. Line length 100, double quotes, target Python 3.13.
- **Modern union syntax**: `str | None`, `list[int]`, `dict[str, Any]`. NOT `Optional[T]` / `Union[A, B]`.
- **Sphinx/reST docstrings** (`:param:`, `:type:`, `:return:`, `:rtype:`, `:raises:`) on every public function. Not Google or NumPy style.
- **Type hints required** on every public function/method parameter and return.
- **Pydantic 2** for models. `.model_dump(mode="json")` when producing JSON.
- **CLI is `click` / `asyncclick`**. Don't bake Click types into business logic — keep `click.echo()` etc. confined to the entry-point module.

### Shell (under `components/scripts/shell/`)
- **Bash, not zsh**, unless a script genuinely needs zsh-only features.
- **Shellcheck enforced** via pre-commit. Globally disabled rules are documented in `.shellcheckrc`.
- Shebang: `#!/bin/bash`. For scripts run by Jamf, the standard parameters (`$4`-`$11`) are passed positionally; reference them as `param_name="$4"` near the top.
- Exit codes: `0` success, non-zero failure. Do not silently swallow errors.

### Terraform (under `terraform/`)
- 2-space indent. `terraform fmt -recursive` enforced via pre-commit.
- One file per resource type / domain (`scripts.tf`, `xattrs.tf`, `app_installers.tf`, etc.).
- `variables.tf` for variable declarations. `main.tf` for provider config. `locals.tf` for `locals { ... }` blocks.
- Variable names: `snake_case`. Resource names: `snake_case`. Values use `for_each` over `count` whenever the underlying source is a map or set.

### YAML (under `.github/workflows/`)
- 2-space indent. `actionlint` enforced via pre-commit.
- Pin actions by SHA when used in shared/release workflows; tags okay for internal CI.

## Workflow

### Setup
```bash
git submodule update --init --recursive   # fetch the docs/ submodules
make install-dev                          # uv sync --all-packages --all-extras
make pre-commit-install                   # enable pre-commit hooks
```

### Daily commands
```bash
make help          # list everything
make format        # auto-format Python + Terraform
make lint          # check formatting + lint Python
make test          # run pytest
make tf-validate   # terraform validate
make docs-update   # pull latest from each submoduled wiki
```

### Pre-commit
Configured hooks: ruff, terraform_fmt, terraform_validate, shellcheck, actionlint,
plus the standard pre-commit-hooks (trailing whitespace, EOF, yaml, large files,
private keys). Pre-commit is the source of truth for "is this ready to commit?"

### Commits
Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`,
`build:`, `ci:`. Keep subjects under 72 characters.

## Things to be careful about

- **Don't commit real Jamf Pro URLs, API tokens, or organizational data.** Use the
  Avengers / Marvel-themed fake data convention already established in `terraform/`
  (Stark Industries departments, Avengers Tower buildings, etc.).
- **Vendor-provided scripts retain their original license.** When dropping a script
  into `components/vendor-provided/`, preserve the original license header.
- **Don't touch the submoduled `docs/`.** They're read-only references. Changes go
  upstream.
- **GitHub Actions secrets do not exist in this public repo.** Workflows that
  reference `${{ secrets.JAMF_URL }}` etc. are example-only and won't run.

## What this repo is NOT

- Not a deployment framework. It's a reference + a few CLIs.
- Not a Jamf Pro client library. That's `pymdm`.
- Not a place for organization-specific secrets or PII. If you find any, file an issue immediately.
