# Scale Reference 1.5.1

The extension is now **Scale Reference**. The name covers both the viewport height ruler and optional physical reference figures.

- Updated extension name, sidebar panel, display checkbox, repository, new installer, documentation and native viewport screenshots.
- Kept the internal `height_axis` extension ID and saved-data identifiers. Update the existing extension to preserve scenes, frozen placements and object attachments.
- Imperial readouts already exist: **N > Scale > Units > ft / in**, or **Scene** to follow Blender's imperial unit system. Reference-height and width-offset inputs remain in metres.
- Preserved selection-only live display, no figure and no half-height value by default; subtle **0.02 s** following and unchanged **24 px** minor ticks. Freeze and saved object attachments remain available independently of live selection filtering.

![Scale Reference in Blender](https://raw.githubusercontent.com/taoluo20/blender-scale-reference/v1.5.1/docs/images/selected.png)

Download `scale-reference-1.5.1.zip` and use **Preferences > Get Extensions > menu > Install from Disk**. Enable **Scale Reference**, then **N > Scale > Show Scale Reference**. `SHA256SUMS.txt` contains the package checksum. Previously saved settings remain as authored.

Validation: **297 checks on Blender 5.2.2 LTS**, including imperial conversion, saved-file persistence and legacy attachment/Freeze compatibility. The final ZIP passed manifest validation, isolated installation and installed-namespace behavior checks. Ten public PNGs were refreshed from eight native non-isometric perspective states. Manifest minimum: Blender 4.5; this release was not tested on 4.5 or 5.1. See [validation](https://github.com/taoluo20/blender-scale-reference/blob/v1.5.1/docs/VALIDATION.md).

Optional figure screenshots use Epic's gray UE Manny. No Epic model or source assets are included in the repository or installer. See [source and attribution](https://github.com/taoluo20/blender-scale-reference/blob/v1.5.1/docs/UE_MANNEQUIN.md). Extension code remains GPL-3.0-or-later.

---

## 简体中文

插件现已更名为 **Scale Reference（尺度参考）**，同时涵盖视口高度尺和可选的实际比例参考人物。

- 更新扩展名称、侧栏面板、显示开关、仓库、新安装包、说明与真实视口截图。
- 保留内部 `height_axis` 扩展 ID 及保存数据标识；更新现有扩展后，已有场景、冻结位置和物体绑定可继续使用。
- 英制读数已经具备：进入 **N > Scale > Units / 单位**，选择 **ft / in**，或通过 **Scene / 场景**跟随 Blender 场景英制单位。参考高度及宽度偏移输入仍使用米。
- 默认保持仅选中显示实时参照、无人物、无半高数值，跟随缓动为轻微的 **0.02 秒**，小刻度间距仍为 **24 px**；冻结与保存的物体绑定独立于实时选择过滤。

下载 `scale-reference-1.5.1.zip`，通过 **Preferences > Get Extensions > 菜单 > Install from Disk** 安装。启用 **Scale Reference** 后，在 **N > Scale** 勾选 **Show Scale Reference / 显示尺度参考**。`SHA256SUMS.txt` 提供校验值；原来保存的设置保留。

验证：**Blender 5.2.2 LTS 的 297 项检查通过**，覆盖英制换算、保存重开与旧绑定/冻结兼容。最终 ZIP 通过清单、隔离安装和实际安装命名空间检查；8 种原生非等距透视状态重拍了 10 张公开 PNG。清单最低为 Blender 4.5，本轮未在 4.5 或 5.1 测试，详见[验证记录](https://github.com/taoluo20/blender-scale-reference/blob/v1.5.1/docs/VALIDATION.md)。

可选人物截图使用 Epic 灰色 UE Manny；仓库与安装包不包含 Epic 模型或源资产，详见[来源与署名](https://github.com/taoluo20/blender-scale-reference/blob/v1.5.1/docs/UE_MANNEQUIN.md)。插件代码继续采用 GPL-3.0-or-later。
