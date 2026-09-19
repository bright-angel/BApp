#!/usr/bin/env python3
"""
处理 GitHub Issue 提交的扩展
自动添加到 extensions.json，支持去重
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional

import requests
from github import Github


def load_extensions(file_path: str) -> List[Dict]:
    """加载扩展数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_extensions(file_path: str, extensions: List[Dict]) -> None:
    """保存扩展数据（按 last_commit 降序排序）"""
    extensions.sort(key=lambda x: x.get('last_commit', ''), reverse=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(extensions, f, ensure_ascii=False, indent=2)


def extract_repo_info(url: str) -> Optional[tuple]:
    """从 GitHub URL 提取仓库信息"""
    # 支持多种格式
    # https://github.com/owner/repo
    # https://github.com/owner/repo.git
    # github.com/owner/repo
    url = url.strip().rstrip('/')
    pattern = r'github\.com[/:]([^/]+)/([^/\.]+?)(?:\.git)?$'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None


def get_repo_info(g: Github, owner: str, repo: str) -> Optional[Dict]:
    """从 GitHub API 获取仓库信息"""
    try:
        repository = g.get_repo(f"{owner}/{repo}")

        # 获取第一次和最后一次提交
        commits = list(repository.get_commits())
        if not commits:
            return None

        first_commit = commits[-1].commit.author.date.strftime('%Y-%m-%d')
        last_commit = commits[0].commit.author.date.strftime('%Y-%m-%d')

        return {
            'first_commit': first_commit,
            'last_commit': last_commit
        }
    except Exception as e:
        print(f"❌ 获取仓库信息失败: {e}")
        return None


def parse_issue_body(body: str) -> Optional[Dict]:
    """解析 Issue 内容"""
    result = {}

    # 提取项目链接
    url_match = re.search(r'### 项目链接\s*\n\s*(.+)', body)
    if url_match:
        result['url'] = url_match.group(1).strip()

    # 提取标签
    tags_match = re.search(r'### 标签\s*\n\s*(.+?)(?=\n###|\Z)', body, re.DOTALL)
    if tags_match:
        tags_text = tags_match.group(1).strip()
        # 移除可能的示例文本
        tags_text = re.sub(r'常用标签参考:.*', '', tags_text, flags=re.DOTALL)
        # 提取实际标签
        tags = [t.strip() for t in tags_text.split(',') if t.strip() and not t.strip().startswith('-')]
        result['tags'] = ','.join(tags) if tags else ''

    # 提取描述
    desc_match = re.search(r'### 项目描述\s*\n\s*(.+?)(?=\n###|\Z)', body, re.DOTALL)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result if all(k in result for k in ['url', 'tags', 'description']) else None


def is_duplicate(extensions: List[Dict], url: str) -> bool:
    """检查是否重复（基于 URL）"""
    normalized_url = url.lower().rstrip('/').replace('.git', '')
    for ext in extensions:
        ext_url = ext.get('url', '').lower().rstrip('/').replace('.git', '')
        if ext_url == normalized_url:
            return True
    return False


def add_extension(token: str, data_file: str, issue_data: Dict) -> bool:
    """添加新扩展"""
    g = Github(token)

    # 加载现有数据
    extensions = load_extensions(data_file)
    print(f"📊 当前扩展数量: {len(extensions)}")

    # 解析项目 URL
    url = issue_data['url']
    repo_info = extract_repo_info(url)

    if not repo_info:
        print(f"❌ 无效的 GitHub URL: {url}")
        return False

    owner, repo = repo_info
    print(f"📦 项目: {owner}/{repo}")

    # 检查重复
    if is_duplicate(extensions, url):
        print(f"⚠️  扩展已存在，跳过: {url}")
        return False

    # 获取仓库信息
    print(f"🔍 获取仓库信息...")
    repo_data = get_repo_info(g, owner, repo)

    if not repo_data:
        print(f"❌ 无法获取仓库信息")
        return False

    # 构建新扩展数据
    new_extension = {
        'author': owner,
        'project': repo,
        'url': f"https://github.com/{owner}/{repo}",
        'first_commit': repo_data['first_commit'],
        'last_commit': repo_data['last_commit'],
        'tags': issue_data['tags'],
        'description': issue_data['description']
    }

    # 添加到列表
    extensions.append(new_extension)

    # 保存
    save_extensions(data_file, extensions)

    print(f"✅ 成功添加扩展:")
    print(f"   - 作者: {owner}")
    print(f"   - 项目: {repo}")
    print(f"   - 首次提交: {repo_data['first_commit']}")
    print(f"   - 最后提交: {repo_data['last_commit']}")
    print(f"   - 标签: {issue_data['tags']}")
    print(f"   - 总数: {len(extensions)}")

    return True


def main():
    # 从环境变量获取 Issue 信息
    issue_body = os.environ.get('ISSUE_BODY', '')
    # 支持 GITHUB_TOKEN 和 GH_TOKEN 两种环境变量
    github_token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN', '')

    if not issue_body:
        print("❌ 错误: 未找到 ISSUE_BODY 环境变量")
        sys.exit(1)

    if not github_token:
        print("❌ 错误: 未找到 GITHUB_TOKEN 或 GH_TOKEN 环境变量")
        sys.exit(1)

    print("="*60)
    print("🤖 自动处理扩展提交")
    print("="*60)

    # 解析 Issue
    print("\n📝 解析 Issue 内容...")
    issue_data = parse_issue_body(issue_body)

    if not issue_data:
        print("❌ 无法解析 Issue 内容")
        sys.exit(1)

    print(f"✅ 解析成功:")
    print(f"   - URL: {issue_data['url']}")
    print(f"   - 标签: {issue_data['tags']}")
    print(f"   - 描述: {issue_data['description'][:50]}...")

    # 添加扩展
    data_file = 'data/extensions.json'
    if not os.path.exists(data_file):
        print(f"❌ 错误: 数据文件不存在: {data_file}")
        sys.exit(1)

    try:
        success = add_extension(github_token, data_file, issue_data)
        if success:
            print("\n✅ 扩展添加成功！")
            sys.exit(0)
        else:
            print("\n⚠️  扩展未添加（可能是重复）")
            sys.exit(0)  # 不视为错误
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
