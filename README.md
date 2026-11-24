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
│   └── automation/        # 服务调用、启动与第三方客户端辅助
├── tests/                 # 可提交的业务调用参考和真实参数预设
├── local/                 # 当前机器/环境的适配调用，除 README 外不提交
└── docs/                  # 分类、迁移和调用规范
```

- `scripts`：只保存相对通用的实现，不写死客户、项目或本机路径。
- `tests`：不是单元测试，而是可共享的业务调用参考。可以保存真实目录结构、类别、尺寸和处理参数。
- `local`：用于不同开发环境的本地适配。这里可以复制 `tests` 中的调用并修改路径、凭证、服务地址或临时业务参数，也可以按业务保存多组调用。

## 功能清单

当前按数据集工具、文档内容处理、视觉算法与图像处理、服务调度辅助四个功能域整理。
完整的“脚本—功能描述—Test / 业务调用参考”对应关系见 [功能清单](docs/function-catalog.md)。

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

- [功能清单](docs/function-catalog.md)
- [脚本分类](docs/taxonomy.md)
- [命名规范](docs/naming-conventions.md)
- [调用约定](docs/script-call-convention.md)
- [来源取舍](docs/source-disposition.md)
- [迁移规则](docs/migration.md)
- [迁移状态](docs/migration-status.md)

已确认不迁移旧目录中的 `asr`、`backend`、`baiduapi`，以及缓存、生成物、远程删除、账号分析和其他明确无用内容。
