#!/usr/bin/env python3
"""
Random Number Generator
快速生成随机数字的命令行工具
"""

import argparse
import json
import random
import sys
from statistics import mean


def generate_random_numbers(count=3, min_val=1, max_val=100, unique=False, sort=False):
    """生成随机数字列表"""
    if unique and (max_val - min_val + 1) < count:
        raise ValueError(f"无法生成 {count} 个不重复的数字（范围 {min_val}-{max_val} 只有 {max_val - min_val + 1} 个值）")
    
    if unique:
        numbers = random.sample(range(min_val, max_val + 1), count)
    else:
        numbers = [random.randint(min_val, max_val) for _ in range(count)]
    
    if sort:
        numbers.sort()
    
    return numbers


def format_output(numbers, output_format='default'):
    """格式化输出"""
    if output_format == 'json':
        return json.dumps({
            'numbers': numbers,
            'count': len(numbers),
            'min': min(numbers),
            'max': max(numbers),
            'avg': round(mean(numbers), 2),
            'sum': sum(numbers)
        }, ensure_ascii=False, indent=2)
    
    elif output_format == 'csv':
        return '\n'.join(map(str, numbers))
    
    elif output_format == 'array':
        return str(numbers)
    
    elif output_format == 'sum-only':
        return str(sum(numbers))
    
    else:  # default
        stats = f"""
统计信息：
- 最小值：{min(numbers)}
- 最大值：{max(numbers)}
- 平均值：{round(mean(numbers), 2)}
- 总和：{sum(numbers)}
"""
        return f"""🎲 随机生成了 {len(numbers)} 个数字：

{chr(10).join(map(str, numbers))}
{stats}"""


def main():
    parser = argparse.ArgumentParser(
        description='随机生成指定数量的数字（默认3个）',
        usage='random [数量] [最小值] [最大值] [选项]'
    )
    parser.add_argument('count', nargs='?', type=int, default=3,
                        help='要生成的随机数个数（默认：3）')
    parser.add_argument('min', nargs='?', type=int, default=1,
                        help='随机数的最小值（默认：1）')
    parser.add_argument('max', nargs='?', type=int, default=100,
                        help='随机数的最大值（默认：100）')
    parser.add_argument('--unique', '-u', action='store_true',
                        help='生成不重复的数字')
    parser.add_argument('--sort', '-s', action='store_true',
                        help='排序输出')
    parser.add_argument('--json', action='store_true',
                        help='JSON格式输出')
    parser.add_argument('--csv', action='store_true',
                        help='CSV格式输出')
    parser.add_argument('--array', action='store_true',
                        help='数组格式输出')
    parser.add_argument('--sum-only', action='store_true',
                        help='只显示总和')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.count <= 0:
        print("❌ 错误：数量必须大于0", file=sys.stderr)
        sys.exit(1)
    
    if args.min >= args.max:
        print("❌ 错误：最小值必须小于最大值", file=sys.stderr)
        sys.exit(1)
    
    # 确定输出格式
    output_format = 'default'
    if args.json:
        output_format = 'json'
    elif args.csv:
        output_format = 'csv'
    elif args.array:
        output_format = 'array'
    elif args.sum_only:
        output_format = 'sum-only'
    
    try:
        # 生成随机数
        numbers = generate_random_numbers(
            count=args.count,
            min_val=args.min,
            max_val=args.max,
            unique=args.unique,
            sort=args.sort
        )
        
        # 输出结果
        print(format_output(numbers, output_format))
        
    except ValueError as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
