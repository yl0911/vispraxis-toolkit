# Local 本地适配

该目录用于保存当前机器、开发环境或临时业务所需的调用适配。

除本说明外，`local/` 下的内容默认被 Git 忽略，适合保存：

- 本机绝对路径和目录映射；
- 不同客户、项目或数据批次的参数组合；
- 本地模型地址、服务地址和端口；
- 从环境变量或本机密钥存储读取凭证的调用代码；
- 尚未确定是否具有共享价值的临时业务步骤。

推荐从 `tests/<类型>/` 复制一个接近的业务参考，然后在 `local` 下修改：

```powershell
New-Item -ItemType Directory local\my_project
Copy-Item tests\datasets\geetest_split_image_list.py local\my_project\split.py
```

可以同时维护多组调用：

```text
local/
├── workstation_a/
│   └── split.py
├── project_x/
│   ├── convert.py
│   └── extract.py
└── temporary_20261124/
    └── cleanup.py
```

边界约定：

- 通用功能修改到 `scripts/`。
- 适合共享的业务参数参考整理到 `tests/`。
- 只对本机或临时任务有效的内容保留在 `local/`。
- 不要把仅存在于 `local/` 的关键实现当作长期唯一版本。
- 即使目录被忽略，也不要在代码中直接写入真实密码或密钥；优先从环境变量或系统密钥存储读取。
