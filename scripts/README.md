# BApp 自动更新脚本说明

本目录包含用于自动更新 Burp Suite 扩展数据的脚本。

## 📁 文件说明

- `update_last_commit.py` - 自动更新所有扩展的最后提交时间

## 🚀 使用方法

### 本地运行

```bash
# 安装依赖
pip install requests PyGithub

# 设置 GitHub Token（需要 repo 读权限）
export GHTOKEN="your_GHTOKEN"

# 运行更新脚本
python scripts/update_last_commit.py
```

### GitHub Actions 自动运行

脚本会通过 GitHub Actions 每周一自动运行，无需手动操作。

## 🔑 获取 GitHub Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择 `public_repo` 权限
4. 生成并复制 Token

**注意**: GitHub Actions 使用内置的 `GHTOKEN`，无需额外配置。

## ⚙️ 工作原理

1. 读取 `data/extensions.json` 文件
2. 遍历每个扩展的 GitHub 仓库
3. 通过 GitHub API 获取最新提交时间
4. 更新 `last_commit` 字段
5. 保存更新后的 JSON 文件

## 📊 API 速率限制

- **认证请求**: 5000 次/小时
- **未认证请求**: 60 次/小时

脚本会自动处理速率限制，并在请求间添加延迟。
