# Skill Creation Tools

This directory contains scripts for creating and packaging Claude skills.

## Files

- **package_skill.py** - Package a skill folder into a distributable .skill file
- **init_skill.py** - Initialize a new skill with proper structure

## Usage

### Creating a New Skill

```bash
cd /Volumes/livestuff/claude
python3 skill-tools/init_skill.py <skill-name> --path .
```

Example:
```bash
python3 skill-tools/init_skill.py my-new-skill --path .
```

This will create:
```
my-new-skill/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

### Packaging a Skill

After developing your skill, package it for distribution:

```bash
cd /Volumes/livestuff/claude
python3 skill-tools/package_skill.py <skill-folder> <output-directory>
```

Example:
```bash
python3 skill-tools/package_skill.py woosmap-skill skills-dist
```

This will:
1. Validate the skill structure
2. Create a .skill file (zip archive)
3. Save it to the output directory

### Re-packaging the Woosmap Skill

If you edit `woosmap-skill/SKILL.md`, re-package it with:

```bash
cd /Volumes/livestuff/claude
python3 skill-tools/package_skill.py woosmap-skill skills-dist
```

The updated `skills-dist/woosmap.skill` will be created.

## Requirements

- Python 3.x
- PyYAML (install with: `pip install pyyaml`)

## Validation

The `package_skill.py` script automatically validates:
- YAML frontmatter format
- Required fields (name, description)
- Directory structure
- File organization

If validation fails, fix the errors and run the packaging command again.

## Examples

### Full Workflow for a New Skill

```bash
# 1. Create new skill
python3 skill-tools/init_skill.py api-helper --path .

# 2. Edit the skill
nano api-helper/SKILL.md

# 3. Package it
python3 skill-tools/package_skill.py api-helper skills-dist

# 4. Distribute
# Share skills-dist/api-helper.skill with others
```

## Troubleshooting

### "No module named 'yaml'"
```bash
pip install pyyaml
```

### Permission denied
```bash
chmod +x skill-tools/package_skill.py
chmod +x skill-tools/init_skill.py
```

### Validation errors
Check the error message and fix the issues in SKILL.md:
- Ensure YAML frontmatter has `name` and `description`
- Verify frontmatter is enclosed in `---`
- Check for proper formatting
