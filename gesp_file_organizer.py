#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESP文件分类整理脚本
根据Markdown文件的frontmatter元数据和文件名规则，将文件分类拷贝到对应目录
"""

import os
import re
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class GESPFileOrganizer:
    """GESP文件分类整理器"""
    
    def __init__(self, source_dir: str, target_dir: str):
        """
        初始化文件整理器
        
        Args:
            source_dir: 源目录路径
            target_dir: 目标根目录路径
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # 级别映射字典
        self.level_mapping = {
            "一级": "1", "二级": "2", "三级": "3", "四级": "4",
            "五级": "5", "六级": "6", "七级": "7", "八级": "8"
        }
        
        # 统计信息
        self.stats = {
            "processed": 0,
            "copied": 0,
            "skipped": 0,
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
    
    def extract_level_from_categories(self, categories: List[str]) -> Optional[str]:
        """
        从categories中提取级别信息
        
        Args:
            categories: 分类列表
            
        Returns:
            级别编号（如"1", "2"等）或None
        """
        if not categories:
            return None
            
        for category in categories:
            for level_name, level_num in self.level_mapping.items():
                if level_name in str(category):
                    return level_num
        return None
    
    def determine_subdirectory(self, frontmatter: Dict, filename: str) -> Optional[str]:
        """
        根据frontmatter和文件名确定子目录
        
        Args:
            frontmatter: 前置数据
            filename: 文件名
            
        Returns:
            子目录名或None
        """
        title = frontmatter.get('title', '')
        categories = frontmatter.get('categories', [])
        
        # 提取级别
        level = self.extract_level_from_categories(categories)
        if not level:
            return None
        
        # 确定子目录
        subdir = None
        
        # 检查是否为真题
        if '真题' in title:
            subdir = 'codereal'
        # 检查是否为练习
        elif '练习' in title:
            subdir = 'practice'
        # 检查文件名是否包含syllabus
        elif 'syllabus' in filename.lower():
            subdir = 'syllabus'
        # 检查文件名是否包含knowledge
        elif 'knowledge' in filename.lower():
            subdir = 'knowledge'
        else:
            # 如果都不匹配，根据其他规则或放到默认目录
            subdir = 'others'
        
        return f"{level}/{subdir}"
    
    def is_gesp_file(self, filename: str) -> bool:
        """
        检查文件是否符合GESP文件命名规则
        
        Args:
            filename: 文件名
            
        Returns:
            是否符合规则
        """
        # 检查文件名格式：yyyy-MM-dd-gesp-*.md
        pattern = r'^\d{4}-\d{2}-\d{2}-gesp-.*\.md$'
        return bool(re.match(pattern, filename))
    
    def copy_file_to_target(self, source_file: Path, relative_path: str) -> bool:
        """
        将文件拷贝到目标位置
        
        Args:
            source_file: 源文件路径
            relative_path: 相对于目标根目录的路径
            
        Returns:
            是否成功拷贝
        """
        target_path = self.target_dir / relative_path / source_file.name
        
        try:
            # 创建目标目录
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 拷贝文件
            shutil.copy2(source_file, target_path)
            
            print(f"✓ 拷贝成功: {source_file.name} -> {relative_path}/")
            return True
            
        except Exception as e:
            print(f"✗ 拷贝失败: {source_file.name} - {e}")
            return False
    
    def process_file(self, file_path: Path) -> bool:
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功处理
        """
        filename = file_path.name
        
        # 检查是否为GESP文件
        if not self.is_gesp_file(filename):
            print(f"⊝ 跳过非GESP文件: {filename}")
            self.stats["skipped"] += 1
            return False
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析frontmatter
            frontmatter, body = self.parse_frontmatter(content)
            if not frontmatter:
                print(f"⊝ 跳过无frontmatter文件: {filename}")
                self.stats["skipped"] += 1
                return False
            
            # 确定目标目录
            target_subdir = self.determine_subdirectory(frontmatter, filename)
            if not target_subdir:
                print(f"⊝ 跳过无法分类文件: {filename}")
                self.stats["skipped"] += 1
                return False
            
            # 拷贝文件
            if self.copy_file_to_target(file_path, target_subdir):
                self.stats["copied"] += 1
                return True
            else:
                self.stats["errors"] += 1
                return False
                
        except Exception as e:
            print(f"✗ 处理文件出错: {filename} - {e}")
            self.stats["errors"] += 1
            return False
    
    def organize_files(self) -> None:
        """执行文件整理"""
        print("=" * 60)
        print("GESP文件分类整理器")
        print("=" * 60)
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("-" * 60)
        
        if not self.source_dir.exists():
            print(f"错误: 源目录不存在 - {self.source_dir}")
            return
        
        # 创建目标根目录
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # 遍历源目录中的所有.md文件
        md_files = list(self.source_dir.rglob("*.md"))
        
        if not md_files:
            print("未找到任何.md文件")
            return
        
        print(f"找到 {len(md_files)} 个.md文件，开始处理...")
        print()
        
        # 处理每个文件
        for file_path in md_files:
            self.stats["processed"] += 1
            self.process_file(file_path)
        
        # 输出统计信息
        print()
        print("=" * 60)
        print("处理完成！统计信息:")
        print(f"总共处理文件: {self.stats['processed']}")
        print(f"成功拷贝文件: {self.stats['copied']}")
        print(f"跳过文件: {self.stats['skipped']}")
        print(f"错误文件: {self.stats['errors']}")
        print("=" * 60)
    
    def preview_organization(self) -> None:
        """预览文件分类结果，不实际拷贝"""
        print("=" * 60)
        print("GESP文件分类预览（仅预览，不实际拷贝）")
        print("=" * 60)
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("-" * 60)
        
        if not self.source_dir.exists():
            print(f"错误: 源目录不存在 - {self.source_dir}")
            return
        
        # 遍历源目录中的所有.md文件
        md_files = list(self.source_dir.rglob("*.md"))
        
        if not md_files:
            print("未找到任何.md文件")
            return
        
        print(f"找到 {len(md_files)} 个.md文件")
        print()
        
        organization_map = {}
        
        # 分析每个文件
        for file_path in md_files:
            filename = file_path.name
            
            if not self.is_gesp_file(filename):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, _ = self.parse_frontmatter(content)
                if not frontmatter:
                    continue
                
                target_subdir = self.determine_subdirectory(frontmatter, filename)
                if target_subdir:
                    if target_subdir not in organization_map:
                        organization_map[target_subdir] = []
                    organization_map[target_subdir].append(filename)
            
            except Exception as e:
                print(f"分析文件出错: {filename} - {e}")
        
        # 输出预览结果
        for subdir, files in sorted(organization_map.items()):
            print(f"\n📁 {subdir}/ ({len(files)} 个文件)")
            for filename in sorted(files):
                print(f"  - {filename}")
        
        print(f"\n总计将拷贝 {sum(len(files) for files in organization_map.values())} 个文件")


def main():
    """主函数"""
    print("GESP文件分类整理工具")
    print("-" * 40)
    
    # 获取源目录
    source_dir = input("请输入源目录路径: ").strip()
    if not source_dir:
        print("错误: 源目录不能为空")
        return
    
    # 获取目标目录
    target_dir = input("请输入目标根目录路径: ").strip()
    if not target_dir:
        print("错误: 目标目录不能为空")
        return
    
    # 创建整理器
    organizer = GESPFileOrganizer(source_dir, target_dir)
    
    # 选择操作模式
    print("\n请选择操作模式:")
    print("1. 预览分类结果（不实际拷贝）")
    print("2. 执行文件拷贝")
    
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        organizer.preview_organization()
    elif choice == "2":
        confirm = input("确认要执行文件拷贝吗？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            organizer.organize_files()
        else:
            print("操作已取消")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()