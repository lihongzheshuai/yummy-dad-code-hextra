---
layout: post
title: 202609-直角三角形(luogu-B4575)
date: 2026-09-15T15:10:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP二级
- 勾股定理
- 递推
- 数学函数
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 二级
- 基础算法
slug: gesp-2-luogu-b4575-right-triangle
type: docs
weight: 29
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 二级试题，洛谷 B4575。本题严格遵循 CCF GESP 官方大纲规范，重点考察**勾股定理与数列平方递推**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## B4575 [GESP202609 二级] 直角三角形

> 🔗 **洛谷原题传送门**：[B4575](https://www.luogu.com.cn/problem/B4575)

### 题目描述

小双刚学会勾股定理，得知直角三角形的斜边的平方等于两直角边的平方和。

小双创造了直角三角形数列：数列前两项由小双指定，从第三项开始，数列中的每个数字的平方等于前两项的平方和。

例如，第一项是 $3.0$，第二项是 $4.0$，则第三项是 $\sqrt{3.0^2 + 4.0^2} = 5.0$。

其中 $\sqrt{x}$ 表示 $x$ 的算术平方根，可以使用 C/C++/Python 标准库中对应函数计算。

小双给定了数列的前两项，并给定一个数列上限，想让你算算数列的第几项会超过小双给定的数列上限？

### 输入格式

输入三行，第一行一个浮点数是数列第一项，第二行一个浮点数是数列第二项，第三行一个浮点数表示数列上限。

### 输出格式

输出一个正整数，表示第几项开始会超过小双给定的数列上限。

### 输入输出样例

#### 输入 #1

```text
3.0
4.0
10.0
```

#### 输出 #1

```text
6
```

### 说明/提示

#### 样例解释 1

数列依次为：

* $3.0$，
* $4.0$，
* $\sqrt{3.0^2 + 4.0^2} = 5.0$，
* $\sqrt{4.0^2 + 5.0^2} \approx 6.403124$，
* $\sqrt{5.0^2 + 6.403124^2} \approx 8.124038$，
* $\sqrt{6.403124^2 + 8.124038^2} \approx 10.344080$，

因此第 6 项会超过上限。

#### 数据范围

输入均为不超过 $10000$ 的正数。

题目保证给定第一项小于第二项。

无需过度考虑浮点精度问题。

---

### 题目分析与解题思路

1. **数列递推模型**：定义 $a_1, a_2$ 为初值。对于 $i \ge 3$，$a_i = \sqrt{a_{i-1}^2 + a_{i-2}^2}$，即 $a_i^2 = a_{i-1}^2 + a_{i-2}^2$。这项增长本质上是斐波那契数列在平方维度的映射，增长速度非常迅猛。
2. **终止条件与初始边界**：题目保证 $a_1 < a_2$。若 $a_1 > \text{limit}$，则第 1 项即超过；若 $a_2 > \text{limit}$，第 2 项超过；否则使用 `while` 循环不断计算下一项直至超过上限，记录项数并输出。
3. **C++ 标准库函数**：使用 `<cmath>` 中的 `std::sqrt()` 函数，完全符合 C++11 标准。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-B4575
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <cmath>

using namespace std;

int main() {
    // 快速输入输出
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    double a, b, limit;
    if (!(cin >> a >> b >> limit)) {
        return 0;
    }

    // 特判前两项已超出上限的情况
    if (a > limit) {
        cout << 1 << "\n";
        return 0;
    }
    if (b > limit) {
        cout << 2 << "\n";
        return 0;
    }

    int step = 2;
    double prev2 = a; // 前两项中的较早一项 a_{i-2}
    double prev1 = b; // 前一项 a_{i-1}

    // 循环模拟生成后续项
    while (prev1 <= limit) {
        double next_val = sqrt(prev2 * prev2 + prev1 * prev1);
        step++;
        if (next_val > limit) {
            cout << step << "\n";
            return 0;
        }
        prev2 = prev1;
        prev1 = next_val;
    }

    cout << step << "\n";
    return 0;
}
```
