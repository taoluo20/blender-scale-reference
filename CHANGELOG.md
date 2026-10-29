# Changelog

## 1.6.0 - Mouse Placement and Ground Projection

- Inverse-project mouse placement onto world Z=0, retaining the screen-left gap and matching the ruler base to the pointer's screen height. Handle perspective, orthographic and rolled views without changing physical height or subtle smoothing.
- Release zero-height placement when the view centre and all visible geometry are below zero; follow the current view depth and restore Z=0 when leaving that state. Skip invalid horizon/clipped ground projections. Preserve existing frozen placements and selected-object measurements.
- Add the scene-saved **Ruler at Mouse Tip** checkbox, default off, with figure-aware placement and a disabled gap control while active. Preserve selection, attachment and Freeze behavior.
- Publish wide landscape viewport images; retain image embeds only on the latest GitHub release page.

## 1.5.1 - Scale Reference

- Rename the extension, panel, display checkbox, repository and new installer to **Scale Reference**.
- Refresh English and Simplified Chinese documentation and native viewport screenshots.
- Retain the internal extension ID and saved-data identifiers for existing scenes, frozen placements and attachments.
- Document the existing ft/in and scene-imperial readouts. Keep the 1.5.0 measurement behavior and defaults.

## 1.5.0 - Selection Defaults and Responsive Following

- Add **Only With Selection**, enabled by default, to hide live guides without selected measurable geometry. Keep existing Freeze placements and object attachments.
- Omit object/model captions from mouse-mode guides, including legacy frozen mouse snapshots.
- Reduce default follow smoothing to 0.02 s for slight easing; retain the 24 px minor tick spacing.
- Add **Show Half-Height Value**, disabled by default, without changing midpoint crossbars or minor ticks. Keep it editable while frozen.
- Capture the new text setting per attachment; preserve the historical visible midpoint for 1.4.0 attachment records without the new field.
- Keep reference figures opt-in and save the new checkbox settings with the scene.

## 1.4.0 — Object Attachments and Gray References

- Use neutral-gray shaded figures. Documentation screenshots show Epic's actual UE 5.8.2 Manny; keep source/derived meshes outside Git and the installer.

- Keep independent ruler/figure references beside multiple objects without replacing live selection/mouse following or toggling Freeze.
- Follow evaluated target movement, scale and height on the current viewport-left side, preserving physical figure height and captured appearance.
- Add a scene-saved list with batch checkboxes, per-row visibility/removal, show/hide selected and delete-all operations. Target objects are preserved.
- Retain reference meshes across live replacement/removal; support target rename, missing/hidden targets, Undo and saved-file persistence.
- Reuse ruler layout/drawing, separate per-entry animation states, and cache batches for multiple reference meshes.
- Prevent repeated drawing failures from flooding the console; clear the error after a successful frame while other references continue drawing.
- Retain the 200-check baseline; add 59 object-attachment checks, 8 drawing-error checks and native perspective review.

## 1.3.0 — Ruler Appearance and Smooth Following

- Add smooth world-space following, physical width offset, optional connectors and zoom-adaptive ticks/units.
- Keep distant/top views readable with one height and object name; eliminate duplicate text during unit and detail transitions.
- Group reference, placement/following and appearance controls; shorten the units label and show only the current state hint.
- Translucent white ruler and text defaults; remove the bottom caption.
- Keep only physical half-height and full-height labels on the screen-left side.
- Thinner crossbars without duplicate tick overdraw; endpoint, half-height and minor marks extend only screen-left from the axis.
- Add scene-saved minor tick spacing, defaulting to a sparser 24 px fade threshold. Adjust density while frozen without moving world positions.
- Use eye-level, non-isometric perspective views by default in preview scripts.
- Add line width, independent line/text RGBA and local TTF/OTF/TTC font selection.
- Preserve appearance in saved scenes and allow edits while frozen; fall back to Blender's font when a font path is missing.
- Retain compatibility with existing Freeze snapshots.

## 1.2.1 — Publication polish

- English UI source labels with optional Simplified Chinese translations.
- Shorter state hints and English-first bilingual documentation.
- Real Blender viewport previews, portable integration checks and reproducible packaging.
- Preserves the placement and Freeze behavior of 1.2.0.

## 1.2.0 — World-space Freeze

- Pin the current ruler and reference figure in world space.
- Capture the last visible mouse placement when clicking Freeze from the sidebar.
- Preserve placement through selection changes, camera navigation and saved-file reloads.

## 1.1.0 — Reference figures

- Load Blend, FBX, OBJ, glTF/GLB and STL models as a display-only reference figure.
- Add independent visibility, physical height, rotation and opacity controls.
- Preserve evaluated poses, exclude rig widgets, simplify heavy references and recover from failed imports.

## 1.0.0 — Height ruler

- Measure selected world-Z height and combined selections.
- Follow the mouse with a configurable reference height when nothing is selected.
- Add adaptive ticks, unit controls and a Scale sidebar panel.

---

## 简体中文

### 1.6.0 - 鼠标放置与地面投影

- 将鼠标放置反投影到世界 Z=0，保持屏幕左侧间距及尺子底部与鼠标的屏幕高度对齐；支持透视、正交和滚转视图，保留实际高度与轻微缓动。
- 观察中心与全部可见几何体都低于零时解除零高度约束，改为当前视口深度跟随，离开该状态后恢复 Z=0；跳过地平线及裁剪范围外的无效投影。已有冻结位置和选中物体测量保持原行为。
- 新增随场景保存的**尺子对齐鼠标尖端**复选框，默认关闭；兼容人物显示，启用时禁用间距控件，保留选中、绑定及冻结行为。
- 说明图采用宽幅横向视口截图；GitHub 只在最新版发布页保留图片。

### 1.5.1 - Scale Reference（尺度参考）

- 扩展、面板、显示开关、仓库及新安装包统一更名为 **Scale Reference**。
- 更新英文及简体中文说明和真实视口截图。
- 保留内部扩展 ID 与保存数据标识，兼容已有场景、冻结位置及物体绑定。
- 补充已有 ft/in 与场景英制读数的入口说明，保留 1.5.0 的测量行为和默认设置。

### 1.5.0 - 选中显示默认值与轻微跟随

- 新增默认开启的**仅选中时显示**，未选中可测量几何体时隐藏实时参照；已有冻结和物体绑定保留。
- 鼠标模式不再显示物体或模型名称，兼容旧版鼠标冻结快照。
- 跟随缓动默认降至 0.02 秒，保留轻微平滑；小刻度间距仍为 24 px。
- 新增默认关闭的**显示半高数值**，不改变中点横条或小刻度；冻结后仍可调整。
- 绑定条目保存新增半高设置；缺少该字段的 1.4.0 记录按旧行为显示中位文字。
- 参考人物仍需主动加载启用，新增开关随场景保存。

### 1.4.0 — 物体绑定参照与灰色人物

- 人物改为中性灰立体着色，项目示意图使用 Epic UE 5.8.2 的真实 Manny；原始及衍生网格不进入 Git 或安装包。

- 在多个物体旁保留独立尺子/人物，不替代实时选中或鼠标跟随，也不切换 Freeze。
- 跟随评估后的目标移动、缩放和高度，保持当前视口左侧、独立物理身高与创建时外观。
- 新增随场景保存的列表，支持勾选多条、逐条显隐/移除、批量显示/隐藏和全部删除；保留所有目标物体。
- 实时人物替换或移除后保留旧网格，处理目标改名、缺失与隐藏，支持撤销及保存重开。
- 复用布局和绘制，分离条目缓动状态，缓存多个人物网格的绘制批次。
- 防止连续绘制异常逐帧刷屏，成功绘制后清除错误，其他参照仍继续显示。
- 保持原有 200 项检查通过，新增 59 项绑定检查、8 项绘制异常检查与真实透视视口审查。

### 1.3.0 — 尺子外观与平滑跟随

- 新增世界空间平滑跟随、实际宽度偏移、可选连接线及随缩放变化的刻度和单位。
- 远景和俯视保留一个高度及物体名称；修复单位与细节过渡时的文字重叠。
- 分组参考人物、放置跟随和外观设置，缩短单位标签，只显示当前状态提示。
- 尺子与文字默认白色半透明，移除底部说明。
- 只保留实际半高与全高数值，均位于屏幕左侧。
- 横向刻度更细，避免重复绘制导致局部加深；上下端、半高及小刻度都只从竖线向屏幕左侧延伸。
- 新增随场景保存的小刻度间距，默认 24 px 渐显阈值，显示更稀疏；冻结时仍可调整，不移动世界位置。
- 预览脚本默认使用平视、非等距透视。
- 新增线粗细、线与文字各自 RGBA、TTF/OTF/TTC 字体文件选择。
- 外观随场景保存，冻结时仍可调整；字体文件缺失时回退到默认字体。
- 兼容已有冻结快照。

### 1.2.1 — 发布整理

- 界面使用英文源文字，并提供随 Blender 语言设置使用的简体中文翻译。
- 精简状态提示，补齐英文在前的双语文档。
- 提供真实视口预览、可移植测试与可重复构建。
- 保持 1.2.0 的放置与冻结行为。

### 1.2.0 — 三维冻结

固定尺子与人物的世界位置；支持侧栏捕获最后的鼠标参照；位置随场景保存，选择变化和相机导航不再带动参照。

### 1.1.0 — 参考人物

支持六种模型格式、人物独立显示、真实身高、朝向及不透明度；保留评估姿态，排除骨骼控制形状，简化大型参照，导入失败保留原模型。

### 1.0.0 — 高度尺

提供选中物体世界 Z 高度、多选整体高度、鼠标参考尺、自动刻度、单位及 Scale 侧栏。
