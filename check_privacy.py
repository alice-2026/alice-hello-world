#!/usr/bin/env python3
"""
隐私检查脚本 - 扫描站点文件是否包含敏感信息
检查项：CY、真实姓名、地址、电话、私人邮箱等关键词
"""

import os
import re
import sys

# 敏感词列表（可根据需要扩展）
SENSITIVE_PATTERNS = [
    r'CY',
    r'程\s*越',
    r'cheng\s*yue',
    r'\d{11}',  # 简单手机号
    r'\d{3,4}[-\s]\d{7,8}',  # 简单座机
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 邮箱
    r'地址[:：]\s*\S+',
    r'电话[:：]\s*\S+',
]

def scan_file(filepath):
    """扫描单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        findings = []
        for pattern in SENSITIVE_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                findings.append({
                    'pattern': pattern,
                    'matches': matches[:5]  # 最多显示5个
                })
        
        return findings
    except Exception as e:
        print(f"  读取失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("隐私检查脚本 - 扫描敏感信息")
    print("=" * 60)
    
    # 要扫描的文件类型
    extensions = ['.html', '.css', '.js', '.md', '.txt']
    
    # 收集所有文件
    files_to_scan = []
    for root, dirs, files in os.walk('.'):
        # 忽略隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                files_to_scan.append(os.path.join(root, file))
    
    print(f"\n找到 {len(files_to_scan)} 个待检查文件")
    
    # 扫描每个文件
    has_issues = False
    for filepath in sorted(files_to_scan):
        print(f"\n检查: {filepath}")
        findings = scan_file(filepath)
        
        if findings:
            has_issues = True
            for f in findings:
                print(f"  ⚠️  发现敏感模式: {f['pattern']}")
                print(f"     匹配示例: {', '.join(str(m) for m in f['matches'])}")
        else:
            print("  ✅ 未发现明显敏感信息")
    
    print("\n" + "=" * 60)
    if has_issues:
        print("❌ 检查完成：发现潜在敏感信息，请人工确认")
        sys.exit(1)
    else:
        print("✅ 检查完成：未发现明显敏感信息")
        sys.exit(0)

if __name__ == "__main__":
    main()