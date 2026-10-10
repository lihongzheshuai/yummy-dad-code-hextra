---
layout: post
title: "P17456 饮品调制"
linkTitle: "P17456 饮品调制"
date: 2026-09-15T15:45:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP五级
- CSP-J
- 贪心
- 排序不等式
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 五级
- 贪心算法
- CSP-J
slug: gesp-5-luogu-p17456-beverage-mix
type: docs
weight: 31
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 五级试题，洛谷 P17456。本题严格遵循 CCF GESP 官方大纲规范，重点考察**贪心算法与平均值平衡杠杆原理**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## P17456 [GESP202609 五级] 饮品调制

> 🔗 **洛谷原题传送门**：[P17456](https://www.luogu.com.cn/problem/P17456)

### 题目描述

你想调制一份甜度恰到好处的饮品给你的朋友们品尝。

有 $n$ 种原料可供用于调制饮品。第 $i$ 种原料存量有 $v_i$ 升，每升含有 $s_i$ 克糖分。你可以自由选择原料加入饮品，但每种原料的使用量不得超过其剩余存量。也就是说，假设第 $i$ 种原料选用 $k_i$ 升，应当有 $0 \le k_i \le v_i$，$k_i$ 可以取 0 到 $v_i$ 之间的任何数字（包括小数）。

一份甜度恰到好处的饮品需要保证甜度恰好为 $t$。最终你调制得到的饮品甜度将为 $\frac{\sum_{i=1}^n k_i \cdot s_i}{\sum_{i=1}^n k_i}$。为了让更多的朋友喝到饮品，请问最多能调制出多少升甜度恰到好处的饮品？如果无法调制出甜度恰到好处的饮品，则认为答案是 0。

### 输入格式

第一行，两个整数 $n, t$，分别表示原料种类数量，恰到好处的甜度。

接下来 $n$ 行，每行两个整数 $v_i, s_i$，分别表示第 $i$ 种原料的存量体积，每升含有的糖分质量。

### 输出格式

一行，一个小数，表示能调制出的甜度恰到好处的饮品最大体积，保留三位小数。

### 输入输出样例

#### 输入 #1

```text
4 2
6 1
5 2
8 5
1 0
```

#### 输出 #1

```text
14.667
```

#### 输入 #2

```text
2 5
3 4
5 3
```

#### 输出 #2

```text
0.000
```

### 说明/提示

#### 数据范围

对于 $40\%$ 的测试点，保证 $n = 2$。

对于所有测试点，保证 $1 \le n \le 2000$，$0 \le t \le 200$，$1 \le v_i \le 100$，$0 \le s_i \le 200$。

---

### 题目分析与解题思路

1. **基准差值转换**：平均甜度等于 $t$ 等价于净糖分盈余为 0：
   $$\sum k_i (s_i - t) = 0$$
   - 若 $s_i = t$：相对贡献为 0，可以无条件全额选用所有体积；
   - 若 $s_i > t$：每升提供 $s_i - t > 0$ 的正贡献；
   - 若 $s_i < t$：每升产生 $t - s_i > 0$ 的负需求。
2. **贪心选择原则（单位贡献体积最大化）**：
   为了在正负糖分平衡的前提下最大化总体积，我们希望**每提供 1 单位盈余/赤字，消耗的液体体积尽可能大**！
   每单位糖分所需体积为 $\frac{1}{|s_i - t|}$。因此，**$|s_i - t|$ 越小，单位效率越高**！
3. **执行流程**：
   - 正侧原料按 $s_i - t$ 升序排序，负侧原料按 $t - s_i$ 升序排序；
   - 最大可平衡的总糖分量为 $W = \min(\text{总正盈余}, \text{总负赤字})$；
   - 分别在正侧与负侧按排好的贪心顺序取出能达到 $W$ 的体积并累加。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-P17456
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <iomanip>

using namespace std;

struct Item {
    double v;
    double s;
    double diff; // |s - t|
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    double t;
    if (!(cin >> n >> t)) {
        return 0;
    }

    double zero_vol = 0.0;
    vector<Item> pos;
    vector<Item> neg;
    double total_pos = 0.0;
    double total_neg = 0.0;

    for (int i = 0; i < n; ++i) {
        double v, s;
        cin >> v >> s;
        if (s == t) {
            zero_vol += v;
        } else if (s > t) {
            pos.push_back({v, s, s - t});
            total_pos += v * (s - t);
        } else {
            neg.push_back({v, s, t - s});
            total_neg += v * (t - s);
        }
    }

    // 贪心排序：diff 越小，每单位贡献换取的体积越大
    sort(pos.begin(), pos.end(), [](const Item& a, const Item& b) {
        return a.diff < b.diff;
    });
    sort(neg.begin(), neg.end(), [](const Item& a, const Item& b) {
        return a.diff < b.diff;
    });

    double balance_w = min(total_pos, total_neg);

    if (balance_w == 0.0 && zero_vol == 0.0) {
        cout << "0.000\n";
        return 0;
    }

    double ans_vol = zero_vol;

    // 贪心满足正侧 balance_w
    double need_pos = balance_w;
    for (const auto& item : pos) {
        if (need_pos <= 0) break;
        double max_give = item.v * item.diff;
        if (need_pos >= max_give) {
            ans_vol += item.v;
            need_pos -= max_give;
        } else {
            ans_vol += need_pos / item.diff;
            need_pos = 0;
        }
    }

    // 贪心满足负侧 balance_w
    double need_neg = balance_w;
    for (const auto& item : neg) {
        if (need_neg <= 0) break;
        double max_give = item.v * item.diff;
        if (need_neg >= max_give) {
            ans_vol += item.v;
            need_neg -= max_give;
        } else {
            ans_vol += need_neg / item.diff;
            need_neg = 0;
        }
    }

    cout << fixed << setprecision(3) << ans_vol << "\n";

    return 0;
}
```
