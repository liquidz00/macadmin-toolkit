---
name: deep-research
description: Decompose a research question into 3–5 parallel angles, dispatch subagents to investigate each angle with web search, and synthesize the findings into a single answer with cited sources at the end. Use when the user invokes /deep-research <topic> or asks a question that warrants deeper investigation than a single web search could answer.
---

# /deep-research

Take a research query, split it into distinct angles, dispatch one general-purpose
subagent per angle (in parallel), then synthesize the results into a single
unified answer with sources cited at the end.

## Usage

```
/deep-research <topic or question>
```

Examples:
- `/deep-research using the Microsoft Graph API to automate intunewin file uploads to Intune`
- `/deep-research proper ways to configure/restrict sshd usage on macOS using MDM`
- `/deep-research best practices for Jamf Pro patch management workflows in 2026`

## Workflow

### 0. Sanity-check the query

If the query is too vague (single word, no clear question, ambiguous scope),
**stop and ask for refinement** before dispatching anything. A good query is
specific enough that you can imagine 3–5 distinct, non-overlapping research
angles. If you can't, ask the user to clarify what they're after.

If the query is something the model already knows with high confidence (basic
factual lookups, well-trodden topics with stable answers), say so and offer
to answer directly without spending the cost of parallel research. Cost note
at the bottom for context.

### 1. Decompose the query into angles

Break the topic into 3–5 distinct research angles. Aim for angles that
**don't overlap** — each subagent should hit different sources or different
facets so you get coverage rather than redundancy.

Useful axes for decomposition:

- **Reference vs. example.** Official API docs are one angle; community blog posts and GitHub samples are another.
- **Technical vs. policy.** "How do I do X" is one angle; "what's the recommended approach / compliance framing" is another.
- **Vendor vs. vendor-agnostic.** For mac admin questions, "what does Apple/Microsoft say" is one angle; "how do Jamf/Kandji/Mosyle implement it" is another.
- **Concept vs. troubleshooting.** "How does it work" is one angle; "what breaks and how do people fix it" is another.

Show the decomposition to the user before dispatching:

> Researching across 4 angles:
> 1. Official Microsoft Graph API endpoints for Win32 app upload
> 2. .intunewin file format and packaging requirements
> 3. Authentication patterns (app registration, scopes, token flow)
> 4. Real-world examples and gotchas from community sources

### 2. Dispatch subagents in parallel

In a **single message**, make N `Agent` tool calls — one per angle. This is
the critical implementation detail: parallel calls happen only when issued
in the same message. Sequential calls block.

Each subagent must:
- Be a `general-purpose` subagent (so it has access to `WebSearch` and `WebFetch`).
- Receive a **self-contained prompt** — subagents don't see the parent conversation, so the prompt must include the full original query, the assigned angle, and the required output format.

Sub-agent prompt template:

```
The user asked: "<original query>"

Your assigned research angle: <angle description>

Use WebSearch and WebFetch to research this angle. Report concrete, useful
findings that directly address the user's question from your assigned angle.

Source quality matters:
- Prefer official documentation (vendor docs, RFCs, Apple/Microsoft developer pages).
- Then well-known community sources (macadmins.org, established blogs, GitHub repos with traction).
- Avoid random blog posts of unclear authorship unless they're the only source.

Output format:
1. Findings — under 400 words, focused on what's actionable. No filler, no recap of the question.
2. ## Sources — every URL you consulted, one per line. Include the page title in parentheses if helpful for the synthesis step.

If you can't find anything useful for this angle, say so explicitly and
describe what you searched for. Don't invent sources.
```

Cap at 5 subagents per query. More than that is rarely worth the time + cost.

### 3. Synthesize

When all subagents return:

1. **Read all findings.** Identify overlaps (multiple angles converging on the same conclusion — a strong signal) and contradictions (angles disagree about a fact or recommendation — flag these explicitly).
2. **Write a unified answer** to the user's original question, organized by what's most useful — *not* by angle. Don't surface "Subagent 1 said X, Subagent 2 said Y" framing; the user wants the *answer*, not the process.
3. **Flag contradictions** when sources disagree: "Microsoft's docs say X, but multiple community implementations use Y because of <reason>."
4. **Note gaps.** If an angle returned little useful info, mention it briefly so the user knows what *wasn't* answered.

### 4. Cite sources

End the response with a `## Sources` section listing every URL referenced
across all subagents. **Deduplicate** — multiple subagents may have hit the
same page. Order roughly by how load-bearing each source was for the answer
(most useful first), not alphabetically.

Format:

```markdown
## Sources

- https://learn.microsoft.com/en-us/graph/api/intune-apps-win32lobapp-create
- https://docs.jamf.com/technical-articles/Configuration_Profile_Reference.html
- https://github.com/macadmins/installomator/wiki/Configuration
- https://support.apple.com/guide/deployment/...
```

## Output structure

The full response should look like:

```markdown
[direct answer to the question, 200–600 words depending on complexity, with
inline references like "(per Apple's MDM Settings reference)" rather than
bare URLs in the prose]

## Caveats / gaps                  ← optional, only if there are real gaps
[anything the research couldn't cover]

## Sources                          ← required
- url 1
- url 2
- ...
```

## When NOT to use this skill

- **Simple factual lookups** ("what's the latest macOS version?") — a single `WebSearch` call is enough.
- **Questions about the current repository or local files** — read the files directly; web search is not relevant.
- **Questions about something you already know with high certainty.** Don't dispatch four subagents to confirm what's clearly true.
- **Conversational chat** — even research-flavored chat where the user is thinking out loud rather than asking a concrete question.

## Cost note

This skill spawns N parallel subagents, each making multiple web-search and
web-fetch calls. It's meaningfully more expensive (in time and API usage)
than answering directly. Worth it for genuinely hard research questions
where the answer needs to be grounded in current sources; overkill for
"how do I install Homebrew." When in doubt, ask the user whether they want
the deep version or a quick answer.
