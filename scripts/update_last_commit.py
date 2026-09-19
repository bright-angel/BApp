#!/usr/bin/env python3
"""
自动更新 Burp Suite 扩展的最后提交时间
通过 GitHub API 获取每个仓库的最新提交日期
"""

import json
import os
import sys
from datetime import datetime
from time import sleep
from typing import Dict, List

import requests
from github import Github, RateLimitExceededException


def load_extensions(file_path: str) -> List[Dict]:
    """加载扩展数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_extensions(file_path: str, extensions: List[Dict]) -> None:
    """保存扩展数据"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(extensions, f, ensure_ascii=False, indent=2)


def extract_repo_info(url: str) -> tuple:
    """从 GitHub URL 提取仓库信息"""
    # https://github.com/owner/repo
    parts = url.rstrip('/').split('/')
    if len(parts) >= 5 and 'github.com' in url:
        return parts[-2], parts[-1]
    return None, None


def get_last_commit_date(g: Github, owner: str, repo: str) -> str:
    """获取仓库最后提交日期"""
    try:
        repository = g.get_repo(f"{owner}/{repo}")
        # 获取默认分支的最新提交
        commits = repository.get_commits()
        if commits.totalCount > 0:
            last_commit = commits[0]
            # 返回 YYYY-MM-DD 格式
            return last_commit.commit.author.date.strftime('%Y-%m-%d')
    except RateLimitExceededException:
        print(f"⚠️  API 速率限制，等待...")
        raise
    except Exception as e:
        print(f"❌ 获取 {owner}/{repo} 失败: {e}")
    return None


def update_extensions_data(token: str, data_file: str) -> None:
    """更新所有扩展的最后提交日期"""
    # 初始化 GitHub 客户端
    g = Github(token)

    # 加载数据
    extensions = load_extensions(data_file)
    print(f"📊 加载了 {len(extensions)} 个扩展")

    updated_count = 0
    failed_count = 0

    for i, ext in enumerate(extensions, 1):
        url = ext.get('url', '')
        owner, repo = extract_repo_info(url)

        if not owner or not repo:
            print(f"⚠️  [{i}/{len(extensions)}] 跳过无效 URL: {url}")
            failed_count += 1
            continue

        print(f"🔄 [{i}/{len(extensions)}] 更新 {owner}/{repo}...", end=' ')

        last_commit = get_last_commit_date(g, owner, repo)

        if last_commit:
            old_date = ext.get('last_commit', '')
            ext['last_commit'] = last_commit

            if old_date != last_commit:
                print(f"✅ {old_date} → {last_commit}")
                updated_count += 1
            else:
                print(f"✓ 无变化 ({last_commit})")
        else:
            print(f"❌ 失败")
            failed_count += 1

        # 避免触发速率限制
        sleep(0.5)

    # 保存更新后的数据
    save_extensions(data_file, extensions)

    print(f"\n{'='*60}")
    print(f"✅ 更新完成！")
    print(f"   - 总数: {len(extensions)}")
    print(f"   - 更新: {updated_count}")
    print(f"   - 失败: {failed_count}")
    print(f"   - 无变化: {len(extensions) - updated_count - failed_count}")

    # 检查 API 速率限制
    rate_limit = g.get_rate_limit()
    core = rate_limit.core
    print(f"\n📈 GitHub API 速率限制:")
    print(f"   - 剩余: {core.remaining}/{core.limit}")
    print(f"   - 重置时间: {core.reset.strftime('%Y-%m-%d %H:%M:%S UTC')}")


def main():
    # 获取 GitHub Token，支持 GITHUB_TOKEN 和 GH_TOKEN
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print("❌ 错误: 未找到 GITHUB_TOKEN 或 GH_TOKEN 环境变量")
        sys.exit(1)

    # 数据文件路径
    data_file = 'data/extensions.json'
    if not os.path.exists(data_file):
        print(f"❌ 错误: 数据文件不存在: {data_file}")
        sys.exit(1)

    try:
        update_extensions_data(token, data_file)
    except RateLimitExceededException:
        print("\n❌ GitHub API 速率限制已达上限，请稍后重试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
