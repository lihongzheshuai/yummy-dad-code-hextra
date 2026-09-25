---
layout: post
title: 202609-公共二进制位(luogu-B4577)
date: 2026-09-15T15:20:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP三级
- CSP-J
- 位运算
- 二进制
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 三级
- 位运算
- CSP-J
slug: gesp-3-luogu-b4577-common-binary-bits
type: docs
weight: 28
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 三级试题，洛谷 B4577。本题严格遵循 CCF GESP 官方大纲规范，重点考察**位运算·按位与及公共位统计**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## B4577 [GESP202609 三级] 公共二进制位

> 🔗 **洛谷原题传送门**：[B4577](https://www.luogu.com.cn/problem/B4577)

### 题目描述

小红有 $n$ 个非负整数 $a_1, a_2, \dots, a_n$。她将每个整数转换为二进制后，想知道有多少个二进制位在所有整数中均为 1。

二进制位从右向左编号为 $0, 1, 2, \dots$。若某个整数的二进制表示中没有第 $k$ 位，则认为它的第 $k$ 位为 0。

请你求出满足条件的二进制位数量。

### 输入格式

* 第一行一个整数 $n$，表示整数的个数。
* 第二行 $n$ 个非负整数 $a_1, a_2, \dots, a_n$。

### 输出格式

输出一个整数，表示所有整数的二进制表示中均为 1 的二进制位的数量。

### 输入输出样例

#### 输入 #1

```text
3
5 13 15
```

#### 输出 #1

```text
2
```

### 说明/提示

#### 样例解释 1

给定的三个整数转换为二进制后分别为 $(0101)_2$、$(1101)_2$ 和 $(1111)_2$。

其中第 0 位和第 2 位均为 1，因此答案为 2。

#### 数据范围

$2 \le n \le 20000$，$0 \le a_i \le 10^9$。

---

### 题目分析与解题思路

1. **按位与（Bitwise AND）的数学本质**：在二进制中，某个位在所有数中均为 1，当且仅当所有数的按位与结果在该位上为 1。因此，所有数二进制公共为 1 的位集合，等价于累计按位与的值：
   $$R = a_1 \ \& \ a_2 \ \& \ \dots \ \& \ a_n$$
2. **快速统计 1 的个数（Hamming Weight）**：求出 $R$ 之后，只需统计 $R$ 二进制表示中 1 的个数即可。既可以通过循环 `while (R > 0) { count += (R & 1); R >>= 1; }`，也可以直接使用内建函数 `__builtin_popcountll(R)`。
3. **数据规模**：$n \le 20000, a_i \le 10^9$，单次遍历求与耗时 $\mathcal{O}(n)$，瞬时完成。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-B4577
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    if (!(cin >> n) || n <= 0) {
        return 0;
    }

    long long common_bits;
    cin >> common_bits;

    // 顺序与后续所有数做按位与
    for (int i = 1; i < n; ++i) {
        long long a;
        cin >> a;
        common_bits &= a;
    }

    // 统计公共位中 1 的数量
    int count = 0;
    while (common_bits > 0) {
        if (common_bits & 1) {
            count++;
        }
        common_bits >>= 1;
    }

    cout << count << "\n";

    return 0;
}
```
