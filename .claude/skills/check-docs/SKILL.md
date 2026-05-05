---
name: check-docs
description: List and surface what documentation is available for an open-source mac admin tool in the docs/ submodule directory. Use when the user asks about a third-party tool (Installomator, swiftDialog, outset, dockutil, pymdm, etc.) or types /check-docs <tool>.
---

# /check-docs

Surface what's available under `docs/<tool>/` so the user (and you) can ground
the conversation in actual reference material instead of training data.

## Usage

```
/check-docs <tool>
```

Where `<tool>` is the name of a directory under `docs/` (e.g. `installomator`,
`swiftdialog`, `outset`, `dockutil`, `pymdm`).

## Workflow

When invoked:

1. **Confirm the submodule exists.** Run `ls docs/<tool>/`. If the directory is missing or empty:
   - Run `ls docs/` and surface the available submodules.
   - Suggest the closest fuzzy match if any.
   - Recommend adding the submodule:
     ```bash
     git submodule add <upstream-wiki-or-repo-url> docs/<tool>
     ```
   - Stop. Do not answer the user's underlying question from training data — refer to the `docs-reference.mdc` rule.

2. **Summarize what's there.** List the markdown files (or other doc files) at the top level of `docs/<tool>/`. Group them roughly by topic if obvious (e.g. "Setup," "Configuration," "Troubleshooting") based on filenames.

3. **Read the landing page.** If the submodule has one of `Home.md`, `README.md`, or `index.md`, read its first 30–50 lines and summarize the project description in 2–3 sentences. This gives the user (and yourself) context.

4. **Surface a numbered list of pages.** Format as:
   ```
   docs/installomator/ contents:

   1. Home.md             — landing page and quick intro
   2. Variables.md        — full list of installer variables and defaults
   3. Configuration.md    — how to configure runtime behavior
   4. ...
   ```

5. **Ask which page to read.** Or, if the user's earlier message implied a specific question, propose a page and offer to read it: *"Want me to read `Variables.md` to answer your question about `IGNORE_APP_STORE_APPS`?"*

## When NOT to use this skill

- The user is asking a question about *this repository* (Patcher, jamfy, common, terraform configuration). That's not a third-party tool — answer from the repo directly.
- The user is asking about a tool that isn't and shouldn't be a submodule (e.g. `bash`, `awk`, `terraform` itself). Use general knowledge or web search.

## Why this exists

Mac admin tooling moves fast and stale model knowledge produces confidently
wrong answers. The `docs/` directory exists so any agent (or human) can ground
themselves before answering. This skill makes "what do I have available?" a
one-line check rather than a multi-step recall.

For the always-on guardrail that this skill complements, see
`.cursor/rules/docs-reference.mdc` and the corresponding section in `AGENTS.md`.
