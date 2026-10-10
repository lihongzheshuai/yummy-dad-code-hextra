---
layout: post
title: "P17457 数组划分"
linkTitle: "P17457 数组划分"
date: 2026-09-15T15:50:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP六级
- CSP-J
- 动态规划
- 前缀和
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 六级
- 动态规划
- CSP-J
slug: gesp-6-luogu-p17457-array-partition
type: docs
weight: 9
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 六级试题，洛谷 P17457。本题严格遵循 CCF GESP 官方大纲规范，重点考察**前缀和优化与线性动态规划**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## P17457 [GESP202609 六级] 数组划分

> 🔗 **洛谷原题传送门**：[P17457](https://www.luogu.com.cn/problem/P17457)

### 题目描述

给定 $n$ 个整数构成的数组 $A = [a_1, a_2, \dots, a_n]$。

你需要将数组 $A$ 划分为若干非空连续子段。对于划分得到的某个子段，它的偏差值定义为子段内整数和的平方。划分方案的偏差值定义为所有子段偏差值之和。

你需要最小化划分方案的偏差值。

形式化地，你可以将 $A$ 划分为若干非空连续子段 $A_1, A_2, \dots, A_k$，使得 $A = A_1 + A_2 + \dots + A_k$，这里的 $+$ 代表数组的连接。对于 $1 \le i \le k$，设数组 $A_i = [a_1^{(i)}, \dots, a_{m_i}^{(i)}]$ 包含 $m_i$ 个整数。你需要最小化 $\sum_{i=1}^k \left(\sum_{j=1}^{m_i} a_j^{(i)}\right)^2$。

### 输入格式

第一行，一个正整数 $n$，表示数组 $A$ 的长度。

第二行，$n$ 个整数 $a_1, a_2, \dots, a_n$，表示数组 $A$。

### 输出格式

一行，一个整数，表示划分方案偏差值的最小值。

### 输入输出样例

#### 输入 #1

```text
4
1 2 -3 4
```

#### 输出 #1

```text
6
```

#### 输入 #2

```text
6
-1 -1 4 -5 -1 4
```

#### 输出 #2

```text
0
```

### 说明/提示

#### 数据范围

对于 $40\%$ 的测试点，保证 $0 \le a_i \le 50$。

对于所有测试点，保证 $1 \le n \le 2000$，$-100 \le a_i \le 100$。

---

### 题目分析与解题思路

1. **最优子结构与状态定义**：
   连续子段划分满足无后效性。定义 $dp[i]$ 表示将前缀 $A[1 \dots i]$ 划分为若干合法子段时的最小偏差值之和。
2. **状态转移方程**：
   枚举最后一个子段的起始位置 $j+1$（即上一个子段在 $j$ 处结束，其中 $0 \le j < i$）：
   $$dp[i] = \min_{0 \le j < i} \left( dp[j] + (prefix[i] - prefix[j])^2 \right)$$
   其中 $prefix[i] = \sum_{k=1}^i a_k$ 为前缀和。
3. **边界条件**：$dp[0] = 0$，其余初始化为正无穷 $\infty$。
4. **时间复杂度**：状态数 $\mathcal{O}(n)$，每个状态转移枚举 $\mathcal{O}(n)$，总时间复杂度 $\mathcal{O}(n^2)$。对于 $n \le 2000$，运算次数约 $2 \times 10^6$，在 $1\text{ s}$ 内轻松通过。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-P17457 [GESP202609 六级] 数组划分
 * Algorithm: 线性动态规划 (DP) + 前缀和优化
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main() {
    // 读入数组元素总数 n
    int n;
    cin >> n;

    // a 数组存储原始输入的 n 个整数 (下标采用 1 ~ n，方便对应前缀和)
    // prefix 数组存储前缀和，prefix[i] 表示前 i 项之和：a[1] + a[2] + ... + a[i]
    // 数据范围：n <= 2000，|a_i| <= 100，前缀和最大绝对值可达 2000 * 100 = 200,000
    // 子段和的平方最大可达 (200,000)^2 = 4 * 10^10，已超出 32 位 int 上限 (~2 * 10^9)
    // 为避免整型溢出，所有数值与 DP 状态统一使用 64 位整型 long long
    vector<long long> a(n + 1);
    vector<long long> prefix(n + 1, 0);

    for (int i = 1; i <= n; ++i) {
        cin >> a[i];
        // 递推计算前缀和，实现 O(1) 快速查询任意连续子段 [j+1, i] 的元素和
        prefix[i] = prefix[i - 1] + a[i];
    }

    // 定义无穷大常量 INF，用于初始化求最小值的 DP 数组
    // 答案上限约为 2000 * (200,000)^2 = 8 * 10^13，1e18 足够充当正无穷上界且不会溢出
    const long long INF = 1e18;

    // dp[i] 表示将前 i 个元素 a[1...i] 划分为若干个非空连续子段时的最小偏差值之和
    vector<long long> dp(n + 1, INF);

    // 初始状态 / 边界条件：
    // 前 0 个元素尚未划分任何子段，偏差值为 0
    dp[0] = 0;

    // 外层循环：依序计算前缀长度 i 从 1 到 n 的最小偏差值
    for (int i = 1; i <= n; ++i) {
        // 内层循环：枚举最后一个子段的起始位置 j+1（即上一个子段结束在 j 处，0 <= j < i）
        // 此时最后一段区间为 [j+1, i]，其子段和为 prefix[i] - prefix[j]
        for (int j = 0; j < i; ++j) {
            // O(1) 计算当前子段的元素和
            long long seg_sum = prefix[i] - prefix[j];
            // 计算按照位置 j 划分时的总偏差值：前 j 个元素的最优值 + 当前子段和的平方
            long long cost = dp[j] + seg_sum * seg_sum;

            // 状态转移：寻找所有合法划分点 j 中的最小值
            if (cost < dp[i]) {
                dp[i] = cost;
            }
        }
    }

    // 输出将整个数组 a[1...n] 划分为若干子段后的最小偏差值
    cout << dp[n] << endl;

    return 0;
}
```
