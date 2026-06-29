---
name: finding-skills
description: Use when you need to discover which skills exist in this repository before invoking one - lists, searches, and inspects available skills so you can pick the right one
---

# Finding Skills

Use this skill to discover what skills are available before you act. Pair it with
**using-superpowers**, which establishes that you must invoke a relevant skill BEFORE
responding — this skill tells you HOW to find that relevant skill.

## When to Use

- You suspect a skill might apply but don't know its name.
- You're starting a task and want to see the full menu of available skills.
- A skill references another skill and you need to confirm it exists.

## How Skills Are Organized

Skills live under `.claude/skills/<skill-name>/SKILL.md`. Each `SKILL.md` begins with
YAML frontmatter:

```yaml
---
name: skill-name
description: Use when <trigger> - <what it does>
---
```

The `description` field is the most important part: its "Use when…" clause tells you
the trigger condition for invoking the skill. Match the user's task against these
triggers.

## Discovery Checklist

1. **List every skill.** Find all skill manifests:

   ```sh
   ls .claude/skills/*/SKILL.md
   ```

2. **Read the triggers, not the bodies.** Scan only the frontmatter `name` and
   `description` of each skill — that is enough to decide relevance. Pull them in one
   pass:

   ```sh
   grep -A2 -H '^name:' .claude/skills/*/SKILL.md
   ```

3. **Search by keyword.** When you have a task in mind (e.g. "debug", "test",
   "review", "plan"), grep descriptions for the matching trigger:

   ```sh
   grep -rin 'debug\|test\|review\|plan' .claude/skills/*/SKILL.md
   ```

4. **Shortlist by the "Use when" clause.** A skill applies if its trigger matches your
   task — even at ~1% likelihood (see using-superpowers). Prefer process skills
   (brainstorming, systematic-debugging) before implementation skills.

5. **Invoke, don't read.** Once you've identified the skill, load it through the
   platform's skill mechanism (in Claude Code, the `Skill` tool) rather than reading
   the file manually — this activates it properly.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just grep the codebase, not the skills" | Check `.claude/skills/` first — a skill may already cover this. |
| "I'll read the whole SKILL.md to decide" | Decide from the `description` trigger; read the body only after invoking. |
| "No skill name matches exactly" | Match on the trigger/intent, not the literal name. |
| "I already know what skills exist" | Skills are added and edited. Re-list before assuming. |
