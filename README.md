# Python Web + GitHub Actions 入门

这是一个最小的 Python Web 应用，用来学习 continuous integration（持续集成，CI）。只使用 Python 标准库，无需 `pip install`。

应用提供两个地址：`/` 显示欢迎页面，`/health` 返回 `{"status": "ok"}`。页面文字来自 `config/app.json`。

## 1. 本地运行

需要 Python 3.13 或更新版本。在仓库根目录执行：

```bash
python3 app.py
```

浏览器打开 <http://localhost:8000>，按 Ctrl+C 停止。修改 `config/app.json` 中的 `message` 后重启，可以看到新文字。

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

## 2. 本地构建容器

先启动 Docker Desktop 或其他 Docker Engine，再执行：

```bash
docker build -t python-ci-demo:latest .
docker run --rm -p 8000:8000 python-ci-demo:latest
```

打开 <http://localhost:8000>。`Dockerfile` 将应用和默认配置打包进镜像；容器启动时执行 `python app.py`。

## 3. GitHub Actions 自动做什么

工作流在 [`.github/workflows/ci.yml`](.github/workflows/ci.yml)，按顺序执行：

```text
push / pull request / 手动触发
    → 下载代码 → 准备 Python → 测试应用
    → 构建镜像 → 启动容器验证 HTTP 响应
    → 导出镜像 + 打包配置 → 上传两个可下载产物
```

理解这几个关键词就能读懂工作流：

| 关键词 | 本例中的含义 |
| --- | --- |
| `on` | 什么事件触发工作流 |
| `jobs` | 要执行的任务；本例只有一个 `build` 任务 |
| `runs-on` | 在 GitHub 提供的 Ubuntu 临时机器上运行 |
| `steps` | 在这台机器上依次执行的步骤 |
| `uses` | 使用别人写好的 Action，例如下载代码或上传文件 |
| `run` | 执行命令，与本地终端的命令相同 |
| artifact | 工作流结束后保留下来供下载的文件 |

某一步失败，后面的普通步骤会跳过，GitHub 会显示红色失败状态。只有测试和构建都通过，才会上传本例的产物。

## 4. 触发第一次 CI

将这些文件提交并推送到 GitHub。在当前仓库中可以执行：

```bash
git add app.py config tests Dockerfile .dockerignore .gitignore .github/workflows/ci.yml README.md
git commit -m "Add Python web app and CI build"
git push origin main
```

打开仓库的 **Actions → Python CI → 对应运行记录**，点击 `build` 查看每一步日志。运行成功后，在该记录的 **Artifacts** 区域下载：

| 文件 | 内容 |
| --- | --- |
| `python-ci-demo.tar.gz` | 可用 `docker load` 导入的容器镜像 |
| `config.zip` | `config/app.json` 配置文件，保留 `config/` 目录结构 |

产物保留 7 天。本例使用 `upload-artifact@v7` 的 `archive: false`，直接下载上述文件，无需先解开额外的 ZIP。[官方说明](https://github.com/actions/upload-artifact#upload-an-individual-file-unzipped)

也可以在 **Actions → Python CI → Run workflow** 手动运行；需要先把工作流推送到默认分支。本例自动构建并提供下载，不会自动部署服务，也无需设置 Secrets 或登录镜像仓库。

## 5. 使用下载的镜像和配置

将两个产物下载到同一目录，在该目录执行：

```bash
docker load -i python-ci-demo.tar.gz
python3 -m zipfile -e config.zip .
```

可以先编辑解压后的 `config/app.json`，再挂载配置启动容器：

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/config:/app/config:ro" \
  python-ci-demo:latest
```

这样修改配置后只需重启容器，无需重新构建镜像。直接运行 Python 时，也可以通过 `APP_CONFIG` 环境变量指定其他 JSON 配置路径。配置 ZIP 只应包含示例配置，不要放密码或密钥。

GitHub 的 Ubuntu 工作流构建 Linux AMD64 镜像。Apple Silicon Mac 可以在上述 `docker run` 命令中增加 `--platform linux/amd64`，通过 Docker 的模拟能力运行；本地构建则默认使用本机架构。

## 6. 动手练习

1. 修改 `config/app.json` 的 `message`，提交并推送，观察 CI 自动运行，再下载新配置 ZIP。
2. 在测试中临时把健康检查预期的 `"ok"` 改成 `"wrong"`，提交后观察测试失败、构建步骤被跳过，再恢复测试。

这是学习用 HTTP 服务。Python 标准库的 `http.server` 不适合直接用于生产环境。[Python 官方说明](https://docs.python.org/3.13/library/http.server.html)

更多参考：[GitHub Actions 产物文档](https://docs.github.com/en/actions/tutorials/store-and-share-data)。
