---
name: instagram-production-v4
description: Package an Instagram-native textile post and caption from an approved V4 creative brief, using a real source photo, one finished AI product scene, or an AI concept carousel. Use as branch 3 after Instagram research is complete; do not use for research or publishing.
---

# Instagram production branch

Read the source image, `source-manifest.json`, the approved `creative-brief.json`, [the shared three-platform visual system](../textile-social-controller-v4/references/approved-visual-system.md), and [the approved caption system](references/approved-caption-system.md). Do not treat recent outputs as fixed templates.

Choose one asset mode before production.

For `real_product_single`, copy the source image byte-for-byte to `product-original.jpg`. Do not crop, retouch, upscale, add typography, duplicate it into a carousel, or mix in a different material. Record `asset_mode:real_product_single`, `ai_generated:false`, and the source-identical output hash in `usage.json`.

For `concept_single`, use exactly one approved 1080×1350 finished product scene named `product-concept.png`. Generate directly for the Instagram canvas. It must show the designed furniture/product in a complete environment, not the raw source swatch. Record `ai_generated:true`, retain the concept disclosure, and require the platform AI label.

For `concept_carousel`, generate at 1080×1350 without content cropping:

- `human-context.png` is the compatibility filename for the product-centered editorial hero. A person is optional and normally omitted unless the brief gives a concrete use-case reason. Use a furnished, controlled room with foreground, middle ground, background, and strong physically plausible directional light and shadow. Restrained editorial typography is allowed on this image.
- `product-closeup.png` is a people-free, text-free material evidence image from a clearly different angle. Show believable texture scale, pile or relief, seams, edges, drape, or compression.

Preserve the source material's visible color, motif outline, texture-unit size, pile direction, relief, sheen, and physical scale. Vary furniture type, room, composition, palette, light direction, and typography placement across concepts; do not merely recolor one scene. Reject impossible furniture, floating fabric, empty oversized rooms, copied account compositions, brand imitation, logos, watermarks, unreadable text, and unsupported claims.

Use only exact approved product names and neutral visual descriptors in cover typography. Check every letter; regenerate or repair the image if text is wrong.

Write `caption.txt` in one caption mode suited to the material and image: product editorial, human-use tension, or material design. Ground every sentence in supplied facts or visible evidence. Use one specific CTA and 3–5 relevant hashtags. Add the compact concept-visualization disclosure for `concept_single` and `concept_carousel`; do not imply AI generation for `real_product_single`. Do not mechanically describe slide order or force an engagement question. Create `usage.json` with `post_generation_crop:false` and run the V4 validator.

After a clean validation pass, run `v4_pipeline.py stage` to copy the immutable package into `社媒自动化V4/publish-ready/instagram/<run_id>/`. Production may stage a package but must not publish it.
