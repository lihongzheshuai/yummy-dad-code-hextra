#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Markdown文件中空title的临时脚本
递归查找所有.md文件，检查frontmatter中title值为空的文件，
将文件中第一个二级标题（## 标题）的值赋给title字段
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Optional, Tuple

class TitleFixer:
    """空title修复器"""
    
    def __init__(self, root_path: str):
        """
        初始化修复器
        
        Args:
            root_path: 根路径
        """
        self.root_path = Path(root_path)
        self.stats = {
            "total_files": 0,
            "empty_title_files": 0,
            "fixed_files": 0,
            "no_h2_files": 0,
            "errors": 0
        }
    
    def parse_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
        """
        解析Markdown文件的frontmatter
        
        Args:
            content: 文件内容
            
        Returns:
            Tuple[frontmatter_dict, body_content]
        """
        # 匹配frontmatter（用---包围的YAML内容）
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            return None, content
        
        frontmatter_str = match.group(1)
        body = match.group(2)
        
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter, body
        except yaml.YAMLError as e:
            print(f"YAML解析错误: {e}")
            return None, content
    
    def format_frontmatter(self, frontmatter: Dict) -> str:
        """格式化frontmatter为YAML字符串"""
        # 定义字段顺序
        field_order = ['layout', 'title', 'date', 'author', 'comments', 'tags', 'categories', 'slug', 'type', 'weight']
        
        lines = []
        
        # 按顺序添加字段
        for field in field_order:
            if field in frontmatter:
                value = frontmatter[field]
                
                if isinstance(value, list):
                    # 处理数组
                    if len(value) == 0:
                        lines.append(f'{field}: []')
                    else:
                        lines.append(f'{field}:')
                        for item in value:
                            if isinstance(item, str):
                                lines.append(f'- {item}')
                            else:
                                lines.append(f'- {str(item)}')
                elif isinstance(value, bool):
                    # 处理布尔值
                    lines.append(f'{field}: {str(value).lower()}')
                elif isinstance(value, (int, float)):
                    # 处理数字
                    lines.append(f'{field}: {value}')
                else:
                    # 处理字符串
                    if isinstance(value, str) and (':' in value or value.startswith('#')):
                        lines.append(f'{field}: "{value}"')
                    else:
                        lines.append(f'{field}: {value}')
        
        # 添加其他未在顺序中的字段
        for key, value in frontmatter.items():
            if key not in field_order:
                if isinstance(value, list):
                    if len(value) == 0:
                        lines.append(f'{key}: []')
                    else:
                        lines.append(f'{key}:')
                        for item in value:
                            if isinstance(item, str):
                                lines.append(f'- {item}')
                            else:
                                lines.append(f'- {str(item)}')
                elif isinstance(value, bool):
                    lines.append(f'{key}: {str(value).lower()}')
                elif isinstance(value, (int, float)):
                    lines.append(f'{key}: {value}')
                else:
                    if isinstance(value, str) and (':' in value or value.startswith('#')):
                        lines.append(f'{key}: "{value}"')
                    else:
                        lines.append(f'{key}: {value}')
        
        return '\n'.join(lines)
    
    def extract_first_h2_title(self, body: str) -> Optional[str]:
        """
        从Markdown内容中提取第一个二级标题
        
        Args:
            body: Markdown正文内容
            
        Returns:
            第一个二级标题的文本，如果没有找到则返回None
        """
        # 匹配二级标题 ## 标题内容
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                # 提取标题内容，去掉 ## 和可能的尾随空格
                title = line[3:].strip()
                if title:
                    return title
        
        return None
    
    def is_empty_title(self, title) -> bool:
        """
        检查title是否为空
        
        Args:
            title: title值
            
        Returns:
            是否为空
        """
        if title is None:
            return True
        if isinstance(title, str) and title.strip() == '':
            return True
        return False
    
    def process_file(self, filepath: Path) -> bool:
        """
        处理单个文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            是否成功修复
        """
        self.stats["total_files"] += 1
        
        try:
            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析frontmatter
            frontmatter, body = self.parse_frontmatter(content)
            if not frontmatter:
                print(f"跳过文件 {filepath.name}: 无法解析frontmatter")
                return False
            
            # 检查title是否为空
            if not self.is_empty_title(frontmatter.get('title')):
                return False  # title不为空，无需处理
            
            self.stats["empty_title_files"] += 1
            print(f"发现空title文件: {filepath.name}")
            
            # 提取第一个二级标题
            h2_title = self.extract_first_h2_title(body)
            if not h2_title:
                print(f"  ✗ 未找到二级标题，跳过")
                self.stats["no_h2_files"] += 1
                return False
            
            # 设置title
            frontmatter['title'] = h2_title
            print(f"  ✓ 设置title: {h2_title}")
            
            # 格式化frontmatter
            formatted_frontmatter = self.format_frontmatter(frontmatter)
            
            # 重新构建文件内容
            new_content = f"---\n{formatted_frontmatter}\n---\n{body}"
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.stats["fixed_files"] += 1
            return True
            
        except Exception as e:
            print(f"处理文件 {filepath.name} 时出错: {e}")
            self.stats["errors"] += 1
            return False
    
    def scan_and_fix(self) -> None:
        """扫描并修复所有空title文件"""
        print("=" * 60)
        print("Markdown文件空title修复工具")
        print("=" * 60)
        print(f"扫描根目录: {self.root_path}")
        print("-" * 60)
        
        if not self.root_path.exists():
            print(f"错误: 根目录不存在 - {self.root_path}")
            return
        
        # 递归查找所有.md文件
        md_files = list(self.root_path.rglob("*.md"))
        
        # 过滤掉以_开头的文件
        md_files = [f for f in md_files if not f.name.startswith('_')]
        
        if not md_files:
            print("未找到任何.md文件")
            return
        
        print(f"找到 {len(md_files)} 个.md文件，开始检查...")
        print()
        
        # 处理每个文件
        for filepath in md_files:
            self.process_file(filepath)
        
        # 输出统计信息
        print()
        print("=" * 60)
        print("处理完成！统计信息:")
        print(f"总文件数: {self.stats['total_files']}")
        print(f"空title文件数: {self.stats['empty_title_files']}")
        print(f"成功修复文件数: {self.stats['fixed_files']}")
        print(f"无二级标题文件数: {self.stats['no_h2_files']}")
        print(f"错误文件数: {self.stats['errors']}")
        print("=" * 60)
    
    def preview_scan(self) -> None:
        """预览扫描结果，不实际修改文件"""
        print("=" * 60)
        print("Markdown文件空title检查预览")
        print("=" * 60)
        print(f"扫描根目录: {self.root_path}")
        print("-" * 60)
        
        if not self.root_path.exists():
            print(f"错误: 根目录不存在 - {self.root_path}")
            return
        
        # 递归查找所有.md文件
        md_files = list(self.root_path.rglob("*.md"))
        md_files = [f for f in md_files if not f.name.startswith('_')]
        
        if not md_files:
            print("未找到任何.md文件")
            return
        
        print(f"找到 {len(md_files)} 个.md文件")
        print()
        
        empty_title_files = []
        
        # 检查每个文件
        for filepath in md_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = self.parse_frontmatter(content)
                if not frontmatter:
                    continue
                
                # 检查title是否为空
                if self.is_empty_title(frontmatter.get('title')):
                    h2_title = self.extract_first_h2_title(body)
                    empty_title_files.append({
                        'file': filepath,
                        'h2_title': h2_title
                    })
            
            except Exception as e:
                print(f"检查文件 {filepath.name} 时出错: {e}")
        
        # 输出预览结果
        if empty_title_files:
            print(f"发现 {len(empty_title_files)} 个空title文件:")
            print()
            
            for item in empty_title_files:
                rel_path = item['file'].relative_to(self.root_path)
                h2_title = item['h2_title']
                if h2_title:
                    print(f"📄 {rel_path}")
                    print(f"   建议title: {h2_title}")
                else:
                    print(f"📄 {rel_path}")
                    print(f"   ⚠️  未找到二级标题")
                print()
        else:
            print("✅ 未发现空title文件")


def main():
    """主函数"""
    print("Markdown空title修复工具")
    print("-" * 40)
    
    # 获取根目录
    root_dir = input("请输入根目录路径（留空使用当前目录下的content）: ").strip()
    if not root_dir:
        root_dir = "content"
    
    # 创建修复器
    fixer = TitleFixer(root_dir)
    
    # 选择操作模式
    print("\n请选择操作模式:")
    print("1. 预览检查结果（不修改文件）")
    print("2. 执行修复操作")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        fixer.preview_scan()
    elif choice == "2":
        confirm = input("确认要执行修复操作吗？这将修改文件内容 (y/N): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            fixer.scan_and_fix()
        else:
            print("操作已取消")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()