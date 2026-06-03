# Agent Compatibility

This repository keeps the study workflow as a real skill, not as a long context file.

## Source of Truth

The canonical skill lives at:

```text
skills/ai-study-workflow/SKILL.md
```

Edit this copy first.

## Codex

Codex project skill copy:

```text
.codex/skills/ai-study-workflow/SKILL.md
```

Use in Codex:

```text
使用 ai-study-workflow，读取这个课程文件，先做资料卡，再进入期末复习诊断。
```

## Claude Code

Claude Code project skill copy:

```text
.claude/skills/ai-study-workflow/SKILL.md
```

Use in Claude Code:

```text
/ai-study-workflow
```

`CLAUDE.md` imports `AGENTS.md` and points Claude to the project skill. The full workflow stays in the skill because Claude Code skills load on demand, while `CLAUDE.md` is loaded into every session.

## Gemini CLI

Gemini CLI reads `GEMINI.md` by default. This repository's `GEMINI.md` imports `AGENTS.md` and points Gemini to:

```text
skills/ai-study-workflow/SKILL.md
```

If your Gemini setup supports configurable context filenames, you can also configure it to read `AGENTS.md` directly.

## Other Agents

For agents that understand the Agent Skills convention, use:

```text
skills/ai-study-workflow/
```

For agents that only read project instruction files, load `AGENTS.md` first, then explicitly read the canonical skill.

## Keeping Copies in Sync

After editing the canonical skill, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/sync-agent-skills.ps1
```

This mirrors `skills/ai-study-workflow` into `.codex/skills/ai-study-workflow` and `.claude/skills/ai-study-workflow`.
