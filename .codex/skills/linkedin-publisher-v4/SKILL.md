---
name: linkedin-publisher-v4
description: Load one validated LinkedIn V4 single-image textile post, stop for final human approval, then publish once and record a verified permalink.
---

# LinkedIn publishing branch

Require passing validation, a confirmed member/Page identity, `platform=linkedin`, and one staged `product-concept.png`. Reject other platform packages and all files outside the selected `publish-ready/linkedin/<run_id>/` directory.

The branch may open LinkedIn, upload the staged image, add useful alt text, enter the exact caption, preserve disclosure controls, and verify the final preview without intermediate approval. Stop immediately before the final public `Post` action and ask the user to approve that exact post. After confirmation, click once, verify the live permalink, and record `publish-result.json`. Stop on identity, login, verification, duplicate, or permission uncertainty. This skill sends no notifications.
