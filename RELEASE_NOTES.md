# Height Axis 1.4.0

A Blender viewport height ruler and reference figure with view-left following and world-space Freeze.

This release adds object attachments, a batch visibility list and neutral-gray reference shading.

- Attach the current ruler, figure or both to an object while live selection/mouse following continues independently.
- Retain multiple view-left references that follow evaluated target movement, scale and height, with physical figure height and captured appearance.
- Show/hide checked entries, toggle or remove one entry, or delete all attachment records while preserving target objects. Save with the scene and support Undo.
- Keep old reference meshes after live replacement/removal; handle target rename, hidden/missing targets and Overlays. See [object attachments](docs/OBJECT_ATTACHMENTS.md).
- Project screenshots use Epic's gray UE Manny. The character model is not included in the installer; see [source and attribution](docs/UE_MANNEQUIN.md).

![Saved object attachments with an independent live reference](https://raw.githubusercontent.com/taoluo20/blender-height-axis/v1.4.0/docs/images/object-attachments.png)

The 1.3.0 ruler and following features remain available:

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

Download `height-axis-1.4.0.zip` from this release and install it through Blender's **Preferences → Get Extensions → menu → Install from Disk**, then open **N → Scale**. `SHA256SUMS.txt` contains the package checksum.

Repeated drawing failures log once until recovery, while other references continue drawing. Validation: 267 checks on Blender 5.2.2 LTS, including the 200-check baseline, 59 attachment checks and 8 drawing-error checks; native non-isometric perspective review and checkpointed Blender Undo. Manifest minimum: Blender 4.5; this update was not run on 4.5 or 5.1. The figure is a neutral-gray viewport reference; source textures and animation are not displayed. See the README for measurement and instance limits.

---

## 简体中文

Height Axis 1.4.0 新增物体绑定参照、批量显隐列表及中性灰参考人物着色。

- 将当前尺子、人物或二者绑定到物体，实时选择/鼠标跟随继续独立运行。
- 多个参照按当前视口左侧跟随目标评估后的移动、缩放和高度，并保留物理参考身高及创建时外观。
- 支持勾选多条后批量显隐、逐条开关及移除、全部删除绑定记录；保留目标物体，随场景保存并支持撤销。
- 实时人物替换或移除后保留旧绑定网格，处理目标改名、隐藏、缺失和 Overlays。详见[物体绑定说明](docs/OBJECT_ATTACHMENTS.md)。
- 项目示意图使用 Epic 的灰色 UE Manny；安装包不包含该人物模型，详见[来源与署名](docs/UE_MANNEQUIN.md)。

继续保留 1.3.0 的尺子与跟随功能：

- 尺子与文字默认白色半透明，横向刻度更细。
- 只在左侧显示半高及全高，移除底部说明。
- 所有横向刻度只从竖线向屏幕左侧延伸；新增小刻度间距，默认 24 px，随场景保存且冻结后仍可调节。
- 新增线宽、线与文字各自 RGBA、TTF/OTF/TTC 字体文件选择。
- 外观随场景保存，外部字体缺失时自动使用默认字体。
- 新增世界空间平滑跟随、实际宽度偏移及随缩放变化的公制细节。
- 单位与细节过渡时只绘制一套清晰读数，侧栏按可折叠分组整理。

- 在选中物体左侧测量世界 Z 高度，支持多选整体范围。
- 未选中时在鼠标左侧跟随。
- 加载 Blend、FBX、OBJ、glTF/GLB 或 STL 作为可调身高的中性灰立体参照。
- 尺子和人物可同时冻结在三维位置，支持从侧栏冻结最后的鼠标参照。
- 参照数据与冻结位置随 blend 文件保存。
- 英文界面，包含随 Blender 设置使用的简体中文翻译。

从本发布页下载 `height-axis-1.4.0.zip`，在 **Preferences → Get Extensions → 菜单 → Install from Disk** 安装，然后进入 **N → Scale**。`SHA256SUMS.txt` 提供校验值。

连续相同绘制异常只记录一次，恢复后可重新记录，其他参照继续绘制。验证：Blender 5.2.2 LTS 的 267 项检查，包含原有 200 项、59 项绑定检查及 8 项绘制异常检查；真实非等距透视视口及带明确检查点的 Blender 原生撤销。清单最低版本为 Blender 4.5，本轮未在 4.5 或 5.1 运行。人物只作中性灰视口参照，不显示源贴图和动画；测量及实例边界见 README。
