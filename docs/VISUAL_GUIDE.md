# Visual Guide

**English** · [简体中文](#简体中文)

## Selection: measure and compare

![Selection mode in Blender](images/selected.png)

The translucent white ruler shows the selection's world-Z height with the full-height value on its left and a smaller object name below. **Only With Selection** starts on, while **Show Half-Height Value** and the reference figure start off. The optional gray figure keeps its own reference height. Guides follow the viewport-left side with subtle 0.02 s easing. Zooming out retains a single height readout and object name; zooming in reveals decimal ticks down to 1 mm. Automatic unit handoffs show one reading at a time.

## No selection: hidden by default

With **Only With Selection** enabled, deselecting geometry hides the live ruler. Stored attachments and explicitly frozen guides remain independent.

![Deselected geometry with the live ruler hidden](images/selection-only.png)

## Mouse: move the reference

![Mouse-following reference in Blender](images/mouse.png)

Uncheck **Only With Selection** to restore the mouse ruler when nothing is selected. It follows on the left without an object/model caption. An independently loaded figure is optional. Leaving the checkbox enabled hides live guides after deselection.

## Freeze: keep a location

![Frozen world-space reference in Blender](images/frozen.png)

**Freeze** pins both guides in world space. The checked control and locked geometry settings indicate the state. Viewport orbit changes how that fixed location appears on screen. There is no bottom caption on the ruler.

## Controls

Visibility, **Only With Selection**, Freeze, reference height and units stay in the main panel. Model loading and figure settings are grouped under **Reference Figure**. **Placement & Follow** and **Ruler Appearance** collapse independently.

![Expanded placement and appearance controls](images/controls.png)

| Control | Purpose |
| --- | --- |
| Show Scale Reference | Ruler visibility |
| Only With Selection | Hide the live guide without selected geometry; keep frozen and attached references |
| Freeze | Capture or release world-space placement |
| Reference Height (m) | Physical height of the mouse ruler and reference figure |
| Width Offset (m) / Mouse Gap (px) | Physical selection offset / screen-space mouse gap |
| Follow Smoothing (s) / Show Connection Lines | Following response and optional connectors |
| Units / Font Size | Measurement formatting and label size |
| Line Width (px) | Main line width; crossbars stay thinner |
| Tick Spacing (px) | Minimum screen spacing before minor ticks fade in; larger values are sparser, default 24 |
| Show Half-Height Value | Optional midpoint text, default off; keeps every crossbar and minor tick |
| Ruler Opacity | Overall ruler and text opacity |
| Line Color / Text Color | Independent RGBA colors, including opacity |
| Choose Font File / reset icon | Use a local TTF, OTF or TTC font, or restore Blender's default |
| Load Reference Figure | Choose a supported model file |
| Show Reference Figure | Figure visibility, independently from the ruler |
| Figure Rotation / Opacity | Reference pose direction and visual strength |
| Remove Reference Figure | Clear the loaded reference |

Minor tick spacing changes the visibility of exact physical decimal levels rather than stretching their distances. It saves with the scene and stays editable while frozen. All crossbars, including both endpoints and half-height, extend horizontally only to screen-left from the axis.

![Sparse default ticks and the spacing control in an eye-level perspective viewport](images/tick-spacing.png)

Enable **Show Half-Height Value** to add the midpoint number. The example keeps the same object, placement and 24 px tick spacing as the default selected preview.

![Optional half-height value enabled without changing tick spacing](images/half-height.png)

The screenshots are exported from a real Blender viewport. New previews default to non-isometric perspective, preferably eye-level with a modest horizontal turn. The study objects are generated locally; current mannequin previews use Epic's UE 5.8.2 Manny. See [source and license](UE_MANNEQUIN.md). No illustration is presented as an application screenshot.

![Custom ruler colors and local font](images/appearance.png)

---

## 简体中文

### 选中、跟随与冻结

第一张图为选中物体：白色半透明尺子显示左侧全高及下方较小的物体名称。默认开启**仅选中时显示**，关闭**显示半高数值**和参考人物；可选的中性灰人物使用独立物理身高。参照以 0.02 秒轻微缓动跟随目标左侧；拉远保留一个高度及名称，拉近渐显最细到 1 mm 的刻度，自动单位切换只显示一套读数。

取消选择时，默认的**仅选中时显示**隐藏实时尺子；已有物体绑定和显式冻结参照继续保留。

![取消选择后隐藏实时尺子](images/selection-only.png)

第二张图为可选鼠标跟随：取消**仅选中时显示**后，未选中时在鼠标左侧显示尺子，尺寸下方没有物体或模型名。人物需独立加载启用；保持该开关开启时，取消选择即隐藏实时参照。

第三张图为冻结：Freeze 勾选后，两种参照固定在世界三维位置。复选框和锁定的几何参数显示当前状态；旋转视角只改变固定位置的投影，尺子底部不再显示说明文字。

### 控件

主面板保留显示、**仅选中时显示**、冻结、参考身高和单位。模型加载与人物参数归入“参考人物”；“放置与跟随”和“尺子外观”可独立折叠。

![简体中文界面](images/chinese-ui.png)

| 控件 | 用途 |
| --- | --- |
| Show Scale Reference / 显示尺度参考 | 控制尺子显示 |
| Only With Selection / 仅选中时显示 | 未选中几何体时隐藏实时参照，保留冻结和绑定 |
| Freeze / 停止跟随 | 捕获或解除三维固定位置 |
| Reference Height (m) / 参考高度 | 鼠标参考尺与人物的真实身高，单位为米 |
| Width Offset (m) / Mouse Gap (px) | 选中范围的实际偏移 / 鼠标屏幕间距 |
| Follow Smoothing (s) / Show Connection Lines | 跟随缓动与可选连接线 |
| Units / Font Size | 数值单位与标签字号 |
| Line Width (px) / 线粗细 | 主线宽度，横向刻度保持更细 |
| Tick Spacing (px) / 小刻度间距 | 小刻度开始渐显的最小屏幕间距；数值越大越稀疏，默认 24 |
| Show Half-Height Value / 显示半高数值 | 默认关闭的中点文字，不改变横条与小刻度 |
| Ruler Opacity / 尺子不透明度 | 尺子与文字的整体不透明度 |
| Line Color / Text Color | 线与文字独立的 RGBA 颜色，包含透明度 |
| Choose Font File / 重置图标 | 选择本地 TTF、OTF、TTC 字体，或恢复默认字体 |
| Load Reference Figure / 加载参考人物 | 选择支持的模型文件 |
| Show Reference Figure / 显示参考人物 | 独立控制人物显示 |
| Figure Rotation / Opacity | 人物朝向与不透明度 |
| Remove Reference Figure / 移除参考人物 | 清除已加载的参照 |

小刻度间距只改变准确十进制刻度层级的显隐，不拉伸实际物理距离。设置随场景保存，冻结后仍可调整。全部横线，包括上下端与半高，都只从竖线水平向屏幕左侧延伸。上方新预览展示默认稀疏刻度与调节控件。

开启**显示半高数值**即可增加中位文字，下图与默认选中预览使用同一物体、放置及 24 px 刻度间距。

![开启半高数值且保持原有横条间距](images/half-height.png)

所有截图都从真实 Blender 视口导出。新预览默认非等距透视，优先平视并适度水平侧转。示例物体在本地生成，当前人物为 Epic UE 5.8.2 Manny（[来源与许可](UE_MANNEQUIN.md)），没有将绘制的示意图当作软件截图。
