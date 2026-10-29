# Visual Guide

**English** · [简体中文](#简体中文)

## Selection: measure and compare

![Selection mode in Blender](images/selected.png)

The cyan ruler shows the selection's world-Z height. The blue figure keeps its own reference height. Both are placed on the viewport-left side of the target, and that side is recalculated when the view rotates.

## Mouse: move the reference

![Mouse-following reference in Blender](images/mouse.png)

With nothing selected, the amber ruler and blue figure follow the mouse on the left. This is useful for quick scale comparisons without adding a scene object.

## Freeze: keep a location

![Frozen world-space reference in Blender](images/frozen.png)

**Freeze** pins both guides in world space. The `FREEZE` caption, checked control and locked geometry settings indicate the state. Viewport orbit changes how that fixed location appears on screen.

## Controls

| Control | Purpose |
| --- | --- |
| Show Height Axis | Ruler visibility |
| Freeze | Capture or release world-space placement |
| Reference Height (m) | Physical height of the mouse ruler and reference figure |
| Left Offset (px) | Gap to the pointer or selection while following |
| Display Units / Font Size | Measurement formatting and label size |
| Load Reference Figure | Choose a supported model file |
| Show Reference Figure | Figure visibility, independently from the ruler |
| Figure Rotation / Opacity | Reference pose direction and visual strength |
| Remove Reference Figure | Clear the loaded reference |

The screenshots are exported from a real Blender viewport. The study object and mannequin are generated locally by this project. No illustration is presented as an application screenshot.

---

## 简体中文

### 选中、跟随与冻结

第一张图为选中物体：青色尺子显示世界 Z 高度，蓝色人物保持独立的参考身高。它们位于当前视口中目标的左侧，旋转视角时重新计算左侧位置。

第二张图为鼠标跟随：未选中物体时，琥珀色尺子和蓝色人物在鼠标左侧移动，用于快速比较尺度，不需要添加场景对象。

第三张图为冻结：Freeze 勾选后，两种参照固定在世界三维位置。`FREEZE` 标记、复选框和锁定的几何参数显示当前状态；旋转视角只改变固定位置的投影。

### 控件

![简体中文界面](images/chinese-ui.png)

| 控件 | 用途 |
| --- | --- |
| Show Height Axis / 显示高度轴 | 控制尺子显示 |
| Freeze / 停止跟随 | 捕获或解除三维固定位置 |
| Reference Height (m) / 参考高度 | 鼠标参考尺与人物的真实身高，单位为米 |
| Left Offset (px) / 向左偏移 | 跟随时与鼠标或选中目标的间隔 |
| Display Units / Font Size | 数值单位与标签字号 |
| Load Reference Figure / 加载参考人物 | 选择支持的模型文件 |
| Show Reference Figure / 显示参考人物 | 独立控制人物显示 |
| Figure Rotation / Opacity | 人物朝向与不透明度 |
| Remove Reference Figure / 移除参考人物 | 清除已加载的参照 |

所有截图都从真实 Blender 视口导出。示例物体和人物由本项目在本地生成，没有将绘制的示意图当作软件截图。
