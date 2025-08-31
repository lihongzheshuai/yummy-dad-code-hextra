import os
import re
import os
from datetime import datetime
import yaml
from pathlib import Path
from collections import defaultdict

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

def clean_title(title):
    """清理title中的GESP前缀"""
    if not title:
        return title
    
    # 删除开头的【GESP】C++X级XX字样
    patterns = [
        r'^【GESP】C\+\+[一二三四五六七八]级[^，,]*[，,]?\s*',
        r'^【GESP】[一二三四五六七八]级[^，,]*[，,]?\s*',
        r'^【GESP】C\+\+[1-8]级[^，,]*[，,]?\s*',
        r'^【GESP】[1-8]级[^，,]*[，,]?\s*'
    ]
    
    for pattern in patterns:
        title = re.sub(pattern, '', title)
    
    return title.strip()

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

def assign_weights_by_date(files_info):
    """根据日期为文件分配weight，日期最早的weight=1"""
    # 按日期排序，日期相同则按文件名排序
    sorted_files = sorted(files_info, key=lambda x: (x[3], x[0]))  # x[3]是解析后的日期，x[0]是文件名
    
    for i, file_info in enumerate(sorted_files, 1):
        file_info[2]['weight'] = i  # 设置weight从1开始
    
    return sorted_files

def process_markdown_files(root_path):
    """递归处理指定根目录下的所有Markdown文件"""
    if not os.path.exists(root_path):
        print(f"目录 {root_path} 不存在")
        return
    
    print(f"开始递归扫描目录: {root_path}")
    
    # 收集所有.md文件，按目录分组
    files_by_dir = collect_files_by_directory(root_path)
    
    total_processed = 0
    total_updated = 0
    
    for rel_dir, files in files_by_dir.items():
        if not files:
            continue
            
        print(f"\n处理目录: {rel_dir} ({len(files)} 个文件)")
        print("-" * 50)
        
        # 收集当前目录下所有文件的信息
        files_info = []
        
        for filename, filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = parse_frontmatter(content)
                if frontmatter is None:
                    print(f"跳过文件 {filename}: 无法解析frontmatter")
                    continue
                
                # 解析日期用于排序
                date_obj = parse_date_for_sorting(frontmatter.get('date', ''))
                
                files_info.append([filename, filepath, frontmatter, date_obj, body])
                
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
        
        if not files_info:
            print(f"目录 {rel_dir} 中没有可处理的文件")
            continue
        
        # 按日期排序并分配weight
        sorted_files = assign_weights_by_date(files_info)
        
        # 处理每个文件
        dir_updated = 0
        for filename, filepath, frontmatter, date_obj, body in sorted_files:
            total_processed += 1
            updated = False
            
            print(f"处理文件: {filename}")
            
            # 1. 修改date格式
            if 'date' in frontmatter:
                new_date = convert_date_format(frontmatter['date'])
                if new_date and new_date != frontmatter['date']:
                    frontmatter['date'] = new_date
                    print(f"  更新date: {new_date}")
                    updated = True
            
            # 2. 清理title中GESP前缀
            if 'title' in frontmatter:
                original_title = frontmatter['title']
                cleaned_title = clean_title(original_title)
                if cleaned_title != original_title:
                    frontmatter['title'] = cleaned_title
                    print(f"  更新title: {original_title} -> {cleaned_title}")
                    updated = True
            
            # 3. 添加或更新slug字段
            slug = extract_slug_from_filename(filename)
            if 'slug' not in frontmatter or frontmatter['slug'] != slug:
                frontmatter['slug'] = slug
                print(f"  设置slug: {slug}")
                updated = True
            
            # 4. 添加或更新type字段
            if 'type' not in frontmatter or frontmatter['type'] != 'docs':
                frontmatter['type'] = 'docs'
                print(f"  设置type: docs")
                updated = True
            
            # 5. weight已在assign_weights_by_date中设置
            print(f"  设置weight: {frontmatter['weight']}")
            
            # 如果有更新，写入文件
            if updated or 'weight' not in frontmatter:
                # 格式化frontmatter
                formatted_frontmatter = format_frontmatter(frontmatter)
                
                # 重新构建文件内容
                new_content = f"---\n{formatted_frontmatter}\n---\n{body}"
                
                # 写入文件
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  ✓ 文件更新成功")
                    dir_updated += 1
                    total_updated += 1
                except Exception as e:
                    print(f"  ✗ 写入文件时出错: {e}")
            else:
                print(f"  - 文件无需更新")
        
        print(f"目录 {rel_dir} 处理完成: {dir_updated}/{len(sorted_files)} 个文件被更新")
    
    print(f"\n总计处理 {total_processed} 个文件，更新 {total_updated} 个文件")

def main():
    """主函数"""
    print("======================================")
    print("Markdown文件frontmatter格式化工具")
    print("======================================")
    print("功能：")
    print("1. 递归查找所有.md文件")
    print("2. 格式化frontmatter元数据")
    print("3. 清理title中GESP前缀")
    print("4. 按日期排序并分配weight")
    print("======================================")
    
    # 指定要处理的目录
    target_directory = input("请输入要处理的根目录路径（相对于项目根目录，留空使用默认）: ").strip()
    
    if not target_directory:
        target_directory = "content"  # 默认目录
    
    # 构建完整路径
    base_dir = Path(__file__).parent
    full_directory = base_dir / target_directory
    
    print(f"处理根目录: {full_directory}")
    
    # 确认操作
    confirm = input("确认开始处理吗？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("操作已取消")
        return
    
    print("=" * 60)
    
    process_markdown_files(str(full_directory))
    
    print("=" * 60)
    print("处理完成！")

if __name__ == "__main__":
    main()