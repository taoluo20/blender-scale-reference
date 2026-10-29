# Features and Placement Logic

**English** · [简体中文](#简体中文)

## State model

```mermaid
stateDiagram-v2
    [*] --> Hidden
    Hidden --> Selection: Enable an unfrozen guide with geometry selected
    Hidden --> Mouse: Enable an unfrozen guide with no selection
    Hidden --> Frozen: Show a guide with a retained Freeze
    Selection --> Mouse: Deselect geometry
    Mouse --> Selection: Select geometry
    Selection --> Frozen: Check Freeze
    Mouse --> Frozen: Check Freeze
    Frozen --> Selection: Uncheck Freeze with a selection
    Frozen --> Mouse: Uncheck Freeze without a selection
    Selection --> Hidden: Disable both guides
    Mouse --> Hidden: Disable both guides
    Frozen --> Hidden: Disable both guides; keep placement
```

The display checkboxes and placement are independent. Hiding both guides can retain a frozen placement; showing a guide again restores that placement. A viewport with no previous visible guide cannot create a meaningful Freeze and displays a hint instead.

## Selection placement

1. Collect the visible selected geometric objects.
2. Measure their combined minimum and maximum **world Z** using evaluated vertices. In Edit Mode use the current editable mesh.
3. Use the horizontal bounds' half-diagonal as a stable envelope. Place a vertical world-space ruler and figure outside it along the viewport's horizontal left direction, with the configured physical width offset.
4. Ease position and orbit changes with frame-rate independent following. The configured figure height and ruler's world-Z span remain constant. A negative width offset moves inward and can reduce surface clearance during orbit.

Only supported geometry is measured; cameras, lights, Empty helpers and armatures themselves are excluded. The ruler starts at zero at the geometry's lowest point.

## Mouse placement

With no selection, the ruler and figure follow the mouse in the active 3D viewport. The whole figure stays left of the pointer with a configurable gap. Its height is specified in physical metres, converted through the scene's unit scale.

The anchor is calculated at the view depth of the 3D Cursor. Entering the sidebar or another editor hides the live mouse guide. The last displayed position is cached so clicking Freeze in the sidebar captures the intended location.

## Freeze

Freeze captures the displayed ruler endpoints and tick positions in world space, together with the figure's complete transform and height. It does not attach those positions to the selected object. Each viewport projects the same stored geometry through its own camera.

While frozen, geometry-changing controls are disabled. Units, font size, line width, line/text RGBA, font choice, figure opacity and visibility remain editable. The snapshot, display settings and baked reference mesh persist in the scene when the blend file is saved. Unfreezing clears the snapshot and resumes the current selection or mouse placement. A successful new model import also resumes following; an unsuccessful import preserves the existing reference.

Only the physical half-height and full-height values are labelled, to the screen-left of their projected marks. Perspective views project the actual world midpoint rather than averaging the screen endpoints. New Freeze snapshots store that midpoint; existing snapshots recover it from their world endpoints. Crowded labels reduce to the full height, and offscreen marks do not create labels at the viewport edge.

Zoom fades decimal tick layers down to 1 mm. Auto units use projected density to select m, cm or mm; during a handoff only the dominant unit is drawn, at its transition opacity. Far and top views retain one full-height readout and a smaller object name. The same readout moves between midpoint and endpoint during the detail transition, without drawing duplicate text. Frozen guides retain these zoom-dependent display changes.

**Tick Spacing (px)** controls the minimum screen separation at which a decimal layer starts fading in. The default is 24 UI-scaled pixels, compared with the previous fixed 6-pixel threshold. Larger values show fewer minor ticks; a layer reaches full opacity at four times its fade threshold. Tick positions remain exact physical multiples, down to 1 mm. Spacing saves with the scene and can change while frozen: display ticks are regenerated along the stored world segment without changing the snapshot or figure transform. Endpoint, half-height and minor marks all extend horizontally only screen-left from the axis.

Appearance settings save with each scene. Local TTF, OTF and TTC fonts are loaded once and reused; font handles are released on file load and extension disable. Font files are external dependencies, so missing paths fall back to Blender's default font and display a panel warning. A failed font choice keeps the previous choice.

## Reference loading

Local 1.4.0 also supports [object attachments](OBJECT_ATTACHMENTS.md). Each scene stores independent object pointers, display choices and appearance snapshots, with retained immutable reference mesh IDs. Entries reuse the live layout/drawing path with their own animation/density keys. Live Freeze and mouse tracking remain independent. Target geometry is evaluated again as it changes; hidden or missing targets are skipped. Removal acts on records and unowned normalized reference meshes, never on target objects.

Import occurs in a temporary scene. The evaluated visible surfaces are combined, optional axis correction is applied, large references are simplified, and the result is normalized to unit height. The normalized display mesh is retained as scene data; the temporary objects, rigs, materials and import data are removed. The original scene selection and active object are restored.

The viewport draws this reference with its own depth buffer and a neutral-gray shaded style. It has no selectable scene object and does not appear in a render. Native format importers are used for Blend, FBX, OBJ, glTF/GLB and STL.

## Interaction rules

- Native selection, navigation and transforms receive their normal events.
- No hotkeys are registered.
- Freeze stops mouse tracking while preserving display.
- Loading or removing a reference is undoable; cached drawing data is cleared after undo/redo.
- Disabling the extension removes its handlers, timer, draw callback, classes and GPU resources. Stored scene values can remain in a saved blend file for later use.

---

## 简体中文

### 状态与放置

参照有隐藏、选中物体跟随、鼠标跟随及冻结四种状态。上方状态图展示其切换关系。显示开关与放置方式独立：隐藏参照时可以保留冻结位置，重新显示后恢复原位置。视口里从未显示过参照时，无法凭空冻结，界面会提示先显示尺子或人物。

选中时，收集可见的选中几何体，计算评估顶点在世界 Z 轴上的整体范围。以水平包围范围的半对角线构成稳定边界，沿视口水平左侧方向将三维竖直尺子与人物放在边界之外，并加入实际宽度偏移。位置与旋转变化使用与帧率无关的平滑跟随；人物身高及尺子的世界 Z 高度保持实际尺寸。负宽度偏移向内靠近，旋转时可能减少与表面的间隔。编辑模式读取当前编辑网格。尺子最低点从 0 开始，不测量海拔；相机、灯光、Empty 和骨架本体不参与高度测量。

未选中时，以 3D Cursor 的视图深度为基础计算鼠标锚点，尺子和人物跟随当前 3D 视口内的鼠标，并保留左侧间隔。参考高度始终以米输入，再按场景单位缩放换算。鼠标进入侧栏或其他编辑器时，实时参照隐藏；会记住最后显示的位置，供侧栏 Freeze 捕获。

### 冻结

冻结保存尺子端点、刻度的世界坐标，以及人物完整变换与高度，不再绑定选中物体。每个视口通过自己的相机投影同一份固定几何位置。

冻结时锁定会改变参照几何形态的参数，仍可调整单位、字号、线宽、线与文字各自 RGBA、字体、人物不透明度和显示开关。快照、显示设置及参考网格随场景保存。解除冻结后清除快照并恢复当前的选择或鼠标跟随。成功加载新模型也会恢复跟随；加载失败保留旧参照。

数值只标注实际半高与全高，位于各自投影刻度的屏幕左侧。透视视图投影真实的三维中点，不直接平均屏幕端点。新冻结快照保存中点，旧快照从世界端点恢复。空间拥挤时仅显示全高，屏幕外的刻度不会把文字挤到视口边缘。

缩放时逐层渐变十进制刻度，最细到 1 mm。自动单位依据投影密度在 m、cm、mm 之间变化；交接时只绘制当前权重较高的一套文字，并保留过渡透明度。远景及俯视保留一个全高数值和较小物体名称；同一套读数在中点与顶点之间移动，避免过渡时重复绘制。冻结后仍保留这些随缩放变化的显示细节。

**小刻度间距 (px)** 控制十进制层级开始渐显时的最小屏幕距离，默认 24 个随界面缩放的像素，原先固定阈值为 6。数值越大，小刻度越稀疏；屏幕间距达到阈值四倍时完全显示。刻度位置仍是准确的物理倍数，最细到 1 mm。设置随场景保存，冻结时可调整：沿已保存的世界线段重新生成显示刻度，不修改冻结快照或人物变换。上下端、半高及小刻度都只从竖线水平向屏幕左侧延伸。

外观设置按场景保存。本地 TTF、OTF、TTC 字体加载后复用，读取文件和禁用扩展时释放字体资源。字体文件保留在外部，路径失效时回退到 Blender 默认字体并在侧栏提示；选择字体失败会保留原选择。

### 人物加载与交互

本地 1.4.0 还支持[物体绑定参照](OBJECT_ATTACHMENTS.md)。每个场景保存独立目标指针、显示选择与外观快照，通过 ID 引用保留不可变的人物网格。条目复用实时布局和绘制，拥有独立的缓动及投影密度缓存；实时 Freeze 与鼠标追踪保持独立。目标变化时重新评估几何，隐藏或缺失时跳过。删除只处理记录和不再被引用的归一化人物网格，绝不操作目标物体。

使用临时场景导入并评估可见表面，合并几何体，按需修正向上轴、简化大型模型，再归一化为单位高度。只保留显示用的参考网格数据，清理临时对象、骨架、材质等导入数据，并恢复原场景的选择和活动对象。

人物使用独立深度缓冲绘制中性灰立体参照，不产生可选中的场景物体，也不进入最终渲染。支持 Blend、FBX、OBJ、glTF/GLB、STL 原生导入器。

原生选择、导航及变换继续接收正常事件，不新增快捷键。冻结停止鼠标追踪但保留绘制。模型加载和移除支持撤销，撤销/重做后清理绘制缓存。禁用扩展时清理处理器、计时器、绘制回调、注册类和 GPU 资源；已保存场景中的参照数据可在以后继续使用。
