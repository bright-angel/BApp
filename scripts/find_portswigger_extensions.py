#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找 PortSwigger 官方的 Burp Suite 扩展
包括官方开发的和 fork 的项目（追踪到源作者）
"""

import json
import os
import sys
from time import sleep

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from github import Github


def load_existing_extensions(file_path):
    """加载现有扩展数据"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_extensions(file_path, extensions):
    """保存扩展数据"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(extensions, f, ensure_ascii=False, indent=2)


def get_portswigger_repos(token=None):
    """获取 PortSwigger 组织的所有仓库"""
    if token:
        g = Github(token)
        org = g.get_organization('PortSwigger')
        repos = list(org.get_repos())
    else:
        # 使用 REST API（无需认证，但有速率限制）
        url = 'https://api.github.com/orgs/PortSwigger/repos'
        params = {'type': 'all', 'per_page': 100}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"❌ API 请求失败: {response.status_code}")
            print(f"   {response.text}")
            return []

        repos = response.json()

        # 检查是否是错误响应
        if isinstance(repos, dict) and 'message' in repos:
            print(f"❌ API 错误: {repos.get('message')}")
            return []

    return repos


def get_parent_repo(g, repo_full_name):
    """获取 fork 仓库的源仓库信息"""
    try:
        repo = g.get_repo(repo_full_name)
        if repo.fork and repo.parent:
            parent = repo.parent
            return {
                'author': parent.owner.login,
                'project': parent.name,
                'url': parent.html_url,
                'description': parent.description or ''
            }
    except Exception as e:
        print(f"  获取源仓库失败: {e}")
    return None


def is_burp_extension(repo_name, description):
    """判断是否是 Burp Suite 扩展"""
    keywords = [
        'burp', 'extension', 'plugin',
        'scanner', 'intruder', 'repeater',
        'proxy', 'extender'
    ]

    text = f"{repo_name} {description}".lower()
    return any(keyword in text for keyword in keywords)


def main():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print("⚠️  未设置 GITHUB_TOKEN，使用公开 API（速率限制更严格）")
        g = None
    else:
        g = Github(token)

    data_file = 'data/extensions.json'
    existing = load_existing_extensions(data_file)
    existing_urls = {ext['url'] for ext in existing}

    print("🔍 正在查找 PortSwigger 组织的仓库...\n")

    repos = get_portswigger_repos(token)
    print(f"找到 {len(repos)} 个仓库\n")

    new_extensions = []

    for repo in repos:
        # 检查响应类型
        if isinstance(repo, str):
            # 错误消息
            print(f"API 错误: {repo}")
            continue
        elif isinstance(repo, dict):
            # REST API 响应
            name = repo.get('name', '')
            html_url = repo.get('html_url', '')
            is_fork = repo.get('fork', False)
            description = repo.get('description') or ''
            full_name = repo.get('full_name', '')
        else:
            # PyGithub 对象
            name = repo.name
            html_url = repo.html_url
            is_fork = repo.fork
            description = repo.description or ''
            full_name = repo.full_name

        # 跳过已存在的
        if html_url in existing_urls:
            print(f"✓ 已存在: {name}")
            continue

        # 判断是否是 Burp 扩展
        if not is_burp_extension(name, description):
            print(f"⊘ 跳过非扩展: {name}")
            continue

        print(f"\n🆕 发现新扩展: {name}")
        print(f"   URL: {html_url}")
        print(f"   Fork: {is_fork}")

        if is_fork and g:
            # 获取源仓库
            print(f"   正在追踪源仓库...")
            parent_info = get_parent_repo(g, full_name)

            if parent_info:
                # 检查源仓库是否已存在
                if parent_info['url'] in existing_urls:
                    print(f"   源仓库已存在: {parent_info['url']}")
                else:
                    print(f"   ✅ 源仓库: {parent_info['author']}/{parent_info['project']}")
                    new_extensions.append({
                        'author': parent_info['author'],
                        'project': parent_info['project'],
                        'url': parent_info['url'],
                        'first_commit': '2020-01-01',  # 需要后续更新
                        'last_commit': '2026-09-19',
                        'tags': 'Burp扩展',
                        'description': parent_info['description']
                    })
                    existing_urls.add(parent_info['url'])
        else:
            # PortSwigger 官方开发的扩展
            print(f"   ✅ 官方扩展")
            new_extensions.append({
                'author': 'PortSwigger',
                'project': name,
                'url': html_url,
                'first_commit': '2020-01-01',  # 需要后续更新
                'last_commit': '2026-09-19',
                'tags': '官方扩展',
                'description': description
            })
            existing_urls.add(html_url)

        sleep(0.5)  # 避免速率限制

    if new_extensions:
        # 合并新扩展
        all_extensions = existing + new_extensions
        save_extensions(data_file, all_extensions)

        print(f"\n{'='*60}")
        print(f"✅ 发现 {len(new_extensions)} 个新扩展")
        print(f"   总扩展数: {len(all_extensions)}")
        print(f"\n新增扩展列表:")
        for ext in new_extensions:
            print(f"  - {ext['author']}/{ext['project']}")
            print(f"    {ext['url']}")

        print(f"\n💡 提示: 运行 update_commit_times.py 更新提交时间")
    else:
        print(f"\n✓ 没有发现新扩展")


if __name__ == '__main__':
    main()
