# Validation Record

**English** · [简体中文](#简体中文)

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

### 1.2.1 版本

Blender 5.1.2 和 5.2.2 LTS 分别通过 **99 项检查**：高度、单位与启停 22 项；六种模型格式、原场景保留、带姿态蒙皮、替换及保存 61 项；冻结几何、视角投影和保存重开 16 项。

测试使用临时 Blender 用户配置，人物和格式样例由脚本生成，不依赖个人项目或第三方人物模型。

### 实际视口与打包

在 Blender 5.2.2 的真实视口验证了选中、鼠标跟随、旋转时保持左侧、偏移值、人物独立显示、两种冻结模式、侧栏捕获最后位置、正交/透视切换和解除冻结。冻结后的世界几何和人物矩阵保持不变，未报告绘制错误。

公开预览直接从发布版界面所在的实际视口导出，并在该过程中检查英文界面及简体中文翻译。

安装包通过 Blender 扩展清单校验，包内源码与发布目录一致，同一工具链中的重复构建具有相同哈希。GitHub Actions 只运行无需 Blender 的语法、清单、刻度和可重复打包检查；后台 Blender 检查在本地单独执行。

扩展清单最低版本为 Blender 4.5，**本次没有在 4.5 上运行验证**。未列出的版本、格式变体及特殊大型场景仍需按具体情况测试。
