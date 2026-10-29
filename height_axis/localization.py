# SPDX-License-Identifier: GPL-3.0-or-later
"""English UI source strings with optional Blender Simplified Chinese translation."""

import bpy

_ZH = {
    'Show Height Axis': '显示高度轴',
    'Show the selected geometry height, or a mouse-following reference ruler': '显示选中几何体的高度，或跟随鼠标的参考尺',
    'Freeze': '停止跟随',
    'Pin the current ruler and figure in world space; uncheck to resume following': '把当前尺子和人物固定在三维位置；取消勾选恢复跟随',
    'Reference Height (m)': '参考高度 (m)',
    'Reference ruler and figure height, always entered in metres': '参考尺与人物的高度，输入单位始终为米',
    'Left Offset (px)': '向左偏移 (px)',
    'Font Size': '字号',
    'Display Units': '显示单位',
    'Scene': '跟随场景',
    'Show Reference Figure': '显示参考人物',
    'Reference Model': '参考模型',
    'Figure Rotation': '人物朝向',
    'Figure Opacity': '人物不透明度',
    'Load Reference Figure': '加载参考人物',
    'Load a model as a height reference beside your selection or mouse': '选择模型文件，作为跟随物体或鼠标的身高参考',
    'Imported Up Axis': '导入后的向上轴',
    'Z (usual choice)': 'Z（通常选此项）',
    'Remove Reference Figure': '移除参考人物',
    'Switch to Object Mode to load a figure': '退出编辑模式后可加载人物',
    'Pinned in world space': '已固定在三维位置',
    'Selection: view-left': '选中：随视口保持在物体左侧',
    'No selection: mouse-left': '未选中：跟随鼠标左侧',
    'Enable viewport Overlays to see the guides': '开启视口 Overlays 以显示参照',
    'Draw error; see the system console': '绘制异常，详情见系统控制台',
    'Display a ruler or figure in the viewport before freezing': '先在视口显示尺子或人物，再冻结',
    'Reference import failed': '参考人物加载失败',
    'Reference figure loaded': '已加载参考人物',
    'Choose a Blend, FBX, OBJ, glTF/GLB or STL model': '请选择 Blend、FBX、OBJ、glTF/GLB 或 STL 模型',
    'Model file not found': '模型文件不存在',
    'Switch to Object Mode before loading a reference figure': '请先退出编辑模式再加载参考人物',
    'The file contains no visible mesh surfaces': '文件里没有可显示的网格表面',
    'The imported model has zero height; check the imported up axis': '模型的向上高度为零，请检查导入后的向上轴',
}


def register():
    messages = {(context, key): value for context in ('*', 'Operator') for key, value in _ZH.items()}
    bpy.app.translations.register(__package__, {'zh_HANS': messages, 'zh_CN': messages})


def unregister():
    bpy.app.translations.unregister(__package__)
