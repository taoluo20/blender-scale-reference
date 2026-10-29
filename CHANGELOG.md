# Changelog

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
