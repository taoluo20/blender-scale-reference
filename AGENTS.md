# Scale Reference project preferences

- Default previews, screenshots, visual reviews and saved handoff views use a **non-isometric perspective** view.
- In Blender, set `RegionView3D.view_perspective = 'PERSP'`. Prefer an eye-level view with a modest horizontal turn so depth remains visible. The approved example uses about 12 degrees of horizontal turn; this is a reference, not a fixed angle requirement.
- Orthographic or isometric views may be used for additional diagnostics or when explicitly requested; they are not the default presentation.
- Apply this preference to preview/capture scripts as well as interactive viewport setup. Preserve the user's explicit instructions when they request a different view.

## 简体中文

- 项目预览、截图、视觉审查及保存交付的视角，默认使用**非等距透视**。
- Blender 使用 `RegionView3D.view_perspective = 'PERSP'`，优先平视并适度水平侧转，让厚度可见。用户认可的示例约水平侧转 12 度；这只是参考，不要求固定角度。
- 正交或等距视角可用于附加诊断或用户明确要求的情况，不作为默认展示。
- 此偏好同时适用于预览截图脚本和交互视口设置；用户明确指定其他视角时，以当次要求为准。
