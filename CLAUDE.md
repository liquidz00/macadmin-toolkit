# CLAUDE.md

This file provides Claude Code (claude.ai/code) with context for working in
this repository.

For the comprehensive convention guide that applies to all AI agents (Claude,
Cursor, Aider, Copilot), see [`AGENTS.md`](./AGENTS.md). This file captures only
Claude-specific guidance.

## Quick orientation

This is `macadmin-toolkit` — a curated personal collection of scripts, Claude
skills, extension attributes, and Terraform patterns for managing macOS fleets
via Jamf Pro. Most of it started life inside a private MDM repo at a previous
role and has been re-implemented or generalized here.

The repo mixes several languages — Python (under `packages/`), bash (under
`components/scripts/shell/`), HCL/Terraform (`terraform/`), and PowerShell. Each
has its own conventions; see `AGENTS.md` for details.

## When asked to add a new component

1. **Identify the right home.** Scripts → `components/scripts/<lang>/`. Extension
   attributes → `components/xattrs/`. Terraform-templated content → `components/configs/<area>/`.
2. **Check `components/vendor-provided/`** before writing something from scratch — there may already be a third-party version.
3. **If the component is delivered via Jamf**, write the corresponding Terraform resource in `terraform/<domain>.tf` and use `templatefile()` if any content needs to be baked in at deploy time.
4. **Follow the existing fake-data convention.** Sample data uses Marvel / Avengers themes (Stark Industries, Wakanda Embassy, etc.) — keep it consistent so the repo reads as a single coherent example rather than a mishmash of placeholders.

## When asked to add a Claude skill

Skills live under `.claude/skills/<skill-name>/`. Each skill is a directory
containing at least a `SKILL.md` describing what it does and when it should be
invoked. Refer to existing skills as templates before adding new ones.

## Don't

- Don't commit real Jamf URLs, API credentials, or any organizationally-identifying
  data. Use Avengers fake data.
- Don't modify files under `docs/` — those are read-only git submodules of
  upstream wikis.
- Don't add new Python top-level dependencies without considering whether they
  fit in `packages/common/` (shared library) vs `packages/jamfy/` (CLI-specific).

## Useful commands

```bash
make help          # list every Make target
make format        # auto-format Python + Terraform
make lint          # check formatting and run ruff
make test          # run pytest
make docs-update   # refresh submoduled docs/
```
