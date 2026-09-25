---
layout: post
title: luogu-P2440 木材加工
date: 2026-09-21T07:15:00+0800
author: OneCoder
comments: true
tags:
- 洛谷
- C++
- 二分答案
- 单调性
- 贪心
- GESP五级
- CSP-J
categories:
- GESP
- 五级
- 二分答案
- CSP-J
slug: gesp-5-luogu-p2440-wood-cut
type: docs
weight: 38
math: true
---


洛谷经典算法题 P2440「木材加工」，是算法竞赛与等级考试中**二分答案（Binary Search on Answer）**思想的极具代表性的入门与进阶典例。本题标准收录于 CCF GESP 五级考纲（二分查找与二分答案核心考点）以及 CSP-J 普及组算法题单。题目核心考查如何将“求满足条件的最大值”这一最优化目标，转化为“给定长度检验是否可行”的判定性问题（Decision Problem），利用切分段数随单段长度递增而严格单调不增的数学性质，在 $\mathcal{O}(n \log (\max L_i))$ 的高效时间复杂度内锁定最优解。题目难度⭐⭐⭐☆☆，洛谷难度评级为`普及/提高-`。

<!--more-->

## luogu-P2440 木材加工

> 🔗 **洛谷原题传送门**：[luogu-P2440 木材加工](https://www.luogu.com.cn/problem/P2440)

### 题目描述

木材厂有 $n$ 根原木，现在想把这些木头切割成 $k$ 段长度**均**为 $l$ 的小段木头（木头有可能有剩余）。

当然，我们希望得到的小段木头越长越好，请求出 $l$ 的最大值。

木头长度的单位是 $\text{cm}$，原木的长度都是正整数，我们要求切割得到的小段木头的长度也是正整数。

例如有两根原木长度分别为 $11$ 和 $21$，要求切割成等长的 $6$ 段，很明显能切割出来的小段木头长度最长为 $5$。

### 输入格式

第一行是两个正整数 $n,k$，分别表示原木的数量，需要得到的小段的数量。

接下来 $n$ 行，每行一个正整数 $L_i$，表示一根原木的长度。

### 输出格式

仅一行，即 $l$ 的最大值。

如果连 $\text{1cm}$ 长的小段都切不出来，输出 `0`。\n\n### 输入输出样例

#### 输入 #1

```text
3 7
232
124
456
```

#### 输出 #1

```text
114
```

### 说明/提示

#### 数据规模与约定

对于 $100\%$ 的数据，有 $1\le n\le 10^5$，$1\le k\le 10^8$，$1\le L_i\le 10^8(i\in[1,n])$。

---

### 题目深度剖析

#### 1. 问题建模与单调性分析

题目给定 $n$ 根原木，长度分别为 $L_1, L_2, \dots, L_n$，要求切出至少 $k$ 段长度均为 $l$ 的小木段，并最大化目标长度 $l$。

若我们设函数 $f(l)$ 表示：**当切出的小木段长度为 $l$ 时，所有原木最多能切出的总段数**。
由于每根原木只能独立切分（木料无法拼接），长度为 $L_i$ 的原木能切出 $\lfloor \frac{L_i}{l} \rfloor$ 段，因此：
$$f(l) = \sum_{i=1}^{n} \left\lfloor \frac{L_i}{l} \right\rfloor$$

观察函数 $f(l)$ 的数学性质：
1. **单调不增性**：随着小木段长度 $l$ 的不断增大，每一项 $\lfloor \frac{L_i}{l} \rfloor$ 均单调不增，其总和 $f(l)$ 必然关于 $l$ 单调递减（或保持不增）。
2. **可行性判定**：若某个长度 $l$ 能够切出不少于 $k$ 段（即 $f(l) \ge k$），则对于任意小于 $l$ 的正整数 $l' < l$，必有 $f(l') \ge f(l) \ge k$ 同样成立；反之，若长度 $l$ 无法切出 $k$ 段（$f(l) < k$），则任意大于 $l$ 的长度也绝不可能切出 $k$ 段。

这种在解空间内呈现出绝对“单调分界”的特性，正是**二分答案（Binary Search on Answer）**的标准应用场景！

#### 2. 二分答案搜索区间设计

我们需要确定答案 $l$ 的上下界：
- **下界（Left Bound）**：题目要求小木段长度为正整数，因此最小有效长度为 $1$。即初始 $left = 1$。
- **上界（Right Bound）**：切出的小木段不可能比所有原木中最长的一根还要长，因此上界可直接取 $right = \max_{1 \le i \le n} (L_i) \le 10^8$。

**二分转移流程**：
- 取区间中点 $mid = left + \lfloor \frac{right - left}{2} \rfloor$；
- 遍历所有原木，计算 $count = \sum_{i=1}^n \lfloor \frac{L_i}{mid} \rfloor$；
- 若 $count \ge k$：说明当前长度 $mid$ 是合法的，但可能还存在更长的合法长度，我们记录当前最优答案 $ans = mid$，并尝试向右半区间探索更优解（令 $left = mid + 1$）；
- 若 $count < k$：说明当前长度 $mid$ 偏大，导致切出的段数不足 $k$，该长度不可行，向左半区间压缩查找范围（令 $right = mid - 1$）。

当 $left > right$ 时，二分终止，$ans$ 即为所求的 $l$ 的最大可能值。

#### 3. 边界特判与整型溢出避坑

在 GESP 五级和 CSP-J 考场上，该题有两大极为致命的失分点：

1. **总段数累加溢出 32 位整型（“不开 long long 见祖宗”）**：
   - 题目中 $n \le 10^5$，$L_i \le 10^8$；
   - 在二分初期，当 $mid$ 较小（例如 $mid = 1$）时，每根原木切出的段数可达 $10^8$；
   - $n$ 根原木的总段数理论最大值可达 $n \times L_i = 10^5 \times 10^8 = 10^{13}$；
   - 32 位有符号整型 `int` 的最大上限约为 $2.14 \times 10^9$。若使用 `int` 存储累加变量 `count`，将发生严重溢出导致判定错误！
   - **应对策略**：累加段数 `count`、原木总长 `total_len` 以及目标需求 $k$ 必须使用 64 位整型 `long long`。同时在 `check` 函数中，一旦 `count >= k` 即可提前 `return true` 实现贪心剪枝。

2. **全长不足 $k$ 时的 $0$ 特判**：
   - 题目明确要求：“如果连 $1\text{cm}$ 长的小段都切不出来，输出 `0`”；
   - 若原木总长之和 $\sum L_i < k$，即便每段只取 $1\text{cm}$ 也无法满足要求；
   - 我们可以在二分前直接统计总长 $\sum L_i$，若小于 $k$ 直接输出 $0$ 退出程序；即使不预先特判，若我们将初始 $ans = 0$，当 $mid = 1$ 判定失败时，二分区间会直接收缩至 $right = 0$，最终输出 $ans = 0$，逻辑天然闭环。

#### 4. 复杂度分析

- **时间复杂度**：
  - 二分区间长度为 $\max L_i \le 10^8$；
  - 二分查找循环次数为 $\lceil \log_2(10^8) \rceil \approx 27$ 次；
  - 每次判定需要遍历一次长度为 $n$ 的数组，耗时 $\mathcal{O}(n)$，且配合 `count >= k` 提前退出常数极小；
  - 总体时间复杂度为 $\mathcal{O}(n \log(\max L_i))$。代入 $n = 10^5$，总基本操作次数约 $2.7 \times 10^6$ 次，在 $1.0\text{s}$ 时限内仅耗时约 $10\text{ms}$，极其充裕。
- **空间复杂度**：
  - 仅需一个全局静态数组存储 $n$ 根原木长度，空间复杂度为 $\mathcal{O}(n)$，占用内存约 $400\text{KB}$，远低于题目限制。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-P2440 木材加工
 * Algorithm: 二分答案 (Binary Search on Answer) / 单调性判定
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <algorithm>

using namespace std;

// 数据规模：n <= 10^5, 原木长度 L_i <= 10^8
const int MAXN = 100005;
int a[MAXN];

// check 函数：检验是否能够切割出至少 k 段长度为 len 的小木头
// 单调性核心：len 越小，切出的小段越多；len 越大，切出的小段越少
bool check(int len, int n, long long k) {
    long long count = 0;
    for (int i = 0; i < n; ++i) {
        // 每根原木长度为 a[i]，最多可切出 a[i] / len 段长度为 len 的小木头
        count += a[i] / len;
        // 剪枝：一旦累计段数达到或超过目标 k，说明该长度可行，直接返回 true
        if (count >= k) {
            return true;
        }
    }
    return count >= k;
}

int main() {
    int n;
    long long k;
    cin >> n >> k;

    int max_len = 0;
    long long total_len = 0;
    for (int i = 0; i < n; ++i) {
        cin >> a[i];
        if (a[i] > max_len) {
            max_len = a[i];
        }
        total_len += a[i];
    }

    // 边界特判：若所有原木总长度累加仍小于目标段数 k，
    // 则即便每段长度取最小正整数 1cm，也无法切出 k 段，直接输出 0
    if (total_len < k) {
        cout << 0 << endl;
        return 0;
    }

    // 二分答案：小段长度 l 的取值范围为 [1, max_len]
    int left = 1;
    int right = max_len;
    int ans = 0;

    while (left <= right) {
        int mid = left + (right - left) / 2;
        // 判定当前长度 mid 是否满足要求
        if (check(mid, n, k)) {
            // 如果长度为 mid 可行，记录该可行解，并尝试寻找更长的小段（向右半区间搜索）
            ans = mid;
            left = mid + 1;
        } else {
            // 如果长度为 mid 无法切出 k 段，说明太长了，向左半区间压缩
            right = mid - 1;
        }
    }

    // 输出所能得到的小段木头的最大长度 l
    cout << ans << endl;

    return 0;
}
```
