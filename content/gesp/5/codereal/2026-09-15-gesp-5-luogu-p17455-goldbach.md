---
layout: post
title: "P17455 哥德巴赫猜想"
linkTitle: "P17455 哥德巴赫猜想"
date: 2026-09-15T15:40:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP五级
- CSP-J
- 数论
- 素数筛
- 哥德巴赫猜想
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 五级
- 数论
- CSP-J
slug: gesp-5-luogu-p17455-goldbach
type: docs
weight: 30
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 五级试题，洛谷 P17455。本题严格遵循 CCF GESP 官方大纲规范，重点考察**初等数论·欧拉线性筛与素数拆分**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## P17455 [GESP202609 五级] 哥德巴赫猜想

> 🔗 **洛谷原题传送门**：[P17455](https://www.luogu.com.cn/problem/P17455)

### 题目描述

众所周知，哥德巴赫猜想是说，任何大于 2 的偶数都能写成两个质数（素数）之和。例如：

* $4 = 2 + 2$
* $6 = 3 + 3$
* $8 = 3 + 5$
* $10 = 3 + 7 = 5 + 5$

聪明的你肯定想知道，对于大于 2 的偶数 $n$，它有多少种写成两个质数之和的方法。例如 4、6 和 8 都只有一种方法，10 有两种方法。请你编写程序计算这个问题的答案。

在本题中，我们认为两种方案不同，当且仅当两种分解方案包含的素数互不相同；即 $10 = 3 + 7$ 和 $10 = 7 + 3$ 是同一种方案，不能重复计数。

### 输入格式

一行，一个大于 2 的偶数 $n$。

### 输出格式

一行，一个整数，表示将 $n$ 写成两个质数之和的方法数。

### 输入输出样例

#### 输入 #1

```text
4
```

#### 输出 #1

```text
1
```

#### 输入 #2

```text
10
```

#### 输出 #2

```text
2
```

### 说明/提示

#### 数据范围

对于 $40\%$ 的测试点，保证 $4 \le n \le 100$。

对于所有测试点，保证 $4 \le n \le 10^6$。

---

### 题目分析与解题思路

1. **线性素数筛预处理**：$n \le 10^6$，若对每个数调用单次 $\mathcal{O}(\sqrt{n})$ 试除判断，总复杂度过高。标准五级解法是采用**欧拉线性筛（Linear Sieve）**在 $\mathcal{O}(n)$ 时间内预处理出 $1 \sim n$ 的所有素数及布尔查表数组 `is_prime`。
2. **无序对枚举避免重复**：要求 $p + q = n$ 且无序，只需枚举质数 $p \le n/2$，此时必有 $q = n - p \ge p$。若 `is_prime[q]` 同样为真，则答案计数加一。
3. **时空复杂度**：线性筛仅耗时约 $10\text{ ms}$，内存仅需 $1\text{ MB}$，完全胜任 $10^6$ 规模。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-P17455
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <vector>

using namespace std;

const int MAXN = 1000000;
bool is_prime[MAXN + 1];
vector<int> primes;

// 欧拉线性筛：保证每个合数仅被其最小质因数筛掉一次
void sieve(int limit) {
    for (int i = 2; i <= limit; ++i) is_prime[i] = true;
    for (int i = 2; i <= limit; ++i) {
        if (is_prime[i]) {
            primes.push_back(i);
        }
        for (int p : primes) {
            if (i * p > limit) break;
            is_prime[i * p] = false;
            if (i % p == 0) break;
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    if (!(cin >> n) || n <= 2 || n % 2 != 0) {
        return 0;
    }

    sieve(n);

    int count = 0;
    // 枚举较小质数 p <= n / 2，保证方案不重复
    for (int p : primes) {
        if (p > n / 2) break;
        int q = n - p;
        if (is_prime[q]) {
            count++;
        }
    }

    cout << count << "\n";

    return 0;
}
```
