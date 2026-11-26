# 功能清单

本清单记录通用脚本的功能边界及其对应的 Test / 业务调用参考。
`tests` 中的文件是带真实业务参数的调用示例，不是通用单元测试。

## 数据集工具

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
| `scripts/datasets/quarantine_unpaired_files.py` | 查找并隔离没有同名配对项的图片或标签，默认预览 | `tests/datasets/street_quarantine_unpaired_files.py` |
| `scripts/datasets/copy_unique_images_by_hash.py` | 按 MD5 或感知哈希复制唯一图片，支持保留原名，默认预览；感知哈希需 Pillow、ImageHash | `tests/datasets/recaptcha_copy_unique_images.py` |
| `scripts/datasets/download_oss_prefix.py` | 按 OSS 对象前缀并发下载文件，保留相对目录且默认预览；凭证仅从参数或环境变量读取 | `tests/datasets/hcaptcha_download_oss_prefix.py` |
| `scripts/datasets/export_image_md5_manifest.py` | 对图片原始字节或 Base64 解码内容计算 MD5，导出 JSON、Go 或 TSV 清单 | `tests/datasets/icon_hash_export_for_go.py` |

## 文档内容处理

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
| `scripts/documents/rename_voc_labels.py` | 按映射批量修改 Pascal VOC 类别名称，默认预览 | `tests/documents/road_puddle_rename_voc_labels.py` |
| `scripts/documents/sync_voc_image_sizes.py` | 按对应图片的真实尺寸同步 VOC width、height、depth，默认预览 | `tests/documents/street_sync_voc_image_sizes.py` |
| `scripts/documents/coco_to_voc.py` | 将 COCO 检测框转换为 Pascal VOC XML，支持类别筛选和可选复制图片 | `tests/documents/coco_outdoor_coco_to_voc.py` |
| `scripts/documents/remove_voc_labels.py` | 从 Pascal VOC XML 中批量移除指定类别对象，默认预览 | `tests/documents/street_remove_voc_labels.py` |
| `scripts/documents/extract_docx_content.py` | 从 DOCX 提取段落、表格二维数据和内嵌媒体，并生成 JSON 内容报告 | `tests/documents/sample_extract_docx_content.py` |

## 视觉算法与图像处理

| 脚本 | 功能描述 | Test / 业务调用参考 |
| --- | --- | --- |
| `scripts/vision/convert_png_to_jpg.py` | 将 PNG 转换为 JPG，透明区域可指定背景色，保留源文件 | `tests/vision/car_png_to_jpg.py` |
| `scripts/vision/crop_images_by_voc_template.py` | 使用一份 VOC XML 模板中的命名框批量裁剪图片 | `tests/vision/nine_crop_by_voc_template.py` |
| `scripts/vision/extract_gif_frames.py` | 按步长和分区提取 GIF 帧为 PNG | `tests/vision/ocr_gif_extract_frames.py` |
| `scripts/vision/extract_video_frames.py` | 按帧间隔或时间间隔批量提取视频帧 | `tests/vision/video_extract_every_two_seconds.py` |
| `scripts/vision/group_images_by_dhash.py` | 使用 dHash 将完全相同哈希的图片分组复制 | `tests/vision/nine_group_images_by_dhash.py` |
| `scripts/vision/inpaint_color_region.py` | 在指定 ROI 内按 HSV 色域生成蒙版并执行图像修复 | `tests/vision/db_boxes_inpaint_yellow_watermark.py` |
| `scripts/vision/merge_fading_video_targets.py` | 从静态背景视频抽帧，将不同时间渐显的目标合成到一张图 | `tests/vision/hcaptcha_merge_fading_video_targets.py` |
| `scripts/vision/crop_images_by_voc_annotations.py` | 按每张图片对应的 VOC XML 批量裁剪对象并按类别保存 | `tests/vision/geetest_crop_images_by_voc_annotations.py` |
| `scripts/vision/composite_rgba_foregrounds.py` | 将 RGBA 前景随机旋转、缩放并按透明度叠加到背景图，支持固定随机种子 | `tests/vision/icon_composite_augmentation.py` |
| `scripts/vision/find_color_outlier_targets.py` | 基于旋转不敏感的 Lab 颜色直方图，从贴合目标的检测框中识别视觉离群项 | `tests/vision/hcaptcha_find_color_outlier_targets.py` |
| `scripts/vision/stitch_base_with_indexed_images.py` | 将主图与同名前缀、按序号命名的小图缩放后纵向拼接，支持缺图占位和递归目录 | `tests/vision/geetest_v4_stitch_request_images.py` |
| `scripts/vision/extract_fixed_image_strip.py` | 按固定起点、宽度、间隔和数量批量切分横向图像条，可选保留顶部区域或读取透明通道 | `tests/vision/visionengine_extract_icon_strip.py` |
| `scripts/vision/split_images_into_grid.py` | 将单张或批量图片切成任意行列网格，按比例边界完整保留不能整除的边缘像素 | `tests/vision/captcha_split_three_by_three_grid.py` |

## 服务调度辅助

| 脚本 | 功能描述 | Test / 业务调用参考 |
| --- | --- | --- |
| `scripts/automation/invoke_image_json_service.py` | 将图片按 MD5 编码为 Base64 JSON 并调用可配置 HTTP 服务，默认预览 | `tests/automation/temu_invoke_image_service.py` |
| `scripts/automation/evaluate_image_text_service.py` | 批量调用图片转文本 HTTP 服务，根据文件名中的预期文本计算准确率并导出报告，默认预览 | `tests/automation/queueit_evaluate_ocr_common2.py` |

远程删除、账号分析和写死凭证的服务调用不会直接迁入；后续继续提取明确可复用的服务启动、健康检查、批量请求和客户端调用功能。
