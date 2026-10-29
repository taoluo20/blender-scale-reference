# Height Axis 1.3.0

A Blender viewport height ruler and reference figure with view-left following and world-space Freeze.

This release adds adjustable ruler appearance and tick spacing, smooth following and clearer measurement transitions.

- Default to white translucent lines and text, with thinner crossbars.
- Show only half-height and full-height values on the left; remove the bottom caption.
- Draw every crossbar only screen-left from the axis. Add scene-saved minor tick spacing, default 24 px, editable while frozen.
- Add line width, independent line/text RGBA and local TTF/OTF/TTC font selection.
- Save appearance with the scene; use Blender's default font if an external font is missing.
- Add smooth world-space following, physical width offset and zoom-adaptive metric detail.
- Keep one readable measurement through unit/detail transitions; organize the sidebar into collapsible sections.

- Measure world-Z height beside the current selection, including combined selections.
- Follow the mouse on the left when nothing is selected.
- Load Blend, FBX, OBJ, glTF/GLB or STL as a configurable, shaded reference figure.
- Freeze both guides in world space, including from the sidebar in mouse mode.
- Save reference data and frozen placement with the blend file.
- English interface with optional Simplified Chinese translation.

Download `height-axis-1.3.0.zip` from this release and install it through Blender's **Preferences → Get Extensions → menu → Install from Disk**, then open **N → Scale**. The ZIP is the installer; the source archives are for development. `SHA256SUMS.txt` contains the package checksum.

Validation: 200 checks on Blender 5.2.2 LTS, isolated ZIP installation/enabling, and native non-isometric perspective review. Manifest minimum: Blender 4.5; the final build was not rerun on 4.5 or 5.1. The figure is a blue viewport reference; source textures and animation are not displayed. See the README for measurement and instance limits.

---

## 简体中文

Height Axis 1.3.0 是 Blender 的视口高度尺和参考人物插件，支持屏幕左侧跟随及世界位置冻结。本版新增尺子外观和刻度间距调节、平滑跟随及更清晰的读数过渡。

- 尺子与文字默认白色半透明，横向刻度更细。
- 只在左侧显示半高及全高，移除底部说明。
- 所有横向刻度只从竖线向屏幕左侧延伸；新增小刻度间距，默认 24 px，随场景保存且冻结后仍可调节。
- 新增线宽、线与文字各自 RGBA、TTF/OTF/TTC 字体文件选择。
- 外观随场景保存，外部字体缺失时自动使用默认字体。
- 新增世界空间平滑跟随、实际宽度偏移及随缩放变化的公制细节。
- 单位与细节过渡时只绘制一套清晰读数，侧栏按可折叠分组整理。

- 在选中物体左侧测量世界 Z 高度，支持多选整体范围。
- 未选中时在鼠标左侧跟随。
- 加载 Blend、FBX、OBJ、glTF/GLB 或 STL 作为可调身高的蓝色立体参照。
- 尺子和人物可同时冻结在三维位置，支持从侧栏冻结最后的鼠标参照。
- 参照数据与冻结位置随 blend 文件保存。
- 英文界面，包含随 Blender 设置使用的简体中文翻译。

从本发布页下载 `height-axis-1.3.0.zip`，在 **Preferences → Get Extensions → 菜单 → Install from Disk** 安装，然后进入 **N → Scale**。该 ZIP 是安装包，源码压缩包供开发使用；`SHA256SUMS.txt` 提供校验值。

验证：Blender 5.2.2 LTS 的 200 项检查、隔离配置内安装并启用 ZIP，以及真实非等距透视视口审查。清单最低版本为 Blender 4.5；最终构建没有在 4.5 或 5.1 重跑。人物只作蓝色视口参照，不显示源贴图和动画；测量及实例边界见 README。
