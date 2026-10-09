---
name: instagram-publisher-v4
description: Load one validated Instagram V4 textile post, stop for final human approval, then publish once and record a verified permalink.
---

# Instagram publishing branch

Read only one staged directory under `社媒自动化V4/publish-ready/instagram/`; do not scan raw `outputs` for files. Run `v4_pipeline.py verify-ready`, require `publish-ready.json` status `ready`, verify its hashes, asset mode, media order, `instagram` platform, and intended visible account. Reject Facebook or LinkedIn packages.

For `real_product_single`, upload only `product-original.jpg`; leave the AI label off only when `ai_generated:false` and the image hash matches the source manifest. For `concept_single`, upload only `product-concept.png`. For `concept_carousel`, upload `human-context.png` first and `product-closeup.png` second. Preserve the disclosure and turn on the platform AI label for both concept modes.

The branch may open Instagram, upload the staged media, enter the exact `caption.txt`, set disclosure controls, and verify the final preview without intermediate approval. Stop immediately before the final public `Share` action and ask the user to approve that exact post. After confirmation, click once, verify the visible post and permanent link, then record `publish-result.json` in the source package and mark the staged manifest published. A Share click alone is not success. Stop on login, account, verification, duplicate, hash, or challenge uncertainty. This skill sends no notifications.
