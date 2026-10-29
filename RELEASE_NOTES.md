# Scale Reference 1.6.0

This release completes the mouse-placement update with **Ruler at Mouse Tip**, grounded screen projection and automatic underground placement.

- **Ruler at Mouse Tip** starts off. Uncheck **Only With Selection**, then enable it to place the ruler base directly at the pointer. The saved left gap returns when disabled. The option saves with the scene and supports optional reference figures.
- Normal mouse placement starts at **world Z=0** while matching the pointer's screen height and left pixel gap. Perspective, orthographic and rolled views retain physical height.
- When the view centre and every visible measurable object's entire geometry are below zero, placement follows the current view depth. Returning to a ground-constrained view immediately restores Z=0.
- Ground projections at the horizon, behind the view or beyond depth clipping are hidden instead of jumping far away.
- Selection measurements, saved object attachments and existing Freeze positions remain compatible. Defaults stay selection-only, no figure, no midpoint, **0.02 s** following and **24 px** ticks.

![Ruler at Mouse Tip in the actual Blender viewport](https://raw.githubusercontent.com/taoluo20/blender-scale-reference/v1.6.0/docs/images/mouse-tip.png)

![Automatic underground placement](https://raw.githubusercontent.com/taoluo20/blender-scale-reference/v1.6.0/docs/images/underground.png)

Download `scale-reference-1.6.0.zip` and use **Preferences > Get Extensions > menu > Install from Disk**. Update the existing **Scale Reference** extension; its internal ID remains `height_axis`. Imperial **ft / in** and scene units remain available.

Validation: **336 checks on Blender 5.2.2 LTS**, isolated ZIP installation, saved-scene compatibility and native perspective review. Twelve public screenshots use wide landscape viewports. Only the latest release page retains screenshot embeds. The manifest minimum is Blender 4.5; this release was not tested on 4.5 or 5.1. See [validation](https://github.com/taoluo20/blender-scale-reference/blob/v1.6.0/docs/VALIDATION.md).

Extension code remains GPL-3.0-or-later. Optional Manny examples contain no bundled Epic geometry; see [source and attribution](https://github.com/taoluo20/blender-scale-reference/blob/v1.6.0/docs/UE_MANNEQUIN.md).

---

## 简体中文

本版本完成本轮鼠标放置更新，加入**尺子对齐鼠标尖端**、地面投影对齐及自动地下放置。

- **尺子对齐鼠标尖端**默认关闭。取消**仅选中时显示**后勾选此项，尺子底部直接位于指针处；关闭后恢复保存的左侧间距。开关随场景保存，兼容可选参考人物。
- 普通鼠标模式从**世界 Z=0** 开始，底部在屏幕上对应鼠标高度及左侧像素间距；支持透视、正交与滚转视图，保留实际高度。
- 观察中心及所有可见可测量物体的全部几何体都低于零时，改用当前视口深度跟随；返回受约束视图后立即恢复 Z=0。
- 地平线、视图后方及深度裁剪范围外的无效投影会隐藏，避免尺子跳远。
- 选中测量、物体绑定及已有冻结位置保持兼容；默认仍为仅选中显示、无人物、无半高、**0.02 秒**缓动及 **24 px** 刻度间距。

下载 `scale-reference-1.6.0.zip`，通过 **Preferences > Get Extensions > 菜单 > Install from Disk** 更新现有 **Scale Reference** 扩展，内部 ID 仍为 `height_axis`。英制 **ft / in** 和场景单位继续保留。

验证：**Blender 5.2.2 LTS 的 336 项检查通过**，并验证隔离安装、场景兼容及真实透视视口。12 张公开截图均采用宽幅横向视口；发布页只在最新版保留截图。清单最低为 Blender 4.5，本版本未在 4.5 或 5.1 测试，详见[验证记录](https://github.com/taoluo20/blender-scale-reference/blob/v1.6.0/docs/VALIDATION.md)。

插件代码保持 GPL-3.0-or-later；可选 Manny 示例不打包 Epic 几何体，详见[来源与署名](https://github.com/taoluo20/blender-scale-reference/blob/v1.6.0/docs/UE_MANNEQUIN.md)。
