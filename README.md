# VisPraxis Toolkit

VisPraxis Toolkit 是服务于开源项目 [**VisPraxis**](https://github.com/yl0911/VisPraxis) 的脚本汇总仓库。
项目只迁移仍有价值、可以复用的功能，将通用脚本与经常变化的业务参数分开维护。

## 目录职责

```text
vispraxis-toolkit/
├── scripts/               # 通用脚本，保持稳定、可单独调用
│   ├── datasets/          # 数据集获取、整理、拆分、去重和管理
│   ├── documents/         # 标注、XML、JSON、PDF 等文档内容处理
│   ├── vision/            # 图像转换、裁剪、修复、聚类等视觉处理
│   └── automation/        # 服务启动、调用和第三方客户端辅助（待迁移）
├── tests/                 # 可提交的业务调用参考和真实参数预设
├── local/                 # 当前机器/环境的适配调用，除 README 外不提交
└── docs/                  # 分类、迁移和调用规范
```

- `scripts`：只保存相对通用的实现，不写死客户、项目或本机路径。
- `tests`：不是单元测试，而是可共享的业务调用参考。可以保存真实目录结构、类别、尺寸和处理参数。
- `local`：用于不同开发环境的本地适配。这里可以复制 `tests` 中的调用并修改路径、凭证、服务地址或临时业务参数，也可以按业务保存多组调用。

## 功能清单

### 数据集工具

| 脚本 | 功能描述 | Test / 业务调用参考 |
| --- | --- | --- |
| `scripts/datasets/move_images_matching_xml.py` | 按 XML 与图片同名关系筛选并移动图片，默认预览 | `tests/datasets/geetest_move_images_matching_xml.py` |
| `scripts/datasets/move_md5_duplicates.py` | 对比同名文件 MD5，将完全重复文件移动到指定目录，默认预览 | `tests/datasets/temu_move_md5_duplicates.py` |
| `scripts/datasets/organize_images_and_xml.py` | 将混合目录中的图片和 XML 分别整理到目标目录，默认预览 | `tests/datasets/street_organize_images_and_xml.py` |
| `scripts/datasets/rename_files_sequentially.py` | 使用标签和序号批量重命名文件，包含冲突检查，默认预览 | `tests/datasets/flowers_rename_files.py` |
| `scripts/datasets/split_image_list.py` | 随机生成训练集和验证集图片路径清单 | `tests/datasets/geetest_split_image_list.py` |
| `scripts/datasets/split_log_embedded_images.py` | 按组拆分日志并解码其中的 icon/background Base64 图片 | `tests/datasets/visionengine_split_log_images.py` |
| `scripts/datasets/uppercase_filename_prefix.py` | 将文件名第一个下划线前的部分转换为大写，默认预览 | `tests/datasets/image2text_uppercase_prefix.py` |
| `scripts/datasets/select_voc_samples_by_labels.py` | 按包含/排除类别筛选并复制成对的图片和 VOC XML | `tests/datasets/byteai_select_outdoor_voc_samples.py` |
| `scripts/datasets/rename_directories_to_pinyin.py` | 将直接子目录的中文名称转换为拼音，默认预览 | `tests/datasets/new_directories_to_pinyin.py` |
| `scripts/datasets/split_paired_dataset.py` | 将成对图片和标签按比例复制到 train/val/test | `tests/datasets/notouchshape_split_paired_dataset.py` |

### 文档内容处理

| 脚本 | 功能描述 | Test / 业务调用参考 |
| --- | --- | --- |
| `scripts/documents/copy_xml_template_for_images.py` | 为每张图片复制一份同名 XML 模板，默认预览 | `tests/documents/nine_copy_xml_template.py` |
| `scripts/documents/count_annotation_labels.py` | 统计 YOLO TXT 和 Pascal VOC XML 中的类别数量 | `tests/documents/fire_smoke_label_statistics.py` |
| `scripts/documents/create_empty_yolo_labels.py` | 为没有 XML 标注的图片创建空 YOLO TXT 标签 | `tests/documents/road_puddle_create_empty_labels.py` |
| `scripts/documents/offset_yolo_class_ids.py` | 对 YOLO 标签类别编号统一增加或减少偏移量，默认预览 | `tests/documents/coco_combined_offset_yolo_labels.py` |
| `scripts/documents/render_pdf_pages.py` | 使用 PyMuPDF 将 PDF 页面渲染为图片 | `tests/documents/sample_pdf_to_images.py` |
| `scripts/documents/svg_to_png.py` | 使用 CairoSVG 将单个或批量 SVG 渲染为 PNG | `tests/documents/captcha_svg_to_png.py` |
| `scripts/documents/voc_to_yolo.py` | 将 Pascal VOC XML 检测框转换为 YOLO TXT 标签 | `tests/documents/geetest_voc_to_yolo.py` |
| `scripts/documents/voc_to_coco.py` | 将一组 Pascal VOC XML 标注汇总为 COCO instances JSON | `tests/documents/coco_person_voc_to_coco.py` |
| `scripts/documents/yolo_to_voc.py` | 根据对应图片尺寸将 YOLO TXT 标签转换为 Pascal VOC XML | `tests/documents/notouchshape_yolo_to_voc.py` |
| `scripts/documents/split_voc_by_label_groups.py` | 按配置的类别组将一份 VOC 拆成多组 XML | `tests/documents/telecom_split_voc_label_groups.py` |

### 视觉算法与图像处理

| 脚本 | 功能描述 | Test / 业务调用参考 |
| --- | --- | --- |
| `scripts/vision/convert_png_to_jpg.py` | 将 PNG 转换为 JPG，透明区域可指定背景色，保留源文件 | `tests/vision/car_png_to_jpg.py` |
| `scripts/vision/crop_images_by_voc_template.py` | 使用一份 VOC XML 模板中的命名框批量裁剪图片 | `tests/vision/nine_crop_by_voc_template.py` |
| `scripts/vision/extract_gif_frames.py` | 按步长和分区提取 GIF 帧为 PNG | `tests/vision/ocr_gif_extract_frames.py` |
| `scripts/vision/extract_video_frames.py` | 按帧间隔或时间间隔批量提取视频帧 | `tests/vision/video_extract_every_two_seconds.py` |
| `scripts/vision/group_images_by_dhash.py` | 使用 dHash 将完全相同哈希的图片分组复制 | `tests/vision/nine_group_images_by_dhash.py` |
| `scripts/vision/inpaint_color_region.py` | 在指定 ROI 内按 HSV 色域生成蒙版并执行图像修复 | `tests/vision/db_boxes_inpaint_yellow_watermark.py` |

### 服务调度辅助

当前还没有迁入确认通用的 `automation` 脚本。远程删除、账号分析、写死凭证的服务调用不会直接迁入；后续只提取明确可复用的服务启动、健康检查、批量请求和客户端调用功能。

## 使用方式

通用脚本可以直接查看帮助并调用：

```powershell
python scripts/documents/voc_to_yolo.py --help
python scripts/vision/extract_video_frames.py --help
```

共享业务参考从仓库根目录以模块方式运行：

```powershell
python -m tests.datasets.geetest_move_images_matching_xml
python -m tests.documents.geetest_voc_to_yolo
```

会移动、重命名或覆盖文件的脚本一般默认只预览，需要明确传入 `--execute` 才执行。运行前仍应检查对应业务测试中的路径和参数。

## Local 本地适配

`local` 用于本机和当前环境的调用适配，不进入版本控制。推荐从 `tests` 复制最接近的业务参考再修改：

```powershell
New-Item -ItemType Directory local\my_project
Copy-Item tests\documents\geetest_voc_to_yolo.py local\my_project\voc_to_yolo.py
```

可以维护多组本地调用：

```text
local/
├── workstation_a/
├── customer_demo/
├── project_x/
└── temporary_20261124/
```

本地文件可以修改路径、类别、模型地址、凭证读取方式和临时业务步骤。通用逻辑有改进时应修改 `scripts`；具有共享价值的业务参考应整理后放入 `tests`，不要把唯一有效实现长期留在 `local`。

详细说明：

- [脚本分类](docs/taxonomy.md)
- [命名规范](docs/naming-conventions.md)
- [调用约定](docs/script-call-convention.md)
- [来源取舍](docs/source-disposition.md)
- [迁移规则](docs/migration.md)
- [迁移状态](docs/migration-status.md)

已确认不迁移旧目录中的 `asr`、`backend`、`baiduapi`，以及缓存、生成物、远程删除、账号分析和其他明确无用内容。
