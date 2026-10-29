# Height Axis for Blender

A viewport height ruler and reference figure that stay on the **view-left side** of your selection or mouse. Freeze them wherever you want a lasting scale reference.

**English** · [简体中文](#简体中文)

Version **1.5.0** defaults to **Only With Selection**, no reference figure and no half-height value. Enable **Show Height Axis** and select geometry to measure it. Following now uses a subtle **0.02 s** response; minor tick spacing remains **24 px**. Mouse following and the midpoint value are optional checkboxes, and existing Freeze placements and object attachments remain available.

Version **1.4.0** adds persistent object attachments and a batch visibility list while preserving live following and Freeze. Reference figures use neutral-gray shading. See [object attachments](docs/OBJECT_ATTACHMENTS.md) for the new workflow.

Version **1.3.0** adds a translucent white ruler, adjustable minor tick spacing, left-only crossbars, appearance controls, smooth world-space following and zoom-adaptive detail. Unit and detail transitions keep one readable measurement, and sidebar controls are grouped by purpose.

![Height Axis in Blender: selection height and the Scale sidebar](docs/images/selected.png)

[Download the latest release](https://github.com/taoluo20/blender-height-axis/releases/latest) · [Visual guide](docs/VISUAL_GUIDE.md) · [Features and behavior](docs/FEATURES_AND_LOGIC.md) · [Build and test](docs/DEVELOPMENT.md)

## Three placement states

| State | Ruler and figure behavior |
| --- | --- |
| **Selection** | Measure the visible selected geometry's world-Z height. Keep the guides to its screen-left as you orbit the viewport. Multi-selection measures the combined height. |
| **Mouse** | Uncheck **Only With Selection** to follow the mouse on the left when nothing is selected. The reference height defaults to **1.8 m**; no object or model name is displayed. |
| **Frozen** | Pin the displayed ruler and figure in **world space**. Mouse movement, selection changes and viewport orbit no longer reposition them. Uncheck **Freeze** to resume following. |

The reference figure keeps its configured physical height, so a 1.8 m person can be compared with a 3.2 m object. It is not stretched to match the target.

Use **Object Attachments → Attach to Object** to retain a reference beside the active object. Select another object to continue using the independent live guide. The scene-saved list supports batch show/hide and removal while preserving target objects.

## Install and use

1. Download `height-axis-1.5.0.zip` from the [1.5.0 release](https://github.com/taoluo20/blender-height-axis/releases/tag/v1.5.0).
2. In Blender, open **Edit → Preferences → Get Extensions → menu → Install from Disk**, select the ZIP, and enable **Height Axis**.
3. In the 3D Viewport press **N**, open **Scale**, enable **Show Height Axis**, and select geometry.

Use **Load Reference Figure** to choose a `.blend`, `.fbx`, `.obj`, `.gltf`, `.glb` or `.stl` model. Adjust **Reference Height (m)**, **Figure Rotation** and **Figure Opacity**. The figure has its own display checkbox.

Enable **Freeze** to preserve the current placement. In mouse mode you can move into the sidebar to click it: the last visible viewport placement is retained. Placement and reference data save with the `.blend` file.

The main panel contains visibility, selection-only display, Freeze, reference height and units. **Reference Figure** contains model loading and figure controls. Expand **Placement & Follow** for the physical width offset, mouse gap, subtle 0.02 s default follow smoothing and optional connection lines. Expand **Ruler Appearance** to change font size, line width, minor tick spacing, **Show Half-Height Value**, overall opacity, line RGBA and text RGBA. **Tick Spacing (px)** remains 24: increase it for fewer minor ticks, or decrease it for more. The midpoint-value checkbox changes text only; all crossbars and minor ticks remain. These appearance settings stay editable while frozen and save with the scene. **Choose Font File** accepts local TTF, OTF and TTC files; the reset icon restores Blender's default font. Font files stay external: if a saved path is unavailable, labels use the default font and the panel shows a warning.

The interface uses English source labels and includes Simplified Chinese translations through Blender's language settings. Display, Freeze, reference figures and half-height values start off; **Only With Selection** starts on. Selection-only filtering controls the live guide and preserves explicitly frozen guides and stored object attachments. Hiding viewport Overlays hides all guides.

## What is included

- Live evaluated geometry bounds, including object transforms and mesh modifiers.
- World-Z height for combined selections; live edit-mesh bounds in Edit Mode.
- Adaptive ruler ticks and scene units, or explicit m / cm / mm / ft / in.
- Translucent white lines and text by default, with the full-height value on the left and an optional half-height value. The bottom caption is removed; all crossbars extend only left from the axis and stay thinner than the main line.
- Independent line/text colors and alpha, line width, font size and local font selection, all editable while frozen.
- Smooth world-space following, optional connection lines, and a physical offset outside the selection's horizontal envelope. Negative offsets move the guides inward.
- Adjustable, sparse-by-default decimal tick levels down to 1 mm and automatic m / cm / mm units as you zoom. Distant or top views retain one height readout and a smaller object name. Transitions draw each reading once.
- A shaded neutral-gray reference figure, independent from the scene's selectable objects and final render.
- Model import with replacement, failure recovery, reference-only display and saved-file persistence.
- World-space Freeze for both selection and mouse placement.
- No added hotkeys or network service dependency.

## Compatibility and limits

The manifest declares **Blender 4.5+**. Version 1.5.0 passed **297 checks on Blender 5.2.2 LTS**, including actual font loading and old attachment/Freeze compatibility. Its final ZIP passed isolated installation, new-default and attachment checks. Eight native perspective states produced ten updated public screenshots, including the English and Chinese controls. Earlier baseline checks ran on 5.1.2; this update was not rerun on 4.5 or 5.1. See [validation details](docs/VALIDATION.md).

- Height follows **world Z**, not an object's local axis. In Edit Mode the editable mesh is measured before final modifiers.
- Unrealized instances are not included in the selection height. Realize or convert them first when needed.
- Mouse placement uses a view-depth plane through the 3D Cursor; it does not automatically snap to the surface under the pointer.
- Near a top/bottom view, the projected Z ruler collapses to a height readout and object name. The numbers remain physical heights.
- Reference models use a single neutral-gray shaded style, with no source textures or animation playback. Hidden/non-rendering meshes and bone widgets are excluded. Large references are simplified to a display budget of about 150,000 triangles.
- Import requires Object Mode. Loading a new model successfully resumes following; removing a figure leaves a frozen ruler in place.
- Guides can be clipped at viewport edges. Frozen positions naturally change screen projection when the camera moves.

## Documentation

The repository keeps the extension in `height_axis/`, public guides and previews in `docs/`, portable checks in `tests/`, and build tools in `tools/`. Generated installers are distributed through Releases.

- [Visual guide](docs/VISUAL_GUIDE.md): controls, colors and examples.
- [Object attachments](docs/OBJECT_ATTACHMENTS.md): binding and batch-list behavior.
- [Visual review](docs/VISUAL_REVIEW.md): findings, adjustments and exercised viewport states.
- [Features and logic](docs/FEATURES_AND_LOGIC.md): state transitions, measurement rules and persistence.
- [Development](docs/DEVELOPMENT.md): reproducible packages and isolated Blender checks.
- [Changelog](CHANGELOG.md) · [License](LICENSE): GPL-3.0-or-later.

Optional figure examples show Epic's UE 5.8.2 Manny in neutral gray; the default preview contains no figure. [Source and license](docs/UE_MANNEQUIN.md) · [Third-party notice](THIRD_PARTY_NOTICES.md). The demonstration model is not included; load your own reference figure. Automated tests use this project's self-authored mannequin. No third-party character geometry is bundled.

---

## 简体中文

**1.5.0** 默认开启**仅选中时显示**、关闭参考人物和半高数值。勾选**显示高度轴**并选择几何体即可测量；跟随缓动默认改为轻微的 **0.02 秒**，小刻度间距保持 **24 px**。鼠标跟随与半高文字可通过开关恢复，已有冻结和物体绑定继续保留。

**1.4.0** 新增持续绑定物体的参照与批量显隐列表，实时跟随和 Freeze 继续独立运行，参考人物改为中性灰立体着色。新用法见[物体绑定说明](docs/OBJECT_ATTACHMENTS.md)。

Height Axis 是 Blender 的视口高度尺与参考人物工具。参照始终位于选中物体或鼠标点的**当前视口左侧**，也可以冻结在需要保留的三维位置。

**1.3.0** 新增白色半透明尺子、可调小刻度间距、仅向左延伸的横线、外观设置、世界空间平滑跟随及随缩放变化的显示细节。单位与远近过渡保留清晰的单套读数，侧栏按用途分组。

### 三种放置状态

| 状态 | 尺子与人物的行为 |
| --- | --- |
| **选中物体** | 测量可见选中几何体的世界 Z 高度；旋转视口时仍位于其屏幕左侧。多选计算整体高度。 |
| **鼠标跟随** | 取消**仅选中时显示**后，未选中物体时在鼠标左侧跟随。默认参考高度为 **1.8 米**，不显示物体名或模型文件名。 |
| **冻结** | 将当时显示的尺子和人物固定在**世界三维位置**。移动鼠标、改变选择及旋转视口都不会重新放置它们；取消勾选 Freeze 后恢复跟随。 |

参考人物始终使用设置的真实身高，例如用 1.8 米人物对比 3.2 米物体，不会自动拉伸成目标物体的高度。

在**物体绑定参照 → 绑定到物体**保留活动物体旁的参照后，可继续选择其他物体使用独立的实时参照。列表随场景保存，支持批量显隐及移除；不会删除目标物体。

### 安装与使用

1. 从 [1.5.0 发布页](https://github.com/taoluo20/blender-height-axis/releases/tag/v1.5.0)下载 `height-axis-1.5.0.zip`。
2. 在 Blender 打开 **Edit → Preferences → Get Extensions → 右上角菜单 → Install from Disk**，选择 ZIP 并启用 Height Axis。
3. 3D 视口按 **N**，打开 **Scale** 页签，勾选 **Show Height Axis / 显示高度轴**并选择几何物体。

点击 **Load Reference Figure / 加载参考人物**，选择 Blend、FBX、OBJ、glTF/GLB 或 STL 文件。可调整参考身高、人物朝向和不透明度；人物有独立显示开关。

勾选 **Freeze / 停止跟随** 即固定位置。未选中时，将鼠标移入侧栏点击也能保留该视口最后显示的参照位置。冻结位置和参考数据随 `.blend` 保存。

主面板保留显示、冻结、参考身高和单位；**Reference Figure / 参考人物**收纳模型加载及人物设置。展开 **Placement & Follow / 放置与跟随**可调实际宽度偏移、鼠标间距、跟随缓动和连接线。展开 **Ruler Appearance / 尺子外观**可调字号、线粗细、小刻度间距、整体不透明度、线与文字各自的颜色及透明度。**小刻度间距 (px)** 默认 24，数值越大越稀疏、越小越密；冻结后仍可调节，并随场景保存。**选择字体文件**支持本地 TTF、OTF、TTC，重置图标恢复默认字体。字体文件保留在外部；保存的路径不可用时回退到 Blender 默认字体，并在侧栏提示。

界面以英文为源语言，包含随 Blender 语言设置使用的简体中文翻译。默认关闭显示、冻结、人物和半高文字，开启**仅选中时显示**；此开关只过滤实时参照，不会移除显式冻结或已保存的物体绑定。跟随缓动默认 0.02 秒。关闭视口 Overlays 时全部参照隐藏。

### 功能与边界

支持变换和网格修改器后的实时高度、多选整体高度、编辑网格、自动刻度、场景单位及 m / cm / mm / ft / in。参考人物采用中性灰立体参照显示，可替换、独立开关并随文件保存，不注册额外快捷键，不依赖网络服务。

尺子和文字默认为白色半透明，默认只显示左侧全高数值；**尺子外观 → 显示半高数值**可恢复中位文字，不改变中点横条或小刻度密度。全部横向刻度只从竖线向屏幕左侧延伸，比主线更细。线宽、小刻度疏密、半高开关、线色、字色、透明度、字号和字体在冻结状态下仍可调整。

跟随在世界空间平滑变化，宽度偏移默认位于选中范围的水平包围之外，负值可向内靠近；连接线默认关闭。缩放时逐层显示十进制刻度，最细到 1 mm，自动单位在 m / cm / mm 之间变化。远景及俯视收为一个高度数值和较小的物体名称；过渡期间每套读数只绘制一次。

清单声明 Blender 4.5+；1.5.0 在 **Blender 5.2.2 LTS 通过 297 项检查**，包含实际字体加载与旧绑定/冻结兼容。最终 ZIP 已验证隔离安装、新默认值及绑定操作；8 种原生透视状态生成了 10 张更新后的公开截图，包含中英文控件。较早的基础检查覆盖 5.1.2；本次没有在 4.5 或 5.1 重跑。详见[验证记录](docs/VALIDATION.md)。

- 高度按世界 Z 轴测量。编辑模式读取修改器之前的当前编辑网格。
- 未实体化实例不计入选中高度，需要时先 Realize Instances 或转换为实际几何体。
- 鼠标参照使用穿过 3D Cursor 的视图深度平面，不自动贴合鼠标下方表面。
- 俯视或仰视时，Z 轴投影接近重合，显示高度数值及物体名称，数值仍为实际高度。
- 人物不使用原贴图、不播放动画；隐藏或不可渲染的网格及骨骼控制形状会排除。大型模型会简化为约 15 万三角面的显示参照。
- 加载需要对象模式。成功加载新模型会恢复跟随；移除人物时，冻结的尺子仍保留原位置。
- 视口边缘可能裁切参照；冻结后的参照会随相机移动自然改变屏幕投影。

更多内容：[视觉指南](docs/VISUAL_GUIDE.md)、[视觉审查](docs/VISUAL_REVIEW.md)、[功能与逻辑](docs/FEATURES_AND_LOGIC.md)、[构建与测试](docs/DEVELOPMENT.md)、[更新记录](CHANGELOG.md)。插件代码许可证为 GPL-3.0-or-later。项目示意图使用 Epic UE 5.8.2 的灰色 Manny，详见[来源与许可](docs/UE_MANNEQUIN.md)及[第三方说明](THIRD_PARTY_NOTICES.md)。示例模型不随插件提供，请加载自己的参考模型。自动检查仍用本项目自制人物，没有打包第三方人物网格。

项目结构：`height_axis/` 为扩展源码，`docs/` 为公开指南与预览，`tests/` 为可移植检查，`tools/` 为构建脚本。生成的安装包通过 Releases 分发。
