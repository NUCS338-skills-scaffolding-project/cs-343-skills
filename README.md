# cs-343-skills

Course skill repository for **COMP_SCI 343 (Operating Systems)** — Northwestern CS338 practicum client course.

## Skills in this repo

| Folder | `skill_id` | Focus |
|--------|------------|--------|
| `ask_for_decomposition` | `ask-for-decomposition` | Planning / breaking problems down |
| `narrow_the_bug_location` | `narrow-the-bug-location` | Systematic debugging |
| `extract_requirements` | `extract-requirements` | Reading assignment specs |
| `explanation_nautilus_architecture` | `explanation-nautilus-architecture` | NK architecture orientation |
| `explain_function_responsibilities` | `explain-function-responsibilities` | Modularity / function boundaries |
| `evaluate_readability_on_code` | `evaluate-readability-on-code` | Code readability review |
| `connect_prior_knowledge` | `connect-prior-knowledge` | Bridging prior coursework |

See `metadata.yaml` for the canonical list passed to the skills registry.

## Validate locally

```bash
pip install pyyaml
python .github/scripts/validate_skills.py
```

## Test with the orchestrator (May 2026 update)

Read the org doc: [Update_18thMay.md](https://github.com/NUCS338-skills-scaffolding-project/skills-documents/blob/main/Update_18thMay.md).

**Sibling layout** (example):

```
Projects/
  skills-orchestrator/
  mentora-skills/
  skills-registry/
  cs-343-skills/          ← this repo
```

**Quick test against this repo** (before sync to `mentora-skills`):

1. In `skills-orchestrator/.env`:
   ```bash
   MENTORA_SKILLS_PATH=../cs-343-skills/skills
   REGISTRY_CACHE_TTL=0
   ```
2. Rebuild catalog:
   ```bash
   cd skills-registry
   python scripts/catalog_builder.py --package ../cs-343-skills/skills
   ```
3. Restart the orchestrator; send messages that should trigger a skill.
4. Inspect selection:
   ```bash
   curl -s http://localhost:8080/sessions/{session-id}/debug | jq
   ```
5. Revert `.env` to `../mentora-skills/mentora_skills/skills` when done.

**What to check** (from TA): correct skill invoked, Socratic flow (not random questions), short responses, stance/trigger behavior. Ignore skill scores in logs.

## Nautilus reference

https://github.com/NorthwesternOS/startlab-f24-Banman03
