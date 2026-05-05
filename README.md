# macadmin-toolkit

Personal collection of scripts, Claude skills, extension attributes, and Terraform patterns I use (or have used) for managing macOS fleets via Jamf Pro.

This is a curated reference, not a packaged product. Most of the contents started life inside a private MDM repository at a previous role and have been re-implemented or generalized here. Take what's useful, leave what isn't.

> [!IMPORTANT]
>
> Nothing in this repo should be considered production-ready without your own testing. Many scripts assume a Jamf Pro environment, specific organizational conventions, or external tooling (Slack, Notion, Falcon) that you'll need to adapt to your setup.

## What's where

| Directory | Contents |
|---|---|
| `components/scripts/` | Deployment scripts grouped by language (zsh, python, powershell) |
| `components/xattrs/` | Jamf extension attributes |
| `components/configs/` | Content baked into deployment scripts at runtime via Terraform `templatefile` |
| `components/vendor-provided/` | Third-party scripts and extension attributes (kept under their original license) |
| `terraform/` | Terraform configuration for Jamf Pro resources |
| `packages/` | Python CLIs and shared library code, organized as a uv workspace |
| `exports/` | JSON exports of MDM resources, used for diff-based change tracking |
| `tests/` | Unit tests for the Python packages |
| `docs/` | Submoduled wikis from frequently-referenced macadmin tools |
| `.claude/skills/` | Claude Code skills for everyday Mac admin work |

## Getting started

```bash
git submodule update --init --recursive   # fetch the docs/ submodules
make install-dev                          # uv sync --all-packages --all-extras
make pre-commit-install                   # enable pre-commit hooks
```

`make help` lists everything else.

## Conventions

Project-wide conventions for code style, docstrings, commit messages, and AI
agent behavior live in two places:

- [`AGENTS.md`](./AGENTS.md) — tool-agnostic guide for any AI coding assistant
  working in this repo (Claude Code, Cursor, Aider, Copilot).
- [`.cursor/rules/`](./.cursor/rules) — Cursor-specific `.mdc` rules. Of note:
  - [`docs-reference.mdc`](./.cursor/rules/docs-reference.mdc) — agents must
    ground answers about third-party mac admin tools (Installomator, swiftDialog,
    outset, dockutil, pymdm, etc.) in the `docs/` submodules rather than training
    data. If no submodule exists, the agent prompts for documentation rather
    than guessing.
  - [`technical-writing.mdc`](./.cursor/rules/technical-writing.mdc) — voice,
    tone, and structure for all prose in the repository.

## License

[MIT](LICENSE) — copy, adapt, ship. No warranty.
