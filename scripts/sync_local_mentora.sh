#!/usr/bin/env bash
# Copy this team's skills into a local mentora-skills clone (sibling of cs-343-skills).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MENTORA="${MENTORA_SKILLS_ROOT:-$ROOT/../mentora-skills/mentora_skills/skills}"

if [[ ! -d "$MENTORA" ]]; then
  echo "mentora-skills not found at: $MENTORA" >&2
  echo "Clone: git clone https://github.com/NUCS338-skills-scaffolding-project/mentora-skills.git" >&2
  exit 1
fi

for dir in "$ROOT"/skills/*/; do
  name="$(basename "$dir")"
  cp "$dir/skills.md" "$MENTORA/$name/skills.md"
  echo "synced $name"
done

echo ""
echo "Rebuild catalog (from skills-registry):"
echo "  python scripts/catalog_builder.py --package ../mentora-skills/mentora_skills/skills --output catalog.json"
echo "Restart skills-orchestrator after rebuild."
