# Validation Record

**English** · [简体中文](#简体中文)

## 1.4.0 object attachments — 2026-10-29

The subsequent gray-preview step retained all **259 checks**. Epic's actual UE 5.8.2 `SKM_Manny_Simple` was exported locally, imported as 92,178 triangles, and used for nine native perspective captures including A attached with B live and two attachments with live C. Every captured view reported `PERSP` and no draw errors. All documented preview PNGs were refreshed. UE source and derived model data remain ignored and excluded from the ZIP; automated fixtures remain self-authored. See [preview provenance](UE_MANNEQUIN.md).

The final Blender 5.2.2 LTS run passed **267 checks**: the complete 200-check baseline, 59 attachment checks and 8 drawing-error checks. The final review reproduced repeated console logging on consecutive failed frames and corrected both model and layout error reporting. Regression checks exercise continuous failure, recovery, failure recurrence and continued drawing of healthy references. Attachment checks cover separate live and retained guides, multiple targets, ruler-only/figure-only/both, target transforms and evaluated modifiers, view-left placement, captured meshes/styles, batch visibility, scene isolation, save/reopen, disable/reenable, target rename/delete/unlink, safe record deletion and Overlays. Native perspective captures cover A attached with B live, two persistent attachments, batch hiding, target scaling/orbit, separate display modes, live-figure removal and Chinese UI. Native Blender Undo with explicit MCP checkpoints restored both deleted records and an orphan reference mesh; target objects remained intact. All views use non-isometric perspective. These checks cover the final 1.4.0 source and installer.

## Tick spacing and left marks — 2026-10-29

Blender 5.2.2 LTS passed **200 checks**: geometry/lifecycle 22, reference imports 61, Freeze 16, appearance/fonts 27 and motion/transitions/localization 74. New cases cover adjustable physical tick layers, continuous opacity, scene persistence while frozen, unchanged Freeze geometry and horizontal left-only marks under reversed projections. Native eye-level perspective captures compare 6 px dense and 24 px default spacing, frozen 6/48 px spacing, zoomed frozen detail and the Chinese control. All captured states reported no draw errors. Preview defaults and the saved review blend use non-isometric perspective. The rebuilt ZIP passed manifest validation, source-byte comparisons and reproducibility checks; installation and enabling succeeded in a temporary Blender configuration. These checks cover the final 1.3.0 package.

## Visual review — 2026-10-29

The final Blender 5.2.2 LTS run passed **188 checks**: geometry/lifecycle 22, reference imports 61, Freeze 16, appearance/fonts 26 and motion/transitions/localization 63. Five new checks cover duplicate-free detail and unit transitions, continuous readout placement, offscreen labels and the translated placement heading. Native viewport captures cover 11 states listed in the [visual review](VISUAL_REVIEW.md). Packaging checks were rerun after the visual changes. This review did not rerun Blender 4.5 or 5.1.

## Local 1.3.0 Checks

Blender 5.1.2 and 5.2.2 LTS each passed **125 checks**: the 99 existing checks below plus 26 appearance checks. New cases cover translucent defaults, sparse left-side labels, unit changes, crowded/offscreen labels, old/new Freeze midpoint data, appearance persistence, actual TTF loading and reuse, failed font selection, default reset and missing-file fallback. Each run used isolated user directories. The ZIP was installed and enabled in an isolated Blender 5.2.2 configuration. Native viewport exports exercised selection, mouse, Freeze, custom colors and an actual font without draw errors. These earlier appearance checks predate the final tick-spacing follow-up.

## Release 1.2.1

| Check group | Blender 5.1.2 | Blender 5.2.2 LTS |
| --- | ---: | ---: |
| Geometry, units and extension lifecycle | 22 passed | 22 passed |
| Six model formats, scene preservation, posed skin, replacement and persistence | 61 passed | 61 passed |
| Freeze geometry, view projection and saved-file persistence | 16 passed | 16 passed |
| **Total per version** | **99 passed** | **99 passed** |

The checks run in temporary Blender user configurations. They generate their own mannequin and format fixtures. No personal project or third-party character model is required.

## Actual viewport checks

Native Blender 5.2.2 viewport checks covered selection and mouse placement, orbit while following, exact left offset, independent figure visibility, Freeze in both placement modes, sidebar capture of the last mouse position, orthographic/perspective switching, and unfreezing. The ruler and figure retained identical stored world geometry during frozen camera and selection changes, with no reported draw errors.

Publication previews are exported from a real viewport using the release UI. English labels and Simplified Chinese translation are checked in that process. They are screenshots of the extension drawing, not rendered marketing substitutes.

## Packages and automation

- The extension ZIP passes Blender's extension manifest validation.
- Source entries inside the ZIP are compared with the staged source.
- Repeated builds in the same toolchain produce the same ZIP hash.
- GitHub Actions runs syntax, metadata, ruler arithmetic and reproducible-package checks without Blender. Headless Blender integration checks are run locally and are listed separately above.
- The manifest minimum is Blender 4.5; **4.5 has not been exercised in this validation run**.

This record describes the exercised cases. Unlisted Blender versions, import variants and unusually large or specialized scenes still need their own validation.

---

## 简体中文

### 1.4.0 物体绑定 — 2026-10-29

后续灰色预览步骤继续保持 **259 项检查通过**。本地导出 Epic UE 5.8.2 的真实 `SKM_Manny_Simple`，导入后为 92,178 个三角面，拍摄了 9 张原生透视截图，包含 A 绑定且 B 实时，以及两个绑定加 C 实时。每张均为 `PERSP`，无绘制异常；文档预览 PNG 已全部更新。UE 原始及衍生模型数据保持忽略并排除在 ZIP 外，自动夹具仍为自制。详见[预览来源](UE_MANNEQUIN.md)。

最终 Blender 5.2.2 LTS 检查通过 **267 项**：完整保留原有 200 项，新增 59 项绑定检查及 8 项绘制异常检查。最终审查复现了连续失败帧重复打印的问题，并修复人物绘制及布局异常的日志处理；回归检查覆盖持续失败、恢复、再次失败及其他参照继续绘制。绑定检查覆盖实时参照与绑定共存、多目标、仅尺/仅人物/二者、目标变换及修改器、视口左侧、网格与外观快照、批量显隐、场景隔离、保存重开、禁用再启用、目标改名/删除/移出场景、记录安全删除及 Overlays。原生透视截图覆盖 A 绑定且 B 实时、两个持续绑定、批量隐藏、目标缩放与旋转视口、独立显示模式、移除实时人物及中文界面。使用明确 MCP 检查点的 Blender 原生撤销恢复了被删除记录及无主人物网格，目标物体保持完整。所有视角均为非等距透视。这些检查覆盖最终 1.4.0 源码及安装包。

### 小刻度间距与左侧横线 — 2026-10-29

Blender 5.2.2 LTS 通过 **200 项检查**：几何及启停 22、参考导入 61、冻结 16、外观及字体 27、运动及过渡和翻译 74。新增覆盖可调物理刻度层级、连续透明度、冻结时保存重开、冻结几何保持不变，以及投影反向后横线仍水平朝左。真实平视透视截图比较了 6 px 密集与 24 px 默认、冻结时 6/48 px、冻结后缩放和中文控件；所有截图状态均未报告绘制异常。预览默认值和已保存审查场景采用非等距透视。重建 ZIP 通过清单、源码字节一致性及可重复构建检查，并在临时 Blender 配置中成功安装启用。这些检查覆盖最终 1.3.0 安装包。

### 视觉审查 — 2026-10-29

最终 Blender 5.2.2 LTS 检查通过 **188 项**：几何及启停 22、参考导入 61、冻结 16、外观及字体 26、运动及过渡和翻译 63。新增 5 项覆盖过渡读数无重复、连续位置、屏幕外标签及分组中文标题。原生视口截图覆盖[视觉审查记录](VISUAL_REVIEW.md)中的 11 种状态；视觉修改后重新进行了打包检查。本轮没有重新运行 Blender 4.5 或 5.1。

### 本地 1.3.0 检查

Blender 5.1.2 与 5.2.2 LTS 各通过 **125 项检查**：下方原有 99 项加上 26 项外观检查，覆盖半透明默认值、左侧精简标签、单位切换、拥挤与屏幕外标签、新旧冻结中点数据、外观保存、真实 TTF 加载及缓存、字体选择失败、恢复默认与文件缺失回退。每次使用隔离用户目录。安装包已在独立 Blender 5.2.2 配置中安装并启用；原生视口导出覆盖选中、鼠标、冻结、自定义颜色及实际字体，未出现绘制错误。这些较早的外观检查早于最终小刻度间距更新。

### 1.2.1 版本

Blender 5.1.2 和 5.2.2 LTS 分别通过 **99 项检查**：高度、单位与启停 22 项；六种模型格式、原场景保留、带姿态蒙皮、替换及保存 61 项；冻结几何、视角投影和保存重开 16 项。

测试使用临时 Blender 用户配置，人物和格式样例由脚本生成，不依赖个人项目或第三方人物模型。

### 实际视口与打包

在 Blender 5.2.2 的真实视口验证了选中、鼠标跟随、旋转时保持左侧、偏移值、人物独立显示、两种冻结模式、侧栏捕获最后位置、正交/透视切换和解除冻结。冻结后的世界几何和人物矩阵保持不变，未报告绘制错误。

公开预览直接从发布版界面所在的实际视口导出，并在该过程中检查英文界面及简体中文翻译。

安装包通过 Blender 扩展清单校验，包内源码与发布目录一致，同一工具链中的重复构建具有相同哈希。GitHub Actions 只运行无需 Blender 的语法、清单、刻度和可重复打包检查；后台 Blender 检查在本地单独执行。

扩展清单最低版本为 Blender 4.5，**本次没有在 4.5 上运行验证**。未列出的版本、格式变体及特殊大型场景仍需按具体情况测试。
