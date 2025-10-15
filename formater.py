import os
import re
import sys
from datetime import datetime
import yaml
from pathlib import Path
from collections import defaultdict
from typing import Optional
import locale

def remove_include_lines(body):
    """删除包含'{% include '的行"""
    if not body:
        return body
    
    # 使用正则表达式删除包含'{% include '的行
    lines = body.split('\n')
    filtered_lines = [line for line in lines if '{% include ' not in line]
    return '\n'.join(filtered_lines)

def parse_frontmatter(content):
    """解析Markdown文件的frontmatter"""
    # 匹配frontmatter（用---包围的YAML内容）
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not match:
        return None, content
    
    frontmatter_str = match.group(1)
    body = match.group(2)
    
    try:
        frontmatter = yaml.safe_load(frontmatter_str)
        return frontmatter, body
    except yaml.YAMLError:
        return None, content

def format_frontmatter(frontmatter):
    """格式化frontmatter为YAML字符串"""
    # 定义字段顺序
    field_order = ['layout', 'title', 'date', 'author', 'comments', 'tags', 'categories', 'slug', 'type', 'weight']
    
    # 按顺序构建有序的frontmatter
    ordered_frontmatter = {}
    for field in field_order:
        if field in frontmatter:
            ordered_frontmatter[field] = frontmatter[field]
    
    # 添加其他未在顺序中的字段
    for key, value in frontmatter.items():
        if key not in ordered_frontmatter:
            ordered_frontmatter[key] = value
    
    # 转换为YAML字符串
    yaml_str = yaml.dump(ordered_frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return yaml_str.rstrip()

def extract_first_h2_title(body: str) -> Optional[str]:
    """
    提取Markdown文档中的第一个二级标题内容
    
    Args:
        body: Markdown文档主体内容
        
    Returns:
        第一个二级标题的内容，去除标记符号和多余空格
    """
    if not body:
        return None
    
    # 匹配第一个二级标题
    match = re.search(r'^##\s+(.+?)$', body, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # 去除可能的额外标记符号
        title = re.sub(r'[#\s]+$', '', title).strip()
        return title if title else None
    
    return None

def clean_title(title):
    """清理title中的GESP前缀"""
    if not title:
        return title
    
    # 删除开头的【GESP】C++X级XX字样
    patterns = [
        r'^【GESP】C\+\+\s*[一二三四五六七八1-8]级.*?[，,]?\s*',
        r'^【GESP】\s*[一二三四五六七八1-8]级.*?[，,]?\s*'
    ]
    
    original_title = title
    for pattern in patterns:
        title = re.sub(pattern, '', title)
    
    # 如果清理后标题为空，则返回原标题
    cleaned_title = title.strip()
    result = cleaned_title if cleaned_title else original_title
    return result

def determine_file_folder_type(filepath: str) -> str:
    """
    根据文件路径判断文件所在的文件夹类型
    
    Args:
        filepath: 文件路径
        
    Returns:
        文件夹类型: 'syllabus', 'practice', 'other'
    """
    path_parts = Path(filepath).parts
    
    for part in path_parts:
        if 'syllabus' in part.lower():
            return 'syllabus'
        elif 'practice' in part.lower():
            return 'practice'
    
    return 'other'

def extract_slug_from_filename(filename):
    # 匹配格式：yyyy-MM-dd-...
    match = re.match(r'^\d{4}-\d{2}-\d{2}-(.+)\.md$', filename)
    if match:
        return match.group(1)
    return filename.replace('.md', '')

def parse_date_for_sorting(date_str):
    """解析日期用于排序"""
    if not date_str:
        return datetime.min
    
    # 处理不同的日期格式
    date_patterns = [
        (r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S'),
        (r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', '%Y-%m-%d %H:%M'),
        (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d')
    ]
    
    for pattern, fmt in date_patterns:
        match = re.search(pattern, str(date_str))
        if match:
            try:
                if len(match.groups()) == 2:
                    date_part = f"{match.group(1)} {match.group(2)}" if ' ' in fmt else f"{match.group(1)}T{match.group(2)}"
                    return datetime.strptime(date_part, fmt)
                else:
                    return datetime.strptime(match.group(1), fmt)
            except ValueError:
                continue
    
    return datetime.min

def convert_date_format(date_str):
    if not date_str:
        return None
    
    # 处理不同的日期格式
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s*(\+\d{4})?',  # 2024-11-03 10:00 +0800
        r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(\+\d{4})?', # 2024-11-02T20:00:00+0800
        r'(\d{4}-\d{2}-\d{2})',  # 2024-11-03
    ]
    
    for pattern in date_patterns:
        match = re.match(pattern, str(date_str))
        if match:
            date_part = match.group(1)
            time_part = match.group(2) if len(match.groups()) > 1 and match.group(2) else "20:00:00"
            timezone = match.group(3) if len(match.groups()) > 2 and match.group(3) else "+0800"
            
            # 如果时间部分只有HH:MM格式，补充秒数
            if len(time_part) == 5:
                time_part += ":00"
            
            return f"{date_part}T{time_part}{timezone}"
    
    return str(date_str)

def collect_files_by_directory(root_path):
    """递归收集所有.md文件，按目录分组"""
    files_by_dir = defaultdict(list)
    
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.md') and not file.startswith('_'):
                filepath = os.path.join(root, file)
                rel_dir = os.path.relpath(root, root_path)
                files_by_dir[rel_dir].append((file, filepath))
    
    return files_by_dir

def assign_weights_by_date(files_info, target_dir_path: str):
    """根据日期为文件分配weight，在目标文件夹最大weight基础上自增"""
    # 获取目标文件夹中已存在文件的最大weight
    max_existing_weight = get_max_weight_in_directory(target_dir_path)
    
    # 按日期排序，日期相同则按文件名排序
    sorted_files = sorted(files_info, key=lambda x: (x[3], x[0]))  # x[3]是解析后的日期，x[0]是文件名
    
    for i, file_info in enumerate(sorted_files, 1):
        file_info[2]['weight'] = max_existing_weight + i  # 在已存在最大weight基础上自增
    
    return sorted_files

def get_max_weight_in_directory(directory_path: str) -> int:
    """
    获取目标文件夹中已存在文件的最大weight值
    
    Args:
        directory_path: 目标文件夹路径
        
    Returns:
        最大weight值，如果没有文件则返回0
    """
    max_weight = 0
    directory = Path(directory_path)
    
    if not directory.exists():
        return 0
    
    # 遍历目标文件夹中的所有md文件
    for md_file in directory.glob("*.md"):
        try:
            content, _ = read_file_with_encoding(str(md_file))
            frontmatter, _ = parse_frontmatter(content)
            
            if frontmatter and 'weight' in frontmatter:
                weight = frontmatter['weight']
                if isinstance(weight, int) and weight > max_weight:
                    max_weight = weight
        except Exception:
            # 忽略读取错误的文件
            continue
    
    return max_weight

def read_file_with_encoding(filepath):
    """尝试用多种编码读取文件"""
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1', 'cp1252']
    
    # 获取系统默认编码
    default_encoding = locale.getpreferredencoding()
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
                # 使用兼容性更好的输出方式
                print_safe(f"  成功用 {encoding} 编码读取文件")
                return content, encoding
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print_safe(f"  用 {encoding} 编码读取时出现其他错误: {e}")
            continue
    
    # 如果所有编码都失败，尝试用二进制模式读取并替换无效字符
    try:
        with open(filepath, 'rb') as f:
            raw_content = f.read()
            content = raw_content.decode('utf-8', errors='replace')
            print_safe(f"  警告：使用UTF-8编码并替换无效字符读取文件")
            return content, 'utf-8-with-errors'
    except Exception as e:
        raise Exception(f"无法读取文件 {filepath}: {e}")

def process_specific_files(file_paths):
    """
    处理指定的Markdown文件列表
    
    Args:
        file_paths: 文件路径列表
    """
    if not file_paths:
        print_safe("没有指定要处理的文件")
        return
    
    print_safe("=" * 60)
    print_safe("处理指定文件的frontmatter格式化")
    print_safe("=" * 60)
    
    total_processed = 0
    total_updated = 0
    
    for filepath in file_paths:
        filepath = Path(filepath)
        
        if not filepath.exists():
            print_safe(f"文件不存在，跳过: {filepath}")
            continue
            
        if not filepath.suffix.lower() == '.md':
            print_safe(f"非Markdown文件，跳过: {filepath}")
            continue
        
        try:
            content, used_encoding = read_file_with_encoding(str(filepath))
            
            frontmatter, body = parse_frontmatter(content)
            if frontmatter is None:
                print_safe(f"跳过文件 {filepath.name}: 无法解析frontmatter")
                continue
            
            # 删除包含'{% include '的行
            body = remove_include_lines(body)
            
            total_processed += 1
            updated = False
            
            print_safe(f"处理文件: {filepath.name}")
            
            # 1. 修改date格式
            if 'date' in frontmatter:
                new_date = convert_date_format(frontmatter['date'])
                if new_date and new_date != frontmatter['date']:
                    frontmatter['date'] = new_date
                    print_safe(f"  更新date: {new_date}")
                    updated = True
            
            # 2. 根据文件夹类型处理title字段
            folder_type = determine_file_folder_type(str(filepath))
            
            if 'title' in frontmatter:
                if folder_type == 'syllabus':
                    # syllabus文件夹：清理GESP前缀
                    original_title = frontmatter['title']
                    cleaned_title = clean_title(original_title)
                    if cleaned_title != original_title:
                        frontmatter['title'] = cleaned_title
                        print_safe(f"  更新title(清理GESP前缀): {original_title} -> {cleaned_title}")
                        updated = True
                elif folder_type == 'practice':
                    # practice文件夹：使用第一个二级标题
                    h2_title = extract_first_h2_title(body)
                    if h2_title and h2_title != frontmatter['title']:
                        original_title = frontmatter['title']
                        frontmatter['title'] = h2_title
                        print_safe(f"  更新title(使用二级标题): {original_title} -> {h2_title}")
                        updated = True
                else:
                    # 其他文件夹：清理GESP前缀
                    original_title = frontmatter['title']
                    cleaned_title = clean_title(original_title)
                    if cleaned_title != original_title:
                        frontmatter['title'] = cleaned_title
                        print_safe(f"  更新title(清理GESP前缀): {original_title} -> {cleaned_title}")
                        updated = True
            
            # 3. 添加或更新slug字段
            slug = extract_slug_from_filename(filepath.name)
            if 'slug' not in frontmatter or frontmatter['slug'] != slug:
                frontmatter['slug'] = slug
                print_safe(f"  设置slug: {slug}")
                updated = True
            
            # 4. 添加或更新type字段
            if 'type' not in frontmatter or frontmatter['type'] != 'docs':
                frontmatter['type'] = 'docs'
                print_safe(f"  设置type: docs")
                updated = True
            
            # 5. 设置weight（根据目标文件夹中的最大weight+1）
            if 'weight' not in frontmatter:
                target_dir = filepath.parent
                max_weight = get_max_weight_in_directory(str(target_dir))
                new_weight = max_weight + 1
                frontmatter['weight'] = new_weight
                print_safe(f"  设置weight: {new_weight} (目标文件夹最大weight: {max_weight})")
                updated = True
            
            # 如果有更新，写入文件
            if updated:
                # 格式化frontmatter
                formatted_frontmatter = format_frontmatter(frontmatter)
                
                # 重新构建文件内容
                new_content = f"---\n{formatted_frontmatter}\n---\n{body}"
                
                # 写入文件，优先使用UTF-8编码
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print_safe(f"  [OK] 文件更新成功（UTF-8编码）")
                    total_updated += 1
                except UnicodeEncodeError:
                    # 如果UTF-8编码失败，尝试原始编码
                    try:
                        with open(filepath, 'w', encoding=used_encoding if used_encoding != 'utf-8-with-errors' else 'utf-8') as f:
                            f.write(new_content)
                        print_safe(f"  [OK] 文件更新成功（{used_encoding}编码）")
                        total_updated += 1
                    except Exception as e:
                        print_safe(f"  [ERROR] 写入文件时出错: {e}")
                except Exception as e:
                    print_safe(f"  [ERROR] 写入文件时出错: {e}")
            else:
                print_safe(f"  - 文件无需更新")
                
        except Exception as e:
            print_safe(f"处理文件 {filepath.name} 时出错: {e}")
            continue
    
    print_safe("=" * 60)
    print_safe(f"指定文件处理完成！")
    print_safe(f"总计处理文件: {total_processed}")
    print_safe(f"更新文件: {total_updated}")
    print_safe("=" * 60)

def process_markdown_files(root_path):
    """递归处理指定根目录下的所有Markdown文件"""
    if not os.path.exists(root_path):
        print_safe(f"目录 {root_path} 不存在")
        return
    
    print_safe(f"开始递归扫描目录: {root_path}")
    
    # 收集所有.md文件，按目录分组
    files_by_dir = collect_files_by_directory(root_path)
    
    total_processed = 0
    total_updated = 0
    
    for rel_dir, files in files_by_dir.items():
        if not files:
            continue
            
        print_safe(f"\n处理目录: {rel_dir} ({len(files)} 个文件)")
        print_safe("-" * 50)
        
        # 收集当前目录下所有文件的信息
        files_info = []
        
        for filename, filepath in files:
            try:
                content, used_encoding = read_file_with_encoding(filepath)
                
                frontmatter, body = parse_frontmatter(content)
                if frontmatter is None:
                    print_safe(f"跳过文件 {filename}: 无法解析frontmatter")
                    continue
                
                # 删除包含'{% include '的行
                body = remove_include_lines(body)
                
                # 解析日期用于排序
                date_obj = parse_date_for_sorting(frontmatter.get('date', ''))
                
                files_info.append([filename, filepath, frontmatter, date_obj, body, used_encoding])
                
            except Exception as e:
                print_safe(f"读取文件 {filename} 时出错: {e}")
                continue
        
        if not files_info:
            print_safe(f"目录 {rel_dir} 中没有可处理的文件")
            continue
        
        # 按日期排序并分配weight
        target_dir_path = os.path.join(root_path, rel_dir)
        sorted_files = assign_weights_by_date(files_info, target_dir_path)
        
        # 处理每个文件
        dir_updated = 0
        for filename, filepath, frontmatter, date_obj, body, used_encoding in sorted_files:
            total_processed += 1
            updated = False
            
            print_safe(f"处理文件: {filename}")
            
            # 1. 修改date格式
            if 'date' in frontmatter:
                new_date = convert_date_format(frontmatter['date'])
                if new_date and new_date != frontmatter['date']:
                    frontmatter['date'] = new_date
                    print_safe(f"  更新date: {new_date}")
                    updated = True
            
            # 2. 清理title中GESP前缀
            if 'title' in frontmatter:
                original_title = frontmatter['title']
                cleaned_title = clean_title(original_title)
                if cleaned_title != original_title:
                    frontmatter['title'] = cleaned_title
                    print_safe(f"  更新title: {original_title} -> {cleaned_title}")
                    updated = True
            
            # 3. 添加或更新slug字段
            slug = extract_slug_from_filename(filename)
            if 'slug' not in frontmatter or frontmatter['slug'] != slug:
                frontmatter['slug'] = slug
                print_safe(f"  设置slug: {slug}")
                updated = True
            
            # 4. 添加或更新type字段
            if 'type' not in frontmatter or frontmatter['type'] != 'docs':
                frontmatter['type'] = 'docs'
                print_safe(f"  设置type: docs")
                updated = True
            
            # 5. weight已在assign_weights_by_date中设置
            print_safe(f"  设置weight: {frontmatter['weight']}")
            
            # 如果有更新，写入文件
            if updated or 'weight' not in frontmatter:
                # 格式化frontmatter
                formatted_frontmatter = format_frontmatter(frontmatter)
                
                # 重新构建文件内容
                new_content = f"---\n{formatted_frontmatter}\n---\n{body}"
                
                # 写入文件，优先使用UTF-8编码
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print_safe(f"  [OK] 文件更新成功（UTF-8编码）")
                    dir_updated += 1
                    total_updated += 1
                except UnicodeEncodeError:
                    # 如果UTF-8编码失败，尝试原始编码
                    try:
                        with open(filepath, 'w', encoding=used_encoding if used_encoding != 'utf-8-with-errors' else 'utf-8') as f:
                            f.write(new_content)
                        print_safe(f"  [OK] 文件更新成功（{used_encoding}编码）")
                        dir_updated += 1
                        total_updated += 1
                    except Exception as e:
                        print_safe(f"  [ERROR] 写入文件时出错: {e}")
                except Exception as e:
                    print_safe(f"  [ERROR] 写入文件时出错: {e}")
            else:
                print_safe(f"  - 文件无需更新")
        
        print_safe(f"目录 {rel_dir} 处理完成: {dir_updated}/{len(sorted_files)} 个文件被更新")
    
    print_safe(f"\n总计处理 {total_processed} 个文件，更新 {total_updated} 个文件")

def print_safe(text):
    """安全打印函数，避免Windows控制台编码问题"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果出现编码错误，使用ASCII安全的输出
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)
    except Exception:
        # 其他异常情况，使用repr输出
        print(repr(text))

def main():
    """主函数"""
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 如果有参数，将其作为文件路径列表处理
        file_paths = sys.argv[1:]
        print_safe(f"接收到 {len(file_paths)} 个文件路径参数")
        process_specific_files(file_paths)
        return
    
    print_safe("======================================")
    print_safe("Markdown文件frontmatter格式化工具")
    print_safe("======================================")
    print_safe("功能：")
    print_safe("1. 递归查找所有.md文件")
    print_safe("2. 格式化frontmatter元数据")
    print_safe("3. 清理title中GESP前缀")
    print_safe("4. 按日期排序并分配weight")
    print_safe("5. 删除包含'{% include '的行")
    print_safe("======================================")
    
    # 指定要处理的目录
    target_directory = input("请输入要处理的根目录路径（相对于项目根目录，留空使用默认）: ").strip()
    
    if not target_directory:
        target_directory = "content"  # 默认目录
    
    # 构建完整路径
    base_dir = Path(__file__).parent
    full_directory = base_dir / target_directory
    
    print_safe(f"处理根目录: {full_directory}")
    
    # 确认操作
    confirm = input("确认开始处理吗？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print_safe("操作已取消")
        return
    
    print_safe("=" * 60)
    
    process_markdown_files(str(full_directory))
    
    print_safe("=" * 60)
    print_safe("处理完成！")

if __name__ == "__main__":
    main()