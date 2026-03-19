---
name: ppvideo
description: 将PPTX 演示文稿转换为视频。包含完整的转换流程：PPTX→PDF→PNG→MP4。使用 when 用户要求将 PPTX转换为视频，或需要创建幻灯片视频。
---

# ppvideo - PPTX 转视频技能

将 PowerPoint 演示文稿 (.pptx) 转换为视频 (.mp4) 格式。

## 转换流程

### 步骤 1: PPTX convert to PDF

使用 LibreOffice 将 PPTX 转换为 PDF：

```bash
soffice --headless --convert-to pdf input.pptx
```

### 步骤 2: PDF convert to PNG files

使用 pdftoppm 将 PDF 转换为图片：

```bash
pdftoppm -png -r 200 input.pdf slide
```

- `-r 200`: 分辨率 200 DPI
- 输出: `slide-1.png`, `slide-2.png`, ...

### 步骤 3: PNG convert to a Video

使用 moviepy 将图片合成为视频：

```
python scripts/images2video.py slide-*.png --cleanup --output output.mp4
```

### 步骤 4: add bgm 可选 如果提供了bgm音乐文件
```
python scripts/add_bgm.py input.mp4 bgm_music.mp3
```

## 依赖安装

```bash
pip install moviepy pillow
```

需要系统已安装：
- LibreOffice (soffice 命令)
- Poppler (pdftoppm 命令)

Windows 安装 Poppler:
```bash
# 下载 pdftoppm Windows 版本并添加到 PATH
```

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 幻灯片时长 | 每张幻灯片显示秒数 | 3秒 |
| FPS | 视频帧率 | 24 |
| 分辨率 | PDF 转 PNG 的 DPI | 200 |

## 示例

将 `presentation.pptx` 转换为视频：

```bash
# 1. PPTX -> PDF
soffice --headless --convert-to pdf presentation.pptx

# 2. PDF -> PNG
pdftoppm -png -r 200 presentation.pdf slide

# 3. PNG -> Video (使用 Python 脚本)
python scripts/images2video.py slide-*.png --cleanup --output output.mp4
```

## 注意事项

- 确保 soffice 和 pdftoppm 已添加到系统 PATH
- 视频使用 H.264 编码，兼容性良好
- 使用 yuv420p 像素格式确保跨平台兼容
- 尺寸会自动调整为偶数（编码器要求）
