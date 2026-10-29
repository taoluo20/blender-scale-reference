# Gray UE Mannequin Preview

**English** · [简体中文](#简体中文)

Optional figure screenshots use Epic's actual **Manny** mannequin, `SKM_Manny_Simple`, from the installed **Unreal Engine 5.8.2** template Characters content. The 1.5.0 default preview contains no figure. It is not an approximation or an AI-generated character. Epic identifies Manny and Quinn in the [Third Person template documentation](https://dev.epicgames.com/documentation/unreal-engine/third-person-template-in-unreal-engine?lang=en-US).

The mesh is exported with Unreal's FBX exporter into an isolated local project, then saved as a gray Blender reference. The local material uses equal RGB channels, roughness 0.72 and zero metallic. Height Axis also uses neutral-gray vertex shading with its own depth buffer; changing only the imported material would not affect that overlay. Physical height, normalization, alpha, reference visibility, object attachments and live following remain active.

## Assets and license

The template asset is governed by the [Unreal Engine EULA](https://www.unrealengine.com/eula/unreal). Its verified Templates origin and sections 1, 2, 4(a)(i), 5(b), 6(c) and 7(a) support our use of these raster documentation images. This is a source-specific license assessment. No Epic asset is offered under GPL. Source assets and derived geometry remain local and excluded from Git and the extension ZIP. See [third-party notices](../THIRD_PARTY_NOTICES.md).

The ignored `verification/ue-gray-mannequin/` folder contains the source provenance, local export project, FBX, gray Blend and review evidence. Automated tests retain this project's self-authored fixture. No proprietary mannequin is needed to build or test the add-on. Set `HEIGHT_AXIS_REFERENCE_MODEL` to an independently available local model when running the preview script; its portable default remains the generated fixture.

Epic Games owns the Unreal Engine trademarks and the Manny asset. © 1998–2026 Epic Games, Inc. All rights reserved. The mannequin is shown for scale-reference demonstration; this add-on is not endorsed by Epic.

---

## 简体中文

可选人物示意图使用 Epic 官方的真实 **Manny** 人偶，来源为已安装 **Unreal Engine 5.8.2** 模板 Characters 内容中的 `SKM_Manny_Simple`，不是近似人物或 AI 生成角色。1.5.0 默认预览不显示人物。Epic 的[第三人称模板说明](https://dev.epicgames.com/documentation/unreal-engine/third-person-template-in-unreal-engine?lang=en-US)介绍了 Manny 与 Quinn。

使用独立本地项目通过 Unreal FBX 导出，再保存为灰色 Blender 参照。本地材质采用 RGB 等值、粗糙度 0.72、金属度 0。Height Axis 的独立深度缓冲叠加绘制也改为中性灰顶点着色；只修改导入材质不会改变该叠加显示。尺寸归一化、物理参考身高、透明度、独立开关、对象绑定与实时跟随均保留。

### 资产与许可

模板资产遵循 [Unreal Engine EULA](https://www.unrealengine.com/eula/unreal)。根据已核实的 Templates 来源及第 1、2、4(a)(i)、5(b)、6(c)、7(a) 节，本项目判断可将这些 PNG 用于文档示意；此判断仅针对该具体来源。Epic 资产不按 GPL 提供，源资产与衍生网格只留本地，不进 Git 或插件 ZIP。详见[第三方说明](../THIRD_PARTY_NOTICES.md)。

忽略目录 `verification/ue-gray-mannequin/` 保存来源记录、本地导出工程、FBX、灰色 Blend 及审查证据。自动测试继续使用本项目自制夹具，构建和测试不依赖 Epic 人偶。预览脚本可通过 `HEIGHT_AXIS_REFERENCE_MODEL` 指向本地独立取得的模型；可移植默认值仍是生成夹具。

Unreal Engine 及相关商标归 Epic Games 所有。上方英文署名保留 Epic 的引擎版权与商标说明；人偶仅用于比例参照演示，本插件未获 Epic 背书。
