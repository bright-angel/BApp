#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新通用标签为具体标签
将"官方扩展"和"Burp扩展"更新为更具体的功能标签
"""

import json
import sys
import io

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def infer_tags(ext):
    """根据项目信息推断标签"""
    project = ext.get('project', '').lower()
    description = ext.get('description', '').lower()
    url = ext.get('url', '').lower()
    combined = project + ' ' + description

    tags = []

    # 官方扩展
    if 'portswigger' in ext.get('author', '').lower():
        tags.append('官方扩展')

    # AI/MCP相关
    if any(k in combined for k in ['mcp', 'ai', 'llm', 'gpt', 'claude']):
        tags.append('AI集成')

    # 主动扫描
    if any(k in combined for k in ['active scan', 'scanner', 'audit', 'crawl']):
        tags.append('主动扫描')

    # 被动扫描
    if any(k in combined for k in ['passive', 'monitor', 'detect']):
        tags.append('被动扫描')

    # 漏洞类型
    if any(k in combined for k in ['sql', 'sqli', 'injection']):
        tags.append('SQL注入')
    if any(k in combined for k in ['xss', 'cross-site']):
        tags.append('XSS检测')
    if any(k in combined for k in ['ssrf', 'server-side request']):
        tags.append('SSRF检测')
    if any(k in combined for k in ['xxe']):
        tags.append('XXE检测')

    # 权限测试
    if any(k in combined for k in ['auth', 'authorization', 'idor', 'privilege', 'access control']):
        tags.append('权限测试')

    # API安全
    if any(k in combined for k in ['api', 'rest', 'graphql', 'swagger', 'openapi']):
        tags.append('API安全')

    # 加密解密
    if any(k in combined for k in ['encrypt', 'decrypt', 'crypto', 'cipher', 'aes', 'rsa']):
        tags.append('加密解密')

    # WAF绕过
    if any(k in combined for k in ['waf', 'bypass', 'evasion']):
        tags.append('WAF绕过')

    # 流量处理
    if any(k in combined for k in ['http', 'request', 'response', 'proxy', 'intercept']):
        tags.append('流量处理')

    # 功能增强
    if any(k in combined for k in ['enhance', 'utility', 'tool', 'helper', 'logger', 'export']):
        tags.append('功能增强')

    # 如果没有推断出标签，使用通用标签
    if not tags:
        tags.append('Burp扩展')

    return tags


def main():
    # 读取数据
    with open('data/extensions.json', 'r', encoding='utf-8') as f:
        extensions = json.load(f)

    updated_count = 0

    print(f"开始更新标签...\n")

    # 遍历每个扩展
    for ext in extensions:
        old_tags = ext.get('tags', '')

        # 如果标签只是"官方扩展"或"Burp扩展"或为空，需要更新
        if old_tags in ['官方扩展', 'Burp扩展', '']:
            new_tags = infer_tags(ext)
            new_tags_str = ','.join(new_tags)

            ext['tags'] = new_tags_str

            print(f"[+] {ext['author']}/{ext['project']}")
            print(f"    {old_tags} -> {new_tags_str}\n")
            updated_count += 1

    # 保存更新后的数据
    with open('data/extensions.json', 'w', encoding='utf-8') as f:
        json.dump(extensions, f, ensure_ascii=False, indent=2)

    print(f"{'='*60}")
    print(f"更新完成: {updated_count} 个扩展的标签已更新")
    print(f"总扩展数: {len(extensions)}")


if __name__ == '__main__':
    main()
