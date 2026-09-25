---
layout: post
title: 202609-有序网格(luogu-B4580)
date: 2026-09-15T15:35:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP四级
- CSP-J
- 二维数组
- 排序
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 四级
- 二维数组
- CSP-J
slug: gesp-4-luogu-b4580-ordered-grid
type: docs
weight: 28
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 四级试题，洛谷 B4580。本题严格遵循 CCF GESP 官方大纲规范，重点考察**二维数组与行列双重排序**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## B4580 [GESP202609 四级] 有序网格

> 🔗 **洛谷原题传送门**：[B4580 [GESP202609 四级] 有序网格](https://www.luogu.com.cn/problem/B4580)

### 题目描述

小 A 有一个 $n$ 行 $m$ 列格子组成的二维网格，从上到下依次是第 $1$ 行到第 $n$ 行，从左到右依次是第 $1$ 列到第 $m$ 列。每个格子里有一个数字，第 $i$ 行第 $j$ 列的格子里的数字是 $a_{i,j}$。

小 A 想让二维网格变得有序，因此他先对每一行从左到右按升序排序，再对每一列从上到下按升序排序。以下是一个先完成行排序再完成列排序的例子：

$$
\begin{array}{|c|c|c|c|}\hline 1&3&2&5\\\hline 6&2&4&4\\\hline 5&4&1&3\\\hline\end{array}\xrightarrow{\text{每行升序排序}}\begin{array}{|c|c|c|c|}\hline 1&2&3&5\\\hline 2&4&4&6\\\hline 1&3&4&5\\\hline\end{array}\xrightarrow{\text{每列升序排序}}\begin{array}{|c|c|c|c|}\hline 1&2&3&5\\\hline 1&3&4&5\\\hline 2&4&4&6\\\hline\end{array}
$$

小 A 想知道二维网格经过以上排序后的结果。你能编写程序帮助他吗？

### 输入格式

第一行，两个正整数 $n,m$，分别表示二维网格的行数与列数。

接下来 $n$ 行，每行 $m$ 个整数 $a_{i,1},\ldots,a_{i,m}$，表示二维网格中的数字。

### 输出格式

输出 $n$ 行，每行 $m$ 个整数，表示二维网格先完成行排序再完成列排序后的结果。

### 输入输出样例

#### 输入 #1

```text
3 2
6 5
4 3
2 1
```

#### 输出 #1

```text
1 2
3 4
5 6
```

#### 输入 #2

```text
3 4
1 3 2 5
6 2 4 4
5 4 1 3
```

#### 输出 #2

```text
1 2 3 5
1 3 4 5
2 4 4 6
```

### 说明/提示

#### 数据范围

对于所有测试点，保证 $2 \le n \le 10$，$2 \le m \le 10$，$1 \le a_{i,j} \le 100$。

---

### 题目分析与解题思路

1. **二维网格操作模型**：
   题目要求对二维网格做两阶段排序：
   - **第一阶段（行排序）**：固定每一行 $i$（$0 \le i < n$），对该行的 $m$ 个元素调用 `std::sort(grid[i], grid[i] + m)` 进行升序排序；
   - **第二阶段（列排序）**：固定每一列 $j$（$0 \le j < m$），将该列的全部 $n$ 个元素抽取至一维容器 `col`，排序后再按升序放回原网格的对应列 `grid[i][j]`。
2. **数据规模与复杂度**：
   - 保证 $2 \le n, m \le 10$，网格中最多仅 100 个数字；
   - 行排序复杂度为 $O(n \cdot m \log m)$，列排序复杂度为 $O(m \cdot n \log n)$，总计算量在数百次操作内，耗时不超过 1ms，直接使用标准库 `std::sort` 即可优雅解决。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-B4580
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    // 提升 I/O 执行效率
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    if (!(cin >> n >> m)) {
        return 0;
    }

    int grid[15][15];
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cin >> grid[i][j];
        }
    }

    // 1. 对每一行按升序排序
    for (int i = 0; i < n; ++i) {
        sort(grid[i], grid[i] + m);
    }

    // 2. 对每一列按升序排序
    for (int j = 0; j < m; ++j) {
        vector<int> col(n);
        for (int i = 0; i < n; ++i) {
            col[i] = grid[i][j];
        }
        sort(col.begin(), col.end());
        for (int i = 0; i < n; ++i) {
            grid[i][j] = col[i];
        }
    }

    // 3. 格式化输出排序后的最终结果
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cout << grid[i][j] << (j == m - 1 ? "" : " ");
        }
        cout << "\n";
    }

    return 0;
}
```
