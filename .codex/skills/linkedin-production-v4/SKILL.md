---
name: linkedin-production-v4
description: Generate and package one LinkedIn-native finished-furniture concept image and a professional B2B caption from an approved V4 brief. Use as branch 3.
---

# LinkedIn production branch

Read the source image, `source-manifest.json`, the approved `creative-brief.json`, and [the shared three-platform visual system](../textile-social-controller-v4/references/approved-visual-system.md).

Use `concept_single`: generate exactly one LinkedIn-native 1080×1350 finished-furniture editorial scene named `product-concept.png`. Use the same approved visual language as Instagram—complete furnished environment, foreground/middle/background, strong physically coherent directional light, readable source-faithful textile, and restrained verified editorial typography—but generate a fresh LinkedIn composition directly at its target canvas. Never reuse, crop, or resize an Instagram or Facebook final image into the LinkedIn deliverable.

People are optional and normally omitted. The image may feel architecturally precise, but it must remain a finished furniture advertisement rather than a meeting or material-review screenshot. Record `ai_generated:true`; preserve the concept disclosure and any platform AI disclosure control.

Write a value-first LinkedIn-native `caption.txt`, create `usage.json` with `asset_mode:concept_single` and `post_generation_crop:false`, disclose the concept visualization, and run validation. Stage only after validation passes. Do not publish.
