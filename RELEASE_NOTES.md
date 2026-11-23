# Scale Reference 1.7.0

**Show Ground Clearance** adds a readout in the **Scale** panel for the vertical gap from the measured geometry's lowest point to the ground reference.

- **World Z = 0** uses the scene origin as the ground level. **Relative to Object** uses the selected ground object's highest evaluated world Z, including transforms and modifiers.
- The value is negative below the reference and uses the ruler's display units. The readout is off by default.
- Frozen selections keep their captured lowest point. Each object attachment saves its ground setting and follows the assigned ground object's current height.

Download `scale-reference-1.7.0.zip` and use **Preferences → Get Extensions → Install from Disk** in Blender. This updates the existing Scale Reference extension.

Verified with 350 checks on Blender 5.2.2 LTS, plus isolated installation and reopening an older scene with two object attachments.

## 简体中文

**Scale** 面板新增**显示离地高度**，可读出测量几何体最低点与地面基准之间的垂直高度差。

- **世界 Z = 0** 以世界零高度为基准。**相对物体**以指定地面物体求值后的最高世界 Z 为基准，包含变换与修改器。
- 低于基准时显示负值，读数沿用尺子的显示单位。此功能默认关闭。
- 冻结选区保留捕获时的最低点。每条物体绑定单独保存地面设置，并随指定地面物体的当前高度更新。

下载 `scale-reference-1.7.0.zip`，在 Blender 的**偏好设置 → 获取扩展 → 从磁盘安装**中选择 ZIP，即可更新现有 Scale Reference 扩展。

已在 Blender 5.2.2 LTS 通过 350 项检查，并验证隔离安装及读取含两条物体绑定的旧场景。
