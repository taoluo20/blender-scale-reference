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
python tests/run_checks.py --blender "/path/to/blender" --font "/path/to/font.ttf"
```

The first command checks Python syntax, manifest metadata, ruler arithmetic and reproducible packaging. It is also the GitHub Actions job; it does not claim to exercise Blender's viewport.

The integration runner uses six independent Blender processes with temporary user directories: geometry/units/lifecycle, reference-format round trips, Freeze geometry/persistence, appearance/labels/fonts/persistence, motion/detail transitions, and object attachments. Passing `--font` also verifies actual font loading, caching and failure recovery. It generates its own mannequin assets. Local reports and blend files go to ignored folders. The summary contains only reports from that invocation.

For visual changes, also inspect selection, mouse and Freeze in a real 3D viewport. Default presentation and saved handoff views use non-isometric perspective (`PERSP`), preferably eye-level with a modest horizontal turn. `tools/capture_preview.py` uses that default. Orthographic and top views are additional diagnostics. Check orbit, sidebar capture of the last mouse position, editable frozen tick spacing, Overlay visibility, reference-only display and cleanup after disable. The published validation record distinguishes these manual/native UI checks from headless and packaging checks.

## Release

`tools/capture_preview.py` optionally reads `HEIGHT_AXIS_REFERENCE_MODEL` for an independently available local model. It defaults to the generated test fixture; no personal Unreal installation or proprietary model is required by the build or tests. Current UE mannequin preview provenance is documented [separately](UE_MANNEQUIN.md).

Update the extension version, changelog and release notes; build and validate the installer, then attach the versioned ZIP and `SHA256SUMS.txt` to the matching GitHub Release. Keep generated packages out of the source tree. Use English first, then Simplified Chinese, in public release notes.

---

## 简体中文

### 目录与构建

`height_axis/` 是扩展源码，`docs/` 是英文在前的双语说明与真实视口预览，`tests/` 生成自己的测试资产，`tools/` 提供构建和检查脚本。生成的 `dist/` 安装包与 `verification/` 本地报告不提交到 Git。

独立构建工具需要 Python 3.11+。运行上方构建命令即可得到版本化 ZIP 和 SHA256 记录。ZIP 根目录包含扩展清单，固定时间戳和排序使同一 Python/zlib 环境下的重复构建保持一致。传入 `--blender` 时，在临时用户配置中调用 Blender 校验。

### 测试与发布

`tools/capture_preview.py` 可通过可选环境变量 `HEIGHT_AXIS_REFERENCE_MODEL` 读取本地独立取得的模型，默认仍使用生成的测试夹具；构建和测试不依赖个人 Unreal 安装或专有模型。当前 UE 人偶预览的[来源记录](UE_MANNEQUIN.md)单独说明。

`tools/quick_check.py` 检查语法、清单、刻度计算和可重复打包，也是 GitHub Actions 执行的检查；它不声称验证 Blender 的实际视口。

`tests/run_checks.py --blender ...` 使用临时用户目录运行六个 Blender 进程，分别验证高度与单位及启停、模型格式往返导入、冻结几何及保存重开、外观与字体设置保存、运动和细节过渡，以及物体绑定参照。传入 `--font` 可验证实际字体加载、缓存与失败恢复。示例人物由测试生成，本地报告和测试 blend 文件放在忽略目录；摘要只列出本次运行的结果。

视觉改动还需在真实视口检查选中、鼠标跟随和冻结。默认展示及保存交付视角使用非等距透视（`PERSP`），优先平视并适度水平侧转；`tools/capture_preview.py` 也采用此默认值。正交及俯视仅作附加诊断。检查旋转、侧栏冻结、冻结后调节小刻度间距、Overlays、人物独立显示及禁用后的清理。公开验证记录区分实际 UI、后台和打包检查。

发布时更新版本、更新记录和说明，构建并校验安装包，将版本化 ZIP 与 `SHA256SUMS.txt` 附到对应 GitHub Release。对外发布说明先英文、后简体中文。
