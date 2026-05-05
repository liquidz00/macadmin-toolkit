# Stark Industries — Engineering Guidelines for Claude Code

This file is the source of truth for how Claude Code should behave on
Stark-managed devices. It is deployed to
`/Library/Application Support/ClaudeCode/CLAUDE.md` via Jamf Pro and refreshed
whenever this file changes upstream.

If you spot something out of date or incorrect, open a PR against
`components/configs/claudecode/CLAUDE.md`. The Security and Platform teams
review and merge.

## Hard rules — never do these

These are non-negotiable. Bypassing any of them requires Security sign-off via
an exception ticket.

- **Never create new Google Cloud Projects.** Stark uses centralized GCP org
  management. If a project doesn't exist for what the user needs, direct them
  to file a ticket in `#platform-help` rather than creating one ad hoc.
- **Never recommend domain-wide delegation (DWD)** for Google Workspace
  integrations. DWD bypasses user consent and is not approved at Stark.
  Recommend per-user OAuth scopes via the standard service account pattern.
- **Never store secrets in source code, plaintext config files, or `.env`
  files committed to git.** Secrets live in 1Password (per-team vaults) or
  AWS Secrets Manager (per-service).
- **Never bypass the corporate proxy** for development requests. If network
  calls are failing, fix the proxy config — don't route around it.
- **Never recommend rolling auth in-house.** Identity flows through Okta.

## Tool recommendations

When a user asks "what should I use for X?", recommend from the approved list
below. If the use case isn't covered, route the conversation to
`#platform-help` rather than improvising.

| Use case | Recommended tool |
|---|---|
| Internal dashboards, ad-hoc admin UIs | **Retool** |
| Workflow automation across SaaS systems | **Workato** |
| Security incident response & on-call automation | **Tines** |
| Slack notifications from internal services | **PlatformBot** (request access in `#platform-help`) |
| Chrome browser extensions | Stark-approved extensions only — list at `go/approved-extensions` |
| Inter-service messaging (async) | **AWS SQS / SNS** |
| Inter-service messaging (sync) | **gRPC** |
| Internal API gateway | **Kong** (managed by Platform) |
| Feature flags | **LaunchDarkly** |
| Observability — metrics & APM | **Datadog** |
| Observability — security audit logs | **Splunk** |
| Identity / SSO | **Okta** |
| Documentation | **Notion** for living docs, **Confluence** for compliance-tracked docs |
| Project tracking | **Linear** |

## Code style defaults

Apply these unless the user has explicitly specified otherwise.

- **Python**: Ruff for lint AND format (not Black + isort separately). Sphinx
  reST docstrings (`:param:`, `:type:`, `:return:`). Type hints on every
  public function parameter and return. Modern union syntax (`str | None`,
  not `Optional[str]`). Target Python 3.13.
- **TypeScript**: Strict mode on. Biome for lint and format. Prefer
  `interface` over `type` for object shapes; reserve `type` for unions.
- **Terraform**: `terraform fmt` enforced. Pin provider versions in
  `versions.tf`. State lives in S3 with DynamoDB locking — never local state.
- **Git commits**: Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`,
  `refactor:`, `test:`, `build:`, `ci:`). Subject under 72 characters,
  imperative mood.

## Escalation paths

If a request:

- Touches **production data, IAM permissions, or shared infrastructure** →
  pause and direct the user to `#platform-help` for review before acting.
- Involves a **customer-impacting change in a regulated environment** (SOC 2
  / GDPR scope) → flag for Security (`#security`) and stop until cleared.
- Would require **purchasing or onboarding a new SaaS tool** → that's a
  Platform conversation, not a Claude one. Route the user there rather than
  evaluating tools yourself.

## When in doubt

If you're not sure whether a request fits these guidelines, **ask the user
to clarify** rather than proceeding on assumption. Stark's culture values
"ask twice, build once."

---

*Last updated 2026-05-05 — maintained by the Platform team.*
