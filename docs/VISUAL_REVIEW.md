# Visual Review — 2026-10-29

**English** · [简体中文](#简体中文)

## 1.6.0 mouse projection and tip placement

Reviewed the new main-panel checkbox, disabled gap state, screen-matched grounded placement and automatic underground release. Twelve wide native PNGs cover ten perspective states, including mouse-left, mouse-tip and underground examples. Each mouse capture verifies the projected base against the target pixel within 0.01 px. The full integration suite passed 336 checks. New release pages keep the current gallery only; older release image embeds are removed without rewriting tags or installers.

## 1.5.1 naming review

Recaptured all ten public PNGs from eight native perspective states for the **Scale Reference** panel and **Show Scale Reference** checkbox. English and Chinese labels fit the sidebar; default selection, optional mouse/Freeze, appearance, midpoint and object-attachment states retain the 1.5.0 behavior. All captured states reported no draw errors.

## 1.5.0 default display review

The default review now shows a selected-object ruler without a figure or half-height value, using 0.02 s following and unchanged 24 px ticks. Eight actual non-isometric perspective states cover selection, deselection hiding, nameless optional mouse following, nameless mouse Freeze, custom appearance, optional half-height, Chinese UI and optional gray-Manny bindings. Ten public PNGs were refreshed. The binding example keeps two saved references beside A/B and a separate live reference beside C, with the list visible and labels separated. All states reported no draw errors. See the [visual guide](VISUAL_GUIDE.md) and [validation record](VALIDATION.md).

## Earlier 1.3.0 review

Reviewed the local 1.3.0 source, placement and Freeze logic, reference rendering, fonts, translations, packaging, tests and documentation. Native viewport checks used Blender 5.2.2 LTS and a separate generated review scene.

| Finding | Adjustment |
| --- | --- |
| Automatic units superimposed different numbers during a unit crossfade. | Draw the dominant unit once, using its transition opacity. |
| Near/far transitions could draw the full measurement and object name twice. | Share one readout and move it smoothly between midpoint and endpoint. |
| The default sidebar clipped the Display Units label and mixed placement with figure controls. | Use the shorter Units label; group Reference Figure, Placement & Follow and Ruler Appearance. |
| Both following-state hints were always visible. | Show the current selection, mouse or frozen state. |
| Figure controls remained active with the figure hidden. | Dim rotation and opacity when figure display is off. |
| Minor tick density was fixed, and major crossbars crossed the axis. | Add scene-saved Tick Spacing, default 24 px; draw all marks only horizontally left from the axis, including while frozen. |

The existing translucent white ruler, sparse height values, smaller object name and blue figure remain the visual basis. Placement and appearance sections collapse independently. Model removal sits beside the filename.

Native captures cover selection, distant view, detail transition, top view, selection Freeze, mouse following, mouse Freeze, figure-only display, hidden Overlays, custom colors/font and Simplified Chinese. Updated public previews are in the [visual guide](VISUAL_GUIDE.md). Local screenshots, capture evidence and a saved review blend are under the ignored `verification/visual-review/` directory.

The initial Blender 5.2.2 integration run passed 188 checks, including four new transition regression checks and one Chinese-heading check. The tick-spacing follow-up passed 200 checks and added six native perspective captures; see the [validation record](VALIDATION.md). A generic Placement heading collided with Blender's built-in translation, so the extension uses Placement & Follow. This review does not constitute a new Blender 4.5 or 5.1 verification. These changes are included in version 1.3.0.

---

## 简体中文

### 1.6.0 鼠标投影与尖端放置

检查了主面板的新复选框、禁用的间距状态、地面屏幕对齐及地下自动解除约束。12 张宽幅原生 PNG 覆盖 10 种透视状态，包含鼠标左侧、鼠标尖端及地下示例。每个鼠标截图的投影底点均与目标像素核对，误差小于 0.01 px；完整集成检查通过 336 项。发布页只保留当前图库，撤下旧版图片嵌入，不改写历史标签及安装包。

### 1.5.1 更名审查

围绕 **Scale Reference** 面板与 **Show Scale Reference / 显示尺度参考**开关，从 8 种真实透视状态重拍全部 10 张公开 PNG。中英文标签在侧栏内完整显示；默认选中、可选鼠标/冻结、外观、半高和绑定状态保持 1.5.0 行为，所有截图状态均无绘制异常。

### 1.5.0 默认显示审查

默认预览展示选中物体的尺子，不显示人物与半高数值，跟随为 0.02 秒，小刻度仍为 24 px。8 种真实非等距透视状态覆盖选中、取消选择隐藏、无名称的可选鼠标跟随和鼠标冻结、自定义外观、可选半高、中文界面及可选灰色 Manny 绑定，重拍了 10 张公开 PNG。绑定示例同时展示 A/B 的两个已保存参照和 C 的独立实时参照，列表可见，标签互不重叠，所有状态均无绘制异常。详见[视觉指南](VISUAL_GUIDE.md)及[验证记录](VALIDATION.md)。

### 较早的 1.3.0 审查

本轮通读了本地 1.3.0 源码、放置与冻结逻辑、人物绘制、字体、翻译、打包、测试及文档。使用 Blender 5.2.2 LTS 和独立生成的审查场景检查真实视口。

| 问题 | 调整 |
| --- | --- |
| 自动单位渐变时，不同数值叠在同一位置。 | 只绘制当前权重较高的单位，并保留过渡透明度。 |
| 远近过渡可能重复绘制全高与物体名称。 | 共用一套读数，在中点与顶点之间平滑移动。 |
| 默认侧栏截断单位标签，放置参数和人物控件混在一起。 | 缩短单位标签，分为参考人物、放置与跟随、尺子外观。 |
| 同时显示两种跟随状态提示。 | 只显示当前选中、鼠标或冻结状态。 |
| 人物隐藏后仍可操作其显示参数。 | 人物关闭时弱化朝向和不透明度控件。 |
| 小刻度密度固定，主要横线跨过竖线。 | 新增随场景保存的小刻度间距，默认 24 px；包括冻结时在内，全部横线只水平向左延伸。 |

沿用白色半透明尺子、精简高度数值、较小物体名称及蓝色人物的视觉基础。放置与外观可分别折叠；移除人物按钮收在文件名旁。

实际截图覆盖选中、远景、细节过渡、俯视、选中冻结、鼠标跟随、鼠标冻结、仅人物、关闭 Overlays、自定义颜色及字体、简体中文共 11 种状态。[视觉指南](VISUAL_GUIDE.md)已更新公开预览；截图、捕获记录和可继续检查的 blend 文件位于忽略目录 `verification/visual-review/`。

首轮 Blender 5.2.2 集成检查通过 188 项，其中包含 4 项新增过渡回归检查及 1 项中文标题检查。小刻度间距后续修改通过 200 项检查，并增加 6 张原生透视截图，详见[验证记录](VALIDATION.md)。原先通用的 Placement 标题与 Blender 内置翻译冲突，已改用 Placement & Follow。本轮没有重新验证 Blender 4.5 或 5.1。这些调整纳入 1.3.0 版本。
