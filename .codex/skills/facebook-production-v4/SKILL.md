---
name: facebook-production-v4
description: Generate and package one Facebook-native finished-furniture concept image and a conversational Facebook caption from an approved V4 brief. Use as branch 3.
---

# Facebook production branch

Read the source image, `source-manifest.json`, the approved `creative-brief.json`, and [the shared three-platform visual system](../textile-social-controller-v4/references/approved-visual-system.md).

Use `concept_single`: generate exactly one Facebook-native 1200×1500 finished-furniture editorial scene named `product-concept.png`. Use the same approved visual language as Instagram—complete furnished environment, foreground/middle/background, strong physically coherent directional light, readable source-faithful textile, and restrained verified editorial typography—but generate a fresh Facebook composition directly at its target canvas. Never reuse, crop, or resize an Instagram or LinkedIn final image into the Facebook deliverable.

People are optional and normally omitted. The deliverable must be the finished product scene, never the raw material swatch. Record `ai_generated:true`; preserve the concept disclosure and any platform AI disclosure control.

Write a conversational Facebook-native `caption.txt`, create `usage.json` with `asset_mode:concept_single` and `post_generation_crop:false`, include the concept disclosure, and run validation. Stage only after validation passes. Do not publish.
