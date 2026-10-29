# Development

**English** · [简体中文](#简体中文)

## Layout

```text
height_axis/         Blender extension source and its manifest
docs/               English-first bilingual guides and real viewport previews
tests/              Blender integration checks; fixtures are generated locally
tools/build.py      Reproducible ZIP build, with optional Blender validation
tools/quick_check.py Checks that do not require Blender
dist/               Generated release artifacts; ignored by Git
verification/       Local reports, logs and test files; ignored by Git
```

## Build

Python 3.11 or newer is required for the standalone build tools.

```sh
python tools/build.py
python tools/build.py --blender "/path/to/blender"
```

The installer is `dist/height-axis-<version>.zip`, with `blender_manifest.toml` at the archive root. `dist/SHA256SUMS.txt` records the package hash. Fixed timestamps and sorted entries make repeated builds reproducible within the same Python/zlib toolchain. With `--blender`, Blender validates the result in a temporary user configuration.

## Checks

```sh
python tools/quick_check.py
python tests/run_checks.py --blender "/path/to/blender"
```

The first command checks Python syntax, manifest metadata, ruler arithmetic and reproducible packaging. It is also the GitHub Actions job; it does not claim to exercise Blender's viewport.

The second command runs three independent Blender processes with temporary user directories: geometry/units/lifecycle, reference-format round trips, and Freeze geometry/persistence. It generates its own mannequin assets. Local reports and blend files go to ignored folders.

For visual changes, also inspect selection, mouse and Freeze in a real 3D viewport. Check perspective/orthographic orbit, sidebar capture of the last mouse position, Overlay visibility, reference-only display and cleanup after disable. The published validation record distinguishes these manual/native UI checks from headless and packaging checks.

## Release

Update the extension version, changelog and release notes; build and validate the installer, then attach the versioned ZIP and `SHA256SUMS.txt` to the matching GitHub Release. Keep generated packages out of the source tree. Use English first, then Simplified Chinese, in public release notes.

---

## 简体中文

### 目录与构建

`height_axis/` 是扩展源码，`docs/` 是英文在前的双语说明与真实视口预览，`tests/` 生成自己的测试资产，`tools/` 提供构建和检查脚本。生成的 `dist/` 安装包与 `verification/` 本地报告不提交到 Git。

独立构建工具需要 Python 3.11+。运行上方构建命令即可得到版本化 ZIP 和 SHA256 记录。ZIP 根目录包含扩展清单，固定时间戳和排序使同一 Python/zlib 环境下的重复构建保持一致。传入 `--blender` 时，在临时用户配置中调用 Blender 校验。

### 测试与发布

`tools/quick_check.py` 检查语法、清单、刻度计算和可重复打包，也是 GitHub Actions 执行的检查；它不声称验证 Blender 的实际视口。

`tests/run_checks.py --blender ...` 使用临时用户目录运行三个 Blender 进程，分别验证高度与单位及启停、模型格式往返导入、冻结几何及保存重开。示例人物由测试生成，本地报告和测试 blend 文件放在忽略目录。

视觉改动还需在真实视口检查选中、鼠标跟随、冻结、透视/正交旋转、侧栏冻结、Overlays、人物独立显示及禁用后的清理。公开验证记录区分实际 UI、后台和打包检查。

发布时更新版本、更新记录和说明，构建并校验安装包，将版本化 ZIP 与 `SHA256SUMS.txt` 附到对应 GitHub Release。对外发布说明先英文、后简体中文。
