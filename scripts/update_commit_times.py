#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新所有扩展的首次和末次提交时间
"""

import json
import os
import sys
from datetime import datetime
from time import sleep

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from github import Github, RateLimitExceededException


def load_extensions(file_path):
    """加载扩展数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_extensions(file_path, extensions):
    """保存扩展数据"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(extensions, f, ensure_ascii=False, indent=2)


def extract_repo_info(url):
    """从 GitHub URL 提取仓库信息"""
    parts = url.rstrip('/').split('/')
    if len(parts) >= 5 and 'github.com' in url:
        return parts[-2], parts[-1]
    return None, None


def get_commit_times(g, owner, repo):
    """获取仓库的首次和末次提交时间"""
    try:
        repository = g.get_repo(f"{owner}/{repo}")
        commits = repository.get_commits()

        if commits.totalCount > 0:
            # 最新提交
            last_commit = commits[0]
            last_date = last_commit.commit.author.date.strftime('%Y-%m-%d')

            # 最早提交（获取所有提交的最后一个）
            all_commits = list(commits)
            first_commit = all_commits[-1]
            first_date = first_commit.commit.author.date.strftime('%Y-%m-%d')

            return first_date, last_date
    except RateLimitExceededException:
        print(f"⚠️  API 速率限制")
        raise
    except Exception as e:
        print(f"❌ 获取 {owner}/{repo} 失败: {e}")

    return None, None


def update_all_extensions(token, data_file):
    """更新所有扩展的提交时间"""
    g = Github(token)
    extensions = load_extensions(data_file)

    print(f"📊 总共 {len(extensions)} 个扩展需要更新\n")

    updated = 0
    failed = 0
    skipped = 0

    for i, ext in enumerate(extensions, 1):
        url = ext.get('url', '')
        owner, repo = extract_repo_info(url)

        if not owner or not repo:
            print(f"⚠️  [{i}/{len(extensions)}] 跳过无效 URL: {url}")
            skipped += 1
            continue

        print(f"🔄 [{i}/{len(extensions)}] {owner}/{repo}...", end=' ', flush=True)

        first_date, last_date = get_commit_times(g, owner, repo)

        if first_date and last_date:
            old_first = ext.get('first_commit', '')
            old_last = ext.get('last_commit', '')

            ext['first_commit'] = first_date
            ext['last_commit'] = last_date

            if old_first != first_date or old_last != last_date:
                print(f"✅ {old_first}/{old_last} → {first_date}/{last_date}")
                updated += 1
            else:
                print(f"✓ 无变化")
        else:
            print(f"❌ 失败")
            failed += 1

        # 避免触发速率限制
        # sleep(0.5)

        # 每 10 个保存一次（防止中断丢失数据）
        if i % 10 == 0:
            save_extensions(data_file, extensions)
            print(f"💾 已保存进度 ({i}/{len(extensions)})\n")

    # 最终保存
    save_extensions(data_file, extensions)

    print(f"\n{'='*60}")
    print(f"✅ 更新完成！")
    print(f"   - 总数: {len(extensions)}")
    print(f"   - 更新: {updated}")
    print(f"   - 失败: {failed}")
    print(f"   - 跳过: {skipped}")
    print(f"   - 无变化: {len(extensions) - updated - failed - skipped}")

    # 检查 API 速率限制
    try:
        rate_limit = g.get_rate_limit()
        print(f"\n📈 GitHub API 剩余:")
        print(f"   {rate_limit.core.remaining}/{rate_limit.core.limit}")
    except Exception:
        pass


def main():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        print("❌ 错误: 请设置 GITHUB_TOKEN 或 GH_TOKEN 环境变量")
        print("\n使用方法:")
        print("  export GITHUB_TOKEN='your_token_here'")
        print("  python scripts/update_commit_times.py")
        sys.exit(1)

    data_file = 'data/extensions.json'
    if not os.path.exists(data_file):
        print(f"❌ 错误: 找不到 {data_file}")
        sys.exit(1)

    try:
        update_all_extensions(token, data_file)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断，进度已保存")
        sys.exit(0)
    except RateLimitExceededException:
        print("\n❌ GitHub API 速率限制，请稍后重试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
