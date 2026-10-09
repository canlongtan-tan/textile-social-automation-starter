---
name: textile-social-controller-v4
description: Coordinate the project-local Instagram, Facebook, and LinkedIn textile workflow from source intake through platform-native content packages and approval-gated publishing. Use for three-platform runs, V4 tests, or status checks.
---

# Textile social controller V4

Read `社媒自动化V4/00-三平台总控.md`, `社媒自动化V4/research/platform-rules.md`, and `社媒自动化V4/schemas/contracts.md` before routing work.

All three production branches must read [the approved shared visual system](references/approved-visual-system.md). They use the same finished-furniture editorial style but generate separate images at each platform's configured dimensions. Shared style does not authorize sharing or resizing a final image across platforms.

For each selected platform, run the four branch skills in order: source, strategy, production, publishing. Platform branches may share the source file, verified facts, and the approved visual boundary, but must not share final images, captions, briefs, or publishing state.

Keep context modular. Pass only file paths and compact status between branches. Do not preload all platform research, generation history, or publishing history into one task. Each branch owns one job and can be rerun independently.

Use `社媒自动化V4/scripts/v4_pipeline.py prepare` to create isolated packages. Require the selected platform validator to pass, then use `stage` to create one immutable platform-specific publish-ready directory. The publishing branch reads only that staged directory, never arbitrary files from `outputs`.

On a fresh computer, require `素材库/第01批-20个/manifest.json`. If it is missing, run `社媒自动化V4/scripts/download_materials.py --batch 1 --batch-size 20`, then initialize the no-repeat pool with `社媒自动化V4/scripts/material_draw.py init`. Never download from an unrelated mirror or silently substitute another material.

Generation, validation, staging, browser opening, upload, caption entry, disclosure setup, and final-screen verification may run without intermediate approval when the user has requested an end-to-end test. The only mandatory human gate is the final platform action that makes the post public. Stop immediately before `Share` / `Post` / `Publish`, show the exact platform, visible identity, image, caption, disclosure state, and duplicate check, then request confirmation. After confirmation, click once, verify the public permalink and visible account, and only then record `published_verified`.
