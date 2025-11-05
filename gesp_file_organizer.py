#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESP文件分类整理脚本
根据Markdown文件的frontmatter元数据和文件名规则，将文件分类拷贝到对应目录
"""

import os
import re
import shutil
import subprocess
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class GESPFileOrganizer:
    """GESP文件分类整理器"""
    
    def __init__(self, source_dir: str, target_dir: str, use_cache: bool = True):
        """
        初始化文件整理器
        
        Args:
            source_dir: 源目录路径
            target_dir: 目标根目录路径
            use_cache: 是否使用缓存机制
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.use_cache = use_cache
        
        # CSP文件应该迁移到与gesp同级的csp目录
        self.csp_target_dir = self.target_dir.parent / "csp" if self.target_dir.name == "gesp" else self.target_dir / "csp"
        
        # 缓存文件路径
        self.cache_file = Path(__file__).parent / ".gesp_file_cache.json"
        
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
            "existed": 0,
            "errors": 0
        }
        
        # 加载缓存
        self.cache = self.load_cache() if use_cache else {}
    
    def load_cache(self) -> Dict:
        """
        加载缓存文件
        
        Returns:
            缓存数据字典
        """
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    print(f"加载缓存文件: {self.cache_file} (共 {len(cache_data.get('existed_files', {}))} 条记录)")
                    return cache_data
        except Exception as e:
            print(f"加载缓存文件失败: {e}")
        
        return {"existed_files": {}, "last_update": ""}
    
    def save_cache(self) -> None:
        """
        保存缓存数据到文件
        """
        if not self.use_cache:
            return
            
        try:
            from datetime import datetime
            self.cache["last_update"] = datetime.now().isoformat()
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            print(f"缓存数据已保存: {self.cache_file}")
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
    
    def refresh_cache_from_filesystem(self) -> None:
        """
        从文件系统刷新缓存
        """
        print("刷新缓存：从文件系统扫描已存在文件...")
        
        existed_files = {}
        
        # 递归扫描GESP目标目录
        if self.target_dir.exists():
            for md_file in self.target_dir.rglob("*.md"):
                filename = md_file.name
                relative_path = str(md_file.relative_to(self.target_dir))
                existed_files[filename] = relative_path
        
        # 递归扫描CSP目标目录
        if self.csp_target_dir.exists():
            for md_file in self.csp_target_dir.rglob("*.md"):
                filename = md_file.name
                relative_path = str(md_file.relative_to(self.csp_target_dir))
                existed_files[filename] = relative_path
        
        # 更新缓存
        self.cache["existed_files"] = existed_files
        self.save_cache()
        
        print(f"缓存刷新完成，共扫描到 {len(existed_files)} 个文件")
    
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
    
    def extract_image_references(self, content: str) -> List[str]:
        """
        从Markdown内容中提取图片引用的相对路径
        
        Args:
            content: Markdown文件内容
            
        Returns:
            图片相对路径列表
        """
        image_paths = []
        
        # 匹配Markdown图片语法: ![alt](path) 或 ![alt](path "title")
        md_image_pattern = r'!\[.*?\]\(([^\s"]+?\.(?:png|jpg|jpeg|gif|bmp|svg|webp))(?:\s+".*?")?\)'
        image_paths.extend(re.findall(md_image_pattern, content, re.IGNORECASE))
        
        # 匹配HTML img标签: <img src="path" />
        html_img_pattern = r'<img[^>]+src=["\']([^"\']+?\.(?:png|jpg|jpeg|gif|bmp|svg|webp))["\'][^>]*/?>'
        image_paths.extend(re.findall(html_img_pattern, content, re.IGNORECASE))
        
        # 过滤掉绝对路径和URL（只保留相对路径）
        relative_image_paths = [path for path in image_paths if not path.startswith(('http://', 'https://', '/'))]
        
        return relative_image_paths
    
    def _copy_referenced_images(self, source_md_path: Path, target_md_path: Path) -> None:
        """
        拷贝Markdown文件中引用的图片文件
        
        Args:
            source_md_path: 源Markdown文件路径
            target_md_path: 目标Markdown文件路径
        """
        try:
            # 读取Markdown文件内容
            with open(source_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取图片引用
            image_paths = self.extract_image_references(content)
            
            if not image_paths:
                return
            
            print(f"    发现 {len(image_paths)} 个图片引用，正在拷贝...")
            
            # 拷贝每个图片文件
            for image_path in image_paths:
                # 构建源图片路径
                source_image_path = source_md_path.parent / image_path
                
                # 检查源图片是否存在
                if not source_image_path.exists():
                    print(f"    ⚠️  图片不存在: {source_image_path}")
                    continue
                
                # 构建目标图片路径
                target_image_path = target_md_path.parent / image_path
                
                # 创建目标图片目录
                target_image_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 拷贝图片文件
                shutil.copy2(source_image_path, target_image_path)
                print(f"    [IMG] {image_path}")
                
        except Exception as e:
            print(f"    ⚠️  拷贝图片时出错: {e}")
    
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
        
        # 注意：CSP文件的处理已移到analyze_files方法中，此处不再处理
        
        # 检查是否为必备技能文章（优先处理，不需要级别分类）
        for category in categories:
            if '必备技能' in str(category):
                return 'arsenal'
        
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
        # 检查文件名格式：yyyy-MM-dd-gesp-*.md 或包含csp-的文件
        gesp_pattern = r'^\d{4}-\d{2}-\d{2}-gesp-.*\.md$'
        csp_pattern = r'^\d{4}-\d{2}-\d{2}-.*csp-.*\.md$'
        return bool(re.match(gesp_pattern, filename) or re.match(csp_pattern, filename))
    
    def check_file_exists_in_target(self, filename: str) -> Optional[str]:
        """
        检查文件是否在目标根路径下的任何位置存在
        
        Args:
            filename: 文件名
            
        Returns:
            如果文件存在，返回相对于目标根目录的路径；否则返回None
        """
        if self.use_cache:
            # 使用缓存查找
            return self.cache.get("existed_files", {}).get(filename)
        else:
            # 直接从文件系统查找
            for existing_file in self.target_dir.rglob(filename):
                return str(existing_file.relative_to(self.target_dir))
            return None
    
    def check_file_exists_in_csp_target(self, filename: str) -> Optional[str]:
        """
        检查文件是否在CSP目标路径下的任何位置存在
        
        Args:
            filename: 文件名
            
        Returns:
            如果文件存在，返回相对于CSP目标根目录的路径；否则返回None
        """
        if self.use_cache:
            # 使用缓存查找
            return self.cache.get("existed_files", {}).get(filename)
        else:
            # 直接从文件系统查找
            for existing_file in self.csp_target_dir.rglob(filename):
                return str(existing_file.relative_to(self.csp_target_dir))
            return None
    
    def run_formatter(self, copied_files: Optional[List[str]] = None) -> bool:
        """
        运行formater.py脚本格式化目标目录中的文件
        
        Args:
            copied_files: 已拷贝文件路径列表，如果提供则只处理这些文件
        
        Returns:
            是否成功执行
        """
        try:
            # 获取脚本所在目录
            script_dir = Path(__file__).parent
            formatter_script = script_dir / "formater.py"
            
            # 检查formater.py是否存在
            if not formatter_script.exists():
                print(f"❗ 警告: formater.py 脚本不存在：{formatter_script}")
                return False
            
            print("\n" + "=" * 60)
            print("🛠️  开始运行 formater.py 格式化脚本...")
            print("=" * 60)
            
            # 构建命令
            cmd = [sys.executable, str(formatter_script)]
            
            if copied_files:
                # 如果有指定文件列表，将文件路径作为命令行参数传递
                cmd.extend(copied_files)
                print(f"对 {len(copied_files)} 个已拷贝的文件进行格式化...")
                
                # 执行脚本（不需要交互输入）
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=script_dir,
                    encoding='utf-8',
                    errors='replace'  # 添加错误处理
                )
            else:
                # 原始逗辑：传递目标目录 + 确认执行
                # 对于CSP文件，我们需要分别处理GESP和CSP目录
                relative_target = self.target_dir.relative_to(script_dir)
                csp_relative_target = self.csp_target_dir.relative_to(script_dir)
                
                # 先处理GESP目录
                input_data = f"{relative_target}\ny\n"
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    cwd=script_dir,
                    encoding='utf-8',
                    errors='replace'  # 添加错误处理
                )
                
                # 输出GESP目录处理结果
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(f"⚠️  GESP目录警告信息:\n{result.stderr}")
                
                # 再处理CSP目录
                input_data = f"{csp_relative_target}\ny\n"
                result = subprocess.run(
                    cmd,
                    input=input_data,
                    text=True,
                    capture_output=True,
                    cwd=script_dir,
                    encoding='utf-8',
                    errors='replace'  # 添加错误处理
                )
            
            # 输出结果
            if result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print(f"⚠️  警告信息:\n{result.stderr}")
            
            if result.returncode == 0:
                print("\n✅ formater.py 脚本执行成功！")
                return True
            else:
                print(f"\n❌ formater.py 脚本执行失败，退出码: {result.returncode}")
                return False
                
        except Exception as e:
            print(f"\n❌ 运行formater.py时出错: {e}")
            return False
    
    def analyze_files(self) -> Tuple[Dict[str, List[Tuple[Path, str]]], Dict[str, List[str]]]:
        """
        分析所有文件，确定拷贝计划和已存在文件
        
        Returns:
            Tuple[copy_plan, existed_files_map]
            copy_plan: {target_subdir: [(source_file_path, filename), ...]}
            existed_files_map: {existing_dir: [filename_info, ...]}
        """
        copy_plan = {}
        existed_files_map = {}
        
        # 遍历源目录中的所有.md文件
        md_files = list(self.source_dir.rglob("*.md"))
        
        for file_path in md_files:
            filename = file_path.name
            
            # 检查是否为GESP文件或CSP相关文件
            if not self.is_gesp_file(filename):
                continue
            
            # 对于CSP文件，使用特殊处理逻辑
            is_csp_file = False
            if '-csp-' in filename.lower():
                is_csp_file = True
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, _ = self.parse_frontmatter(content)
                if not frontmatter:
                    continue
                
                # 对于CSP文件，使用特殊的目标目录逻辑
                if is_csp_file:
                    target_subdir = 'others'  # 默认CSP目录
                    
                    # 检查是否为CSP XL真题
                    category_str = ''.join(str(cat) for cat in frontmatter.get('categories', []))
                    title = frontmatter.get('title', '')
                    
                    if 'xl' in category_str.lower() and '真题' in title:
                        target_subdir = 'xl/realexam'
                    
                    # CSP文件使用专门的目标目录
                    csp_target_path = self.csp_target_dir / target_subdir
                else:
                    target_subdir = self.determine_subdirectory(frontmatter, filename)
                
                if target_subdir:
                    # 检查文件是否在目标根路径下的任何位置已存在
                    if is_csp_file:
                        # 对于CSP文件，检查在csp目录下是否存在
                        existing_path = self.check_file_exists_in_csp_target(filename)
                    else:
                        existing_path = self.check_file_exists_in_target(filename)
                    
                    if existing_path:
                        # 文件已存在，记录到已存在文件映射
                        existing_dir = str(Path(existing_path).parent) if Path(existing_path).parent != Path('.') else 'root'
                        if existing_dir not in existed_files_map:
                            existed_files_map[existing_dir] = []
                        existed_files_map[existing_dir].append(f"{filename} (存在于: {existing_path})")
                    else:
                        # 文件不存在，加入拷贝计划
                        if is_csp_file:
                            # CSP文件使用专门的键
                            csp_key = f"_csp/{target_subdir}"
                            if csp_key not in copy_plan:
                                copy_plan[csp_key] = []
                            copy_plan[csp_key].append((file_path, filename))
                        else:
                            if target_subdir not in copy_plan:
                                copy_plan[target_subdir] = []
                            copy_plan[target_subdir].append((file_path, filename))
            
            except Exception as e:
                print(f"分析文件出错: {filename} - {e}")
        
        return copy_plan, existed_files_map
    
    def execute_copy_plan(self, copy_plan: Dict[str, List[Tuple[Path, str]]]) -> List[str]:
        """
        执行拷贝计划
        
        Args:
            copy_plan: 拷贝计划字典 {target_subdir: [(source_file_path, filename), ...]}
        
        Returns:
            成功拷贝的文件路径列表
        """
        total_to_copy = sum(len(files) for files in copy_plan.values())
        copied_count = 0
        error_count = 0
        copied_files = []  # 记录成功拷贝的文件路径
        
        print(f"开始执行拷贝计划，共 {total_to_copy} 个文件...")
        print()
        
        for target_subdir, files in copy_plan.items():
            # 检查是否为CSP文件
            if target_subdir.startswith("_csp/"):
                # 处理CSP文件
                csp_subdir = target_subdir[len("_csp/"):]
                print(f"📁 拷贝到 CSP目录 {csp_subdir}/ ({len(files)} 个文件)")
                
                for source_file_path, filename in files:
                    try:
                        target_path = self.csp_target_dir / csp_subdir / filename
                        
                        # 创建目标目录
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 拷贝文件
                        shutil.copy2(source_file_path, target_path)
                        
                        print(f"  [OK] {filename}")
                        copied_count += 1
                        copied_files.append(str(target_path))  # 记录成功拷贝的文件路径
                        
                        # 如果是Markdown文件，提取并拷贝图片
                        if filename.endswith('.md'):
                            self._copy_referenced_images(source_file_path, target_path)
                        
                        # 更新缓存
                        if self.use_cache:
                            relative_path = str(target_path.relative_to(self.csp_target_dir))
                            self.cache["existed_files"][filename] = relative_path
                        
                    except Exception as e:
                        print(f"  [ERROR] {filename} - 拷贝失败: {e}")
                        error_count += 1
            else:
                # 处理普通GESP文件
                print(f"📁 拷贝到 {target_subdir}/ ({len(files)} 个文件)")
                
                for source_file_path, filename in files:
                    try:
                        target_path = self.target_dir / target_subdir / filename
                        
                        # 创建目标目录
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 拷贝文件
                        shutil.copy2(source_file_path, target_path)
                        
                        print(f"  [OK] {filename}")
                        copied_count += 1
                        copied_files.append(str(target_path))  # 记录成功拷贝的文件路径
                        
                        # 如果是Markdown文件，提取并拷贝图片
                        if filename.endswith('.md'):
                            self._copy_referenced_images(source_file_path, target_path)
                        
                        # 更新缓存
                        if self.use_cache:
                            relative_path = str(target_path.relative_to(self.target_dir))
                            self.cache["existed_files"][filename] = relative_path
                        
                    except Exception as e:
                        print(f"  [ERROR] {filename} - 拷贝失败: {e}")
                        error_count += 1
            
            print()
        
        # 更新统计信息
        self.stats["copied"] = copied_count
        self.stats["errors"] = error_count
        self.stats["processed"] = total_to_copy
        
        print("=" * 60)
        print("文件拷贝完成！统计信息:")
        print(f"计划拷贝文件: {total_to_copy}")
        print(f"成功拷贝文件: {copied_count}")
        print(f"拷贝失败文件: {error_count}")
        print("=" * 60)
        
        # 保存缓存
        if self.use_cache and copied_count > 0:
            self.save_cache()
        
        return copied_files
    
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
        
        # 分析文件，获取拷贝计划
        copy_plan, existed_files_map = self.analyze_files()
        
        total_new_files = sum(len(files) for files in copy_plan.values())
        total_existed_files = sum(len(files) for files in existed_files_map.values())
        total_files = total_new_files + total_existed_files
        
        if total_files == 0:
            print("未找到任何GESP文件")
            return
        
        print(f"找到 {total_files} 个GESP文件，其中 {total_new_files} 个需要拷贝，{total_existed_files} 个已存在")
        
        if total_new_files == 0:
            print("没有需要拷贝的新文件")
            self.stats["processed"] = total_files
            self.stats["existed"] = total_existed_files
            return
        
        print()
        
        # 执行拷贝计划
        copied_files = self.execute_copy_plan(copy_plan)
        
        # 设置已存在文件的统计
        self.stats["existed"] = total_existed_files
        
        # 如果有文件被拷贝，自动运行格式化脚本
        if self.stats['copied'] > 0 and copied_files:
            print(f"\n🎯 检测到 {self.stats['copied']} 个文件被成功拷贝，将自动运行格式化脚本...")
            
            # 询问用户是否要运行格式化脚本
            run_formatter = input("是否要运行 formater.py 格式化拷贝的文件头？(Y/n): ").strip().lower() or "y"
            
            if run_formatter not in ['n', 'no', 'N', 'NO', '否']:
                # 运行格式化脚本，传递已拷贝的文件列表
                if self.run_formatter(copied_files):
                    print("\n🎉 文件拷贝和格式化流程全部完成！")
                else:
                    print("\n⚠️ 文件拷贝完成，但格式化过程中出现了问题。")
            else:
                print("\n✅ 文件拷贝完成（跳过格式化）。")
        else:
            print("\n💡 没有新文件被拷贝，无需运行格式化脚本。")
    
    def preview_organization(self) -> Tuple[Dict[str, List[Tuple[Path, str]]], Dict[str, List[str]]]:
        """预览文件分类结果，不实际拷贝，默认只显示将被拷贝的文件。返回拷贝计划供后续执行使用"""
        print("=" * 60)
        print("GESP文件分类预览")
        print("=" * 60)
        print(f"源目录: {self.source_dir}")
        print(f"目标目录: {self.target_dir}")
        print("-" * 60)
        
        if not self.source_dir.exists():
            print(f"错误: 源目录不存在 - {self.source_dir}")
            return {}, {}
        
        # 创建目标根目录（如果不存在）
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        # 分析文件
        copy_plan, existed_files_map = self.analyze_files()
        
        total_new_files = sum(len(files) for files in copy_plan.values())
        total_existed_files = sum(len(files) for files in existed_files_map.values())
        total_files = total_new_files + total_existed_files
        
        if total_files == 0:
            print("未找到任何GESP文件")
            return {}, {}
        
        print(f"找到 {total_files} 个GESP文件")
        print()
        
        # 输出预览结果 - 默认只显示将被拷贝的文件
        if copy_plan:
            print(f"📝 将被拷贝的新文件 ({total_new_files} 个):")
            for subdir, files in sorted(copy_plan.items()):
                # 检查是否为CSP文件
                if subdir.startswith("_csp/"):
                    csp_subdir = subdir[len("_csp/"):]
                    print(f"\n📁 [CSP] {csp_subdir}/ ({len(files)} 个新文件)")
                else:
                    print(f"\n📁 {subdir}/ ({len(files)} 个新文件)")
                for file_path, filename in sorted(files, key=lambda x: x[1]):
                    print(f"  [OK] {filename}")
        else:
            print("🚀 没有需要拷贝的新文件")
        
        # 询问用户是否需要查看已存在的文件
        if existed_files_map:
            print(f"\n🔍 发现 {total_existed_files} 个已存在的文件（将被跳过）")
            show_existed = input("是否需要查看已存在文件的详细信息？(y/N): ").strip().lower()
            
            if show_existed in ['y', 'yes', 'Y', 'YES', '是', 'y', 'Y']:
                print(f"\n📋 已存在的文件（将被跳过）:")
                for subdir, files in sorted(existed_files_map.items()):
                    print(f"\n📁 {subdir}/ ({len(files)} 个已存在文件)")
                    for filename in sorted(files):
                        print(f"  ⊝ {filename}")
        
        print(f"\n📊 统计信息:")
        print(f"总共GESP文件: {total_files}")
        print(f"将被拷贝: {total_new_files}")
        print(f"已存在（跳过）: {total_existed_files}")
        
        return copy_plan, existed_files_map


def main():
    """主函数"""
    print("GESP文件分类整理工具")
    print("-" * 40)
    
    # 默认路径
    default_source = r"D:\MyCode\lihongzheshuai.github.io\_posts"
    default_target = r"D:\MyCode\hugo-site\yummy-dad-code-hextra\content\gesp"
    
    # 获取源目录
    print(f"默认源目录: {default_source}")
    source_dir = input("请输入源目录路径（直接回车使用默认值）: ").strip()
    if not source_dir:
        source_dir = default_source
        print(f"使用默认源目录: {source_dir}")
    
    # 获取目标目录
    print(f"\n默认目标目录: {default_target}")
    target_dir = input("请输入目标根目录路径（直接回车使用默认值）: ").strip()
    if not target_dir:
        target_dir = default_target
        print(f"使用默认目标目录: {target_dir}")
    
    # 创建整理器
    organizer = GESPFileOrganizer(source_dir, target_dir)
    
    # 缓存选项
    print("\n缓存设置:")
    print("1. 使用缓存（推荐，提高性能）")
    print("2. 刷新缓存并使用")
    print("3. 不使用缓存（直接扫描文件系统）")
    
    cache_choice = input("请选择缓存模式 (1/2/3, 默认1): ").strip() or "1"
    
    if cache_choice == "2":
        organizer.refresh_cache_from_filesystem()
    elif cache_choice == "3":
        organizer.use_cache = False
        print("已禁用缓存，将直接扫描文件系统")
    else:
        print(f"使用缓存模式（缓存文件: {organizer.cache_file}）")
    
    # 选择操作模式
    print("\n请选择操作模式:")
    print("1. 直接执行文件拷贝（默认）")
    print("2. 预览后再执行拷贝")
    
    choice = input("请输入选择 (1/2, 默认1): ").strip() or "1"
    
    if choice == "1":
        # 直接执行拷贝
        organizer.organize_files()
    elif choice == "2":
        # 预览后询问是否执行
        copy_plan, existed_files_map = organizer.analyze_files()
        
        total_new_files = sum(len(files) for files in copy_plan.values())
        total_existed_files = sum(len(files) for files in existed_files_map.values())
        total_files = total_new_files + total_existed_files
        
        if total_files == 0:
            print("未找到任何GESP文件")
            return
        
        print(f"找到 {total_files} 个GESP文件")
        print()
        
        # 输出预览结果
        if copy_plan:
            print(f"📝 将被拷贝的新文件 ({total_new_files} 个):")
            for subdir, files in sorted(copy_plan.items()):
                # 检查是否为CSP文件
                if subdir.startswith("_csp/"):
                    csp_subdir = subdir[len("_csp/"):]
                    print(f"\n📁 [CSP] {csp_subdir}/ ({len(files)} 个新文件)")
                else:
                    print(f"\n📁 {subdir}/ ({len(files)} 个新文件)")
                for file_path, filename in sorted(files, key=lambda x: x[1]):
                    print(f"  [OK] {filename}")
        else:
            print("🚀 没有需要拷贝的新文件")
        
        print(f"\n📊 统计信息:")
        print(f"总共GESP文件: {total_files}")
        print(f"将被拷贝: {total_new_files}")
        print(f"已存在（跳过）: {total_existed_files}")
        
        if total_new_files > 0:
            print("\n" + "=" * 60)
            execute = input("🚀 是否要执行上述文件拷贝操作？(Y/n): ").strip().lower() or "y"
            
            if execute not in ['n', 'no', 'N', 'NO', '否']:
                print("\n开始执行文件拷贝...")
                copied_files = organizer.execute_copy_plan(copy_plan)
                
                organizer.stats["existed"] = total_existed_files
                
                # 自动运行格式化脚本
                if organizer.stats['copied'] > 0 and copied_files:
                    print(f"\n🎯 检测到 {organizer.stats['copied']} 个文件被成功拷贝，将自动运行格式化脚本...")
                    
                    run_formatter = input("是否要运行 formater.py 格式化拷贝的文件头？(Y/n): ").strip().lower() or "y"
                    
                    if run_formatter not in ['n', 'no', 'N', 'NO', '否']:
                        if organizer.run_formatter(copied_files):
                            print("\n🎉 文件拷贝和格式化流程全部完成！")
                        else:
                            print("\n⚠️ 文件拷贝完成，但格式化过程中出现了问题。")
                    else:
                        print("\n✅ 文件拷贝完成（跳过格式化）。")
                else:
                    print("\n💡 没有新文件被拷贝，无需运行格式化脚本。")
            else:
                print("✅ 操作已取消，仅完成预览。")
        else:
            print("\n💡 没有需要拷贝的新文件，无需执行拷贝操作。")
    else:
        print("无效选择")


if __name__ == "__main__":
    main()