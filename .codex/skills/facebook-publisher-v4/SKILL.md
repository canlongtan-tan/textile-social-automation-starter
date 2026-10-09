---
name: facebook-publisher-v4
description: Load one validated Facebook V4 single-image textile post, stop for final human approval, then publish once and record a verified permalink.
---

# Facebook publishing branch

Require passing validation, a confirmed visible Page/profile, `platform=facebook`, and one staged `product-concept.png`. Reject all cross-platform packages and all files outside the selected `publish-ready/facebook/<run_id>/` directory.

The branch may open Facebook, upload the staged image, enter the exact caption, set disclosure/safety controls, and verify the final preview without intermediate approval. Stop immediately before the final public `Post` action and ask the user to approve that exact post. After confirmation, click once, verify the live post and permalink, and write `publish-result.json`. A button click is not completion. Stop on account, login, security, duplicate, or visibility uncertainty. This skill sends no notifications.
