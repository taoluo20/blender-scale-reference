# Height Axis 1.5.0

This release makes the default ruler quieter and more responsive.

- **Only With Selection** starts enabled: select measurable geometry to display the live ruler. Uncheck it to restore mouse following.
- Reference figures and **Show Half-Height Value** start disabled. The full-height value stays on the left; all crossbars and the existing **24 px** minor tick spacing remain.
- Follow smoothing now defaults to **0.02 s**, retaining slight easing with a much faster response.
- Mouse-mode measurements have no object/model caption, including old frozen mouse snapshots.
- Change the half-height checkbox while frozen without moving the ruler or figure.
- Saved object attachments retain their captured midpoint setting. Existing 1.4.0 attachment records keep their historical midpoint labels.
- Existing explicit Freeze placements and object attachments remain visible independently of selection-only live filtering.

![Selection ruler and its display controls](https://raw.githubusercontent.com/taoluo20/blender-height-axis/v1.5.0/docs/images/selected.png)

Object attachments, batch visibility, gray reference figures, local model/font loading, automatic m/cm/mm detail and world-space Freeze remain available. Display and Freeze still start disabled; enable **Show Height Axis** in **N > Scale** to begin. New settings save with the blend file. Previously saved values remain as authored.

Download `height-axis-1.5.0.zip` and install it through **Preferences > Get Extensions > menu > Install from Disk**. `SHA256SUMS.txt` contains the package checksum.

Validation: **297 checks on Blender 5.2.2 LTS**, comprising the retained 267-check baseline and 30 checks for selection-only behavior, responsive easing, text toggles, save/reopen and old attachment/Freeze compatibility. Actual font loading is included. The final ZIP passed isolated installation and installed-namespace behavior checks; ten public images were refreshed from eight native perspective states. Manifest minimum: Blender 4.5; this update was not run on 4.5 or 5.1. See [validation](https://github.com/taoluo20/blender-height-axis/blob/v1.5.0/docs/VALIDATION.md).

Optional mannequin examples use Epic's gray UE Manny. No Epic model or source assets are included in the installer or repository; see [source and attribution](https://github.com/taoluo20/blender-height-axis/blob/v1.5.0/docs/UE_MANNEQUIN.md). Extension code remains GPL-3.0-or-later.

---

## 简体中文

此版本减少默认显示内容，并提高跟随响应速度。

- 默认开启**仅选中时显示**，选中可测量几何体后显示实时尺子；取消勾选可恢复鼠标跟随。
- 默认关闭参考人物及**显示半高数值**，保留左侧全高读数；横条与原有 **24 px** 小刻度间距保持不变。
- 跟随缓动默认改为 **0.02 秒**，保留轻微平滑并更快响应。
- 鼠标模式的尺寸下方不显示物体或模型名称，兼容旧版鼠标冻结快照。
- 冻结后仍可切换半高文字，不移动尺子或人物。
- 新绑定保存创建时的半高设置；1.4.0 旧绑定继续显示原来的中位文字。
- 已显式冻结及已绑定的参照不受实时“仅选中时显示”过滤影响。

物体绑定、批量显隐、中性灰参考人物、模型和字体加载、m/cm/mm 细节以及三维冻结继续保留。总显示开关与冻结仍默认关闭，进入 **N > Scale** 勾选**显示高度轴**即可开始。新增设置随 blend 文件保存，原来显式保存的设置保留。

下载 `height-axis-1.5.0.zip`，通过 **Preferences > Get Extensions > 菜单 > Install from Disk** 安装。`SHA256SUMS.txt` 提供校验值。

验证：**Blender 5.2.2 LTS 的 297 项检查通过**，包含原有 267 项及新增 30 项选择过滤、轻微缓动、文字开关、保存重开与旧绑定/冻结兼容检查，并测试了实际字体加载。最终 ZIP 通过隔离安装和实际扩展命名空间行为检查；8 种原生透视状态重拍了 10 张公开图片。清单最低版本为 Blender 4.5，本轮未在 4.5 或 5.1 运行，详见[验证记录](https://github.com/taoluo20/blender-height-axis/blob/v1.5.0/docs/VALIDATION.md)。

可选人物示例使用 Epic 的灰色 UE Manny；安装包和仓库不包含 Epic 模型或源资产，详见[来源与署名](https://github.com/taoluo20/blender-height-axis/blob/v1.5.0/docs/UE_MANNEQUIN.md)。插件代码继续采用 GPL-3.0-or-later。
