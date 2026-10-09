# 纺织三平台社媒自动化｜教师测试版

这是一个可以在新 Mac 上独立运行的 Codex 项目。它包含 Instagram、Facebook、LinkedIn 三套相互隔离的内容生产与发布工作流，不包含原作者的账号、Cookie、历史帖子、生成图片或发布记录。

## 最快开始

1. 在 GitHub 页面点击 `Code` → `Download ZIP`。
2. 解压后打开“终端”，进入解压目录。
3. 运行：

   ```bash
   python3 setup_teacher.py
   ```

4. 脚本会在桌面创建 `纺织社媒自动化`，并从 Hysure 官方网站下载第01批20个原素材。
5. 用 Codex 打开桌面的 `纺织社媒自动化` 文件夹。
6. 在 Safari 分别登录 Instagram、Facebook 和 LinkedIn。
7. 先输入：`检查三平台环境，不发布`。
8. 检查通过后输入：`开始三平台社媒自动化测试`。

完整步骤见 [老师快速测试.md](老师快速测试.md)。

## 工作流边界

- 每个平台依次执行：原材料读取 → 规则与策略 → 平台原生图文生产 → 发布预览。
- Instagram 与 LinkedIn 使用 1080×1350；Facebook 使用 1200×1500。
- 三个平台分别生成图片，禁止用同一张图裁剪成三个尺寸。
- 自动化可以完成上传、文案填写和最终预览，但必须停在最后的 `Share` / `Post` / `Publish` 前等待人工确认。
- 只有公开帖子和永久链接都能验证时，才记录为发布成功。

## 首批素材

默认素材目录：

```text
~/Desktop/纺织社媒自动化/素材库/第01批-20个/
```

每个素材都包含原图、同名来源说明和 SHA-256；`manifest.json` 记录官网页面、官方图片地址和下载时间。重复运行会校验并复用一致文件，不会重复覆盖。

手动重新校验或补齐第一批：

```bash
python3 社媒自动化V4/scripts/download_materials.py --batch 1 --batch-size 20
```

## 本机配置

首次安装会创建未纳入 Git 的 `社媒自动化V4/config.local.json`。老师可以在其中填写三个平台的预期公开账号名。密码、Cookie、验证码和令牌不得写入任何项目文件。

## 系统要求

- macOS
- Python 3.9 或更高版本
- Codex 桌面版
- Safari
- 可访问 Hysure、Instagram、Facebook、LinkedIn 的网络

本项目不包含任何社媒平台官方 API 密钥，网页结构变化、验证码、账号权限或地区限制都可能让自动化停下并要求人工处理。

