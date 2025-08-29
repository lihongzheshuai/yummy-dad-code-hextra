import os
import re
from datetime import datetime
import yaml
from pathlib import Path

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

def extract_slug_from_filename(filename):
    """从文件名提取slug，去掉开头的日期部分"""
    # 匹配格式：yyyy-MM-dd-...
    match = re.match(r'^\d{4}-\d{2}-\d{2}-(.+)\.md$', filename)
    if match:
        return match.group(1)
    return filename.replace('.md', '')

def convert_date_format(date_str):
    """转换日期格式为2024-11-02T20:00:00+0800格式"""
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

def get_max_weight(directory):
    """获取目录中所有文件的最大weight值"""
    max_weight = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, _ = parse_frontmatter(content)
                if frontmatter and 'weight' in frontmatter:
                    weight = int(frontmatter['weight'])
                    max_weight = max(max_weight, weight)
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")
                continue
    
    return max_weight

def process_markdown_files(directory):
    """处理指定目录中的Markdown文件"""
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在")
        return
    
    # 获取当前最大的weight值
    max_weight = get_max_weight(directory)
    print(f"当前目录中最大weight值: {max_weight}")
    
    # 收集需要处理的文件
    files_to_process = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = parse_frontmatter(content)
                if frontmatter is None:
                    print(f"跳过文件 {filename}: 无法解析frontmatter")
                    continue
                
                # 检查是否没有slug字段
                if 'type' not in frontmatter:
                    files_to_process.append((filename, filepath, frontmatter, body))
            
            except Exception as e:
                print(f"读取文件 {filename} 时出错: {e}")
                continue
    
    if not files_to_process:
        print("没有找到需要处理的文件（缺少type字段的文件）")
        return
    
    print(f"找到 {len(files_to_process)} 个需要处理的文件")
    
    # 按文件名排序，确保weight分配的一致性
    files_to_process.sort(key=lambda x: x[0])
    
    # 处理每个文件
    current_weight = max_weight + 1
    
    for filename, filepath, frontmatter, body in files_to_process:
        print(f"处理文件: {filename}")
        
        # 1. 修改date格式
        if 'date' in frontmatter:
            new_date = convert_date_format(frontmatter['date'])
            if new_date:
                frontmatter['date'] = new_date
                print(f"  更新date: {new_date}")
        
        # 2. 添加slug字段
        slug = extract_slug_from_filename(filename)
        frontmatter['slug'] = slug
        print(f"  添加slug: {slug}")
        
        # 3. 添加type字段
        frontmatter['type'] = 'docs'
        print(f"  添加type: docs")
        
        # 4. 添加weight字段
        frontmatter['weight'] = current_weight
        print(f"  添加weight: {current_weight}")
        current_weight += 1
        
        # 格式化frontmatter
        formatted_frontmatter = format_frontmatter(frontmatter)
        
        # 重新构建文件内容
        new_content = f"---\n{formatted_frontmatter}\n---\n{body}"
        
        # 写入文件
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✓ 文件 {filename} 更新成功")
        except Exception as e:
            print(f"  ✗ 写入文件 {filename} 时出错: {e}")

def main():
    """主函数"""
    # 指定要处理的目录
    target_directory = input("请输入要处理的目录路径（相对于项目根目录）: ").strip()
    
    if not target_directory:
        target_directory = "content/gesp/1/codereal"  # 默认目录
    
    # 构建完整路径
    base_dir = Path(__file__).parent
    full_directory = base_dir / target_directory
    
    print(f"处理目录: {full_directory}")
    print("-" * 50)
    
    process_markdown_files(str(full_directory))
    
    print("-" * 50)
    print("处理完成!")

if __name__ == "__main__":
    main()