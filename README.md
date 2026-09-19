# Burp Suite Extensions Directory

📦 一个简洁、快速的 Burp Suite 开源扩展检索网站。

## 🌟 特性

- **🔍 实时搜索** - 按名称、作者、标签或描述搜索扩展
- **📊 表格展示** - 清晰的表格视图，支持排序
- **📄 分页浏览** - 支持 10/25/50/100 条每页
- **🏷️ 智能标签** - 193 个功能标签，多维度分类
- **🎨 简洁界面** - 专业的暗色主题，响应式设计
- **⚡ 纯静态** - 无需后端，可直接部署到 GitHub Pages


## 🚀 快速开始

### 在线访问

```
https://bright-angel.github.io/BApp/
```

### 本地预览

直接用浏览器打开 `index.html` 文件，或使用 Python 启动本地服务器:

```bash
python -m http.server 8000
# 访问 http://localhost:8000
```

## 🔍 搜索示例

- 搜索 **"SQL注入"** - 查看所有 SQL 注入检测工具
- 搜索 **"API安全"** - 查看 API 测试扩展
- 搜索 **"AI集成"** - 查看 AI 相关工具
- 搜索 **"官方扩展"** - 查看 PortSwigger 官方项目

## 📝 提交新扩展

### 方式一：Issue 提交（推荐）

访问 [提交扩展页面](https://github.com/bright-angel/BApp/issues/new?template=submit-extension.yml)，填写表单即可自动处理。

### 方式二：手动编辑

编辑 `data/extensions.json` 文件:

```json
{
  "author": "作者名",
  "project": "项目名",
  "url": "https://github.com/author/project",
  "first_commit": "2020-01-01",
  "last_commit": "2026-09-19",
  "tags": "主动扫描,API安全,漏洞检测",
  "description": "扩展的简短描述"
}
```

## 🚢 部署到 GitHub Pages

1. Fork 本仓库
2. 进入仓库设置 → Pages
3. Source 选择 `main` 分支
4. 保存后访问 `https://你的用户名.github.io/BApp/`

项目已配置 GitHub Actions 自动部署。

## 🛠️ 维护工具

### 更新提交时间

```bash
export GH_TOKEN='your_github_token'
python scripts/update_commit_times.py
```

### 更新标签

```bash
python scripts/update_generic_tags.py
```

## 🛠️ 技术栈

- HTML5 + CSS3 + 原生 JavaScript
- 无框架依赖
- GitHub Pages 静态托管
- GitHub Actions 自动化

## 📄 许可证

MIT License

## 🙏 致谢

感谢 [@Mr-xn](https://github.com/Mr-xn) 的 [BurpSuite-collections](https://github.com/Mr-xn/BurpSuite-collections) 项目提供的扩展收集。

感谢所有 Burp Suite 扩展开发者的贡献！
