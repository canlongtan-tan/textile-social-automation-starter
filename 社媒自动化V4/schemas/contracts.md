# V4 数据合同

数据合同也是上下文边界。分支只读取本节列出的直接输入，不应加载其他平台目录或整个历史记录。

## `source-manifest.json`

必填：`run_id`、`platform`、`source_path`、`source_sha256`、`sidecar_path`、`facts`、`created_at`。源文件只读。

仅供对应平台的策略分支读取。

## `creative-brief.json`

必填：`platform`、`objective`、`audience`、`canvas`、`research_reviewed_at`、`sample_observations`、`visual_direction`、`caption_direction`、`generation_prompts`、`disclosure`。

当前 `concept_single` 的 `generation_prompts` 固定包含 `product_concept`：完整成品家具编辑场景，人物默认省略，必须有完整环境层次、方向性光影、景深和核对无误的克制排版。三平台引用同一视觉边界，但提示词和成图必须按平台独立产生。

历史 `concept_carousel` 仍兼容 `human_context` 与 `product_closeup` 字段，但不作为当前录屏演示默认模式。

生产分支只读取本文件、源图和源清单，不读取研究抓取过程。

Instagram 的 `caption_direction` 还必须指定：三种文案模式之一（产品编辑、生活问题、材料设计）、允许描述的可见证据、一个且仅一个 CTA、披露文案、禁用主张和 3–5 个相关标签范围。问题句可选，不得强制每篇提问。

## `usage.json`

必填：`platform`、`source_sha256`、`asset_mode`、`ai_generated`、`post_generation_crop:false`、`images`。

- `real_product_single`：只允许 `product-original.jpg`，`role=real_product`、`ai_generated:false`，文件 SHA-256 必须与源图完全一致；不得裁切、修图、放大、排字、复制成两张或混入其他材质。
- `concept_single`：只允许一张符合目标平台配置尺寸的完整成品场景图 `product-concept.png`，`role=product_concept`、`ai_generated:true`；Instagram/LinkedIn 为 1080×1350，Facebook 为 1200×1500。不得用原材质图代替成品，不得临时补一张原材质图凑轮播。
- `concept_carousel`：包含 `human-context.png`、`product-closeup.png` 两张 1080×1350 图片，二者角度说明必须不同，并保留概念图披露。

## 平台成品包

每个平台目录必须包含公共文件：

- `source-manifest.json`
- `creative-brief.json`
- `caption.txt`
- `usage.json`
- 校验后生成的 `validation.json`

媒体文件按模式三选一：`real_product_single` 只包含 `product-original.jpg`；`concept_single` 只包含 `product-concept.png`；`concept_carousel` 包含 `human-context.png` 与 `product-closeup.png`。

发布后才允许出现 `publish-result.json`，字段包括 `status`、`attempted_at`、`verified_at`、`permalink`、`visible_account`、`error`。只有 `status=published_verified` 且永久链接可打开才算完成。

## 待发布包

平台成品包通过校验后，必须运行 `v4_pipeline.py stage`，复制到 `社媒自动化V4/publish-ready/<platform>/<run_id>/`。目录包含对应模式的媒体文件、`caption.txt`、源清单、创意简报、`usage.json`、`validation.json` 和 `publish-ready.json`。

`publish-ready.json` 必填：`status:ready`、`platform`、`run_id`、`asset_mode`、`ai_generated`、`expected_account`、`source_package`、`media_order`、`caption_file`、每个文件的 SHA-256。发布前必须运行 `verify-ready`；任何缺失、哈希变化、模式变化、顺序变化或平台不匹配都停止。

发布分支只读取单个已经通过 `verify-ready` 的待发布包，不再直接从 `outputs` 抓取文件；复盘分支只读取永久链接、发布结果和平台分析数据。
