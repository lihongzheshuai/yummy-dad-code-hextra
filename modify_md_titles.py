#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时脚本：修改指定目录下的.md文件的title和二级标题
功能：
1. 如果第一个二级标题已包含title中的文字，则用二级标题覆盖title
2. 否则，将title拼接到第一个二级标题后（中间加空格），然后覆盖到title上
3. 同步更新第一个二级标题，确保与最终的title内容保持一致
4. 删除文章结尾多余的空行，只保留一行空行（符合markdownlint标准）
"""

import os
import re
import sys
from pathlib import Path


def extract_frontmatter_and_content(content):
    """提取YAML前置内容和正文内容"""
    # 匹配YAML前置内容
    frontmatter_pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if match:
        frontmatter = match.group(1)
        body_content = match.group(2)
        return frontmatter, body_content
    else:
        return None, content


def extract_title_from_frontmatter(frontmatter):
    """从YAML前置内容中提取title"""
    title_pattern = r'^title:\s*(.+)$'
    lines = frontmatter.split('\n')
    
    for i, line in enumerate(lines):
        match = re.match(title_pattern, line.strip())
        if match:
            title = match.group(1).strip()
            # 移除可能的引号
            if (title.startswith('"') and title.endswith('"')) or \
               (title.startswith("'") and title.endswith("'")):
                title = title[1:-1]
            return title, i
    
    return None, -1


def find_first_h2_title(content):
    """找到第一个二级标题"""
    # 匹配 ## 开头的二级标题
    h2_pattern = r'^##\s+(.+)$'
    lines = content.split('\n')
    
    for line in lines:
        match = re.match(h2_pattern, line.strip())
        if match:
            return match.group(1).strip()
    
    return None


def update_frontmatter_title(frontmatter, new_title, title_line_index):
    """更新YAML前置内容中的title"""
    lines = frontmatter.split('\n')
    
    if title_line_index >= 0 and title_line_index < len(lines):
        # 保持原有的格式，只更新title值
        original_line = lines[title_line_index]
        if ':' in original_line:
            prefix = original_line.split(':', 1)[0] + ': '
            lines[title_line_index] = prefix + new_title
    
    return '\n'.join(lines)


def update_first_h2_title(content, new_title):
    """更新内容中的第一个二级标题，使其与title保持一致"""
    # 匹配 ## 开头的二级标题
    h2_pattern = r'^(##\s+)(.+)$'
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        match = re.match(h2_pattern, line.strip())
        if match:
            # 保持原有的标记符号和空格，只更新标题内容
            prefix = match.group(1)  # "## "
            lines[i] = prefix + new_title
            break
    
    return '\n'.join(lines)


def normalize_end_lines(content):
    """规范化文件结尾的空行，只保留一行空行符合markdownlint标准"""
    # 移除结尾的所有空白字符（包括空格、制表符、换行符）
    content = content.rstrip()
    # 添加一个换行符，确保文件以单个换行符结尾
    content += '\n'
    return content


def process_md_file(file_path):
    """处理单个markdown文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取前置内容和正文
        frontmatter, body_content = extract_frontmatter_and_content(content)
        
        if frontmatter is None:
            print(f"警告: {file_path} 没有找到YAML前置内容，跳过处理")
            return False
        
        # 提取title
        current_title, title_line_index = extract_title_from_frontmatter(frontmatter)
        if current_title is None:
            print(f"警告: {file_path} 没有找到title字段，跳过处理")
            return False
        
        # 找到第一个二级标题
        first_h2 = find_first_h2_title(body_content)
        if first_h2 is None:
            print(f"警告: {file_path} 没有找到二级标题，跳过处理")
            return False
        
        # 决定新的title值
        new_title = None
        
        # 检查二级标题是否已包含title中的文字
        if current_title in first_h2:
            # 直接用二级标题覆盖title
            new_title = first_h2
            print(f"文件: {file_path}")
            print(f"  二级标题已包含title文字")
            print(f"  原title: {current_title}")
            print(f"  新title: {new_title}")
            print(f"  二级标题保持不变: {first_h2}")
        else:
            # 将title拼接到二级标题后
            new_title = f"{first_h2} {current_title}"
            print(f"文件: {file_path}")
            print(f"  拼接title和二级标题")
            print(f"  原title: {current_title}")
            print(f"  原二级标题: {first_h2}")
            print(f"  新title: {new_title}")
            print(f"  新二级标题: {new_title}")
        
        # 更新frontmatter中的title
        updated_frontmatter = update_frontmatter_title(frontmatter, new_title, title_line_index)
        
        # 更新正文中的第一个二级标题，使其与新title保持一致
        updated_body_content = update_first_h2_title(body_content, new_title)
        
        # 重构完整内容
        updated_content = f"---\n{updated_frontmatter}\n---\n{updated_body_content}"
        
        # 规范化文件结尾的空行
        updated_content = normalize_end_lines(updated_content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"  ✓ 文件已更新（包括空行规范化）\n")
        return True
        
    except Exception as e:
        print(f"错误: 处理文件 {file_path} 时出现异常: {str(e)}")
        return False


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python modify_md_titles.py <目录路径>")
        print("示例: python modify_md_titles.py ./content/gesp/1/practice/")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    
    if not os.path.exists(target_dir):
        print(f"错误: 目录 {target_dir} 不存在")
        sys.exit(1)
    
    if not os.path.isdir(target_dir):
        print(f"错误: {target_dir} 不是一个目录")
        sys.exit(1)
    
    # 查找所有.md文件
    md_files = list(Path(target_dir).glob("*.md"))
    
    if not md_files:
        print(f"在目录 {target_dir} 中没有找到.md文件")
        return
    
    print(f"找到 {len(md_files)} 个.md文件")
    print("开始处理...\n")
    
    success_count = 0
    
    for md_file in md_files:
        if process_md_file(md_file):
            success_count += 1
    
    print(f"处理完成! 成功处理了 {success_count}/{len(md_files)} 个文件")


if __name__ == "__main__":
    main()