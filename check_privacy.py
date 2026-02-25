#!/usr/bin/env python3
"""
隐私安全检查脚本
扫描站点目录下的所有HTML、CSS、MD文件，检查是否包含敏感信息
敏感词列表：CY, 陈阳, 真实姓名, 电话, 手机, 邮箱, 地址, 家庭, 住址
"""

import os
import re
import sys
from pathlib import Path

# 敏感词列表（不区分大小写）
SENSITIVE_PATTERNS = [
    r'\bCY\b',
    r'陈阳',
    r'真实姓名',
    r'电话',
    r'手机',
    r'1[3-9]\d{9}',  # 手机号简单匹配
    r'\b[0-9]{3,4}-[0-9]{7,8}\b',  # 座机
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
    r'地址',
    r'家庭',
    r'住址',
    r'上海市?',
    r'北京市?',
    r'广州市?',
    r'深圳市?',
]

# 例外：允许的邮箱后缀和git协议
ALLOWED_EMAIL_DOMAINS = ['example.com', 'lisi-ai.github.io']
GIT_PROTOCOL_PATTERNS = [r'git@[a-zA-Z0-9.-]+:']

def check_file_for_sensitive(file_path):
    """检查单个文件是否包含敏感信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        findings = []

        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for pattern in SENSITIVE_PATTERNS:
                # 特殊处理邮箱
                if '@' in line and '邮箱' not in pattern:
                    # 检查是否是git协议
                    is_git_protocol = False
                    for git_pattern in GIT_PROTOCOL_PATTERNS:
                        if re.search(git_pattern, line):
                            is_git_protocol = True
                            break

                    if not is_git_protocol:
                        # 提取邮箱
                        emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', line)
                        for email in emails:
                            domain = email.split('@')[1]
                            if domain not in ALLOWED_EMAIL_DOMAINS:
                                findings.append(f"  行 {i}: 发现可疑邮箱 {email}")
                else:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        findings.append(f"  行 {i}: 匹配敏感词模式 '{pattern}' -> '{match.group()}'")

        return findings
    except Exception as e:
        return [f"  读取文件出错: {str(e)}"]

def main():
    """主函数"""
    site_dir = Path.cwd()
    print(f"开始隐私安全检查 - 目录: {site_dir}")
    print("-" * 60)

    # 收集所有要检查的文件
    files_to_check = []
    for ext in ['*.html', '*.css', '*.md', '*.txt']:
        files_to_check.extend(site_dir.glob(f'**/{ext}'))

    # 排除隐藏目录和备份文件
    files_to_check = [f for f in files_to_check if not any(part.startswith('.') for part in f.parts)]

    print(f"找到 {len(files_to_check)} 个文件待检查\n")

    has_issues = False
    for file_path in sorted(files_to_check):
        rel_path = file_path.relative_to(site_dir)
        print(f"检查: {rel_path}")

        findings = check_file_for_sensitive(file_path)
        if findings:
            has_issues = True
            print(f"⚠️  发现潜在问题:")
            for finding in findings:
                print(finding)
        else:
            print(f"✅ 通过")
        print()

    print("-" * 60)
    if has_issues:
        print("❌ 安全检查未通过：发现潜在隐私问题，请检查以上报告")
        sys.exit(1)
    else:
        print("✅ 所有文件通过隐私安全检查")
        print("\n建议在git提交前再次确认：")
        print("1. 检查是否有任何真实姓名、地址信息")
        print("2. 确认邮箱地址只使用了 example.com 或 lisi-ai.github.io 域名")
        print("3. 确保没有透露 CY 关键词")
        sys.exit(0)

if __name__ == "__main__":
    main()
