# macadmin-toolkit

Personal collection of scripts, Claude skills, extension attributes, and Terraform patterns I use (or have used) for managing macOS fleets via Jamf Pro.

This is a curated reference, not a packaged product. Most of the contents started life inside a private MDM repository at a previous role and have been re-implemented or generalized here. Take what's useful, leave what isn't.

> [!IMPORTANT]
>
> Nothing in this repo should be considered production-ready without your own testing. Many scripts assume a Jamf Pro environment, specific organizational conventions, or external tooling (Slack, Notion, Falcon) that you'll need to adapt to your setup.

## Status

This is a **reference architecture, not a packaged product.** The scripts and Terraform configurations here are reproductions of patterns I built while managing a Mac fleet at a previous role, recreated from memory and adapted for a public repository. They have not been validated against a live Jamf Pro instance, and individual scripts may have minor inaccuracies relative to my originals — the goal is to demonstrate the *architecture and patterns*, not to provide drop-in production code.

What this means for you:

- **Treat the patterns as accurate, the bytes as illustrative.** The terraform `templatefile()` + base64 + atomic-write deployment loop, the SHA-256-verified extension attribute, the run-as-user pattern in `jamf_log_uploader.py`, the GitOps-for-endpoints model — those are correct and worth borrowing. The exact field names, paths, or edge-case handling in any specific script may need adapting.
- **Tests are partial.** Where unit tests exist under `tests/`, they cover script logic via mocked filesystem and subprocess boundaries. End-to-end behavior on a real Mac fleet has not been re-verified.
- **No real organizational data is present.** Sample data uses a Marvel / Avengers theme (Stark Industries departments, Avengers Tower buildings, etc.) so nothing here can leak from any real organization.

If you find something that's wrong, an issue or PR is welcome.

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

## Python runtime: `managed_python3`

Every Python deployment script and extension attribute in `components/` is shebanged to:

```python
#!/usr/local/bin/managed_python3
```

This is the [macadmins/python](https://github.com/macadmins/python) bundled Python — a relocatable, self-contained interpreter designed for unattended deployment on managed Mac fleets. It ships with a curated set of packages (`requests`, `cryptography`, `pyobjc`, etc.).

**The scripts here assume the build also includes:**

- `httpx` — async HTTP client used by `pymdm.WebhookSender` and async-style scripts.
- `pandas` — data manipulation in scripts that produce reports or diffs.
- `pymdm` — [the cross-platform MDM utilities package](https://github.com/liquidz00/pymdm) (`MdmLogger`, `CommandRunner`, `SystemInfo`, `WebhookSender`, etc.).

If you're deploying these scripts on your own fleet, either build a custom `managed_python3` package that includes those three (instructions in [macadmins/python's README](https://github.com/macadmins/python#building-the-package)) or adapt each script to import from whatever runtime you're shipping. Don't expect them to work out of the box against the stock `macadmins/python` distribution.

## Conventions

Project-wide conventions for code style, docstrings, commit messages, and AI
agent behavior live in two places:

- [`AGENTS.md`](./AGENTS.md) — tool-agnostic guide for any AI coding assistant working in this repo (Claude Code, Cursor, Aider, Copilot).
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
