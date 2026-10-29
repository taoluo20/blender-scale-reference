# Scale Reference project preferences

- Default previews, screenshots, visual reviews and saved handoff views use a **non-isometric perspective** view.
- In Blender, set `RegionView3D.view_perspective = 'PERSP'`. Prefer an eye-level view with a modest horizontal turn so depth remains visible. The approved example uses about 12 degrees of horizontal turn; this is a reference, not a fixed angle requirement.
- Orthographic or isometric views may be used for additional diagnostics or when explicitly requested; they are not the default presentation.
- Apply this preference to preview/capture scripts as well as interactive viewport setup. Preserve the user's explicit instructions when they request a different view.

- Public visual guides use wide landscape viewport screenshots, with an aspect ratio of at least 16:9. Frame the actual controls and guide clearly.
- Keep image embeds and screenshot assets only on the latest GitHub release page. Remove image embeds and image attachments from older release pages after a new release is published; preserve historical Git tags, source snapshots and installer downloads.

## 简体中文

- 项目预览、截图、视觉审查及保存交付的视角，默认使用**非等距透视**。
- Blender 使用 `RegionView3D.view_perspective = 'PERSP'`，优先平视并适度水平侧转，让厚度可见。用户认可的示例约水平侧转 12 度；这只是参考，不要求固定角度。
- 正交或等距视角可用于附加诊断或用户明确要求的情况，不作为默认展示。
- 此偏好同时适用于预览截图脚本和交互视口设置；用户明确指定其他视角时，以当次要求为准。
- 公开视觉说明采用宽幅横向视口截图，宽高比至少 16:9，清楚展示实际控件与参照。
- GitHub 仅在最新版发布页保留图片及图片附件；新版本发布后，撤除旧发布页的图片嵌入和图片附件，保留历史 Git 标签、源码快照及安装包下载。
