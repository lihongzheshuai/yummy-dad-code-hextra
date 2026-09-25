---
layout: post
title: 202609-生成树计数(luogu-P17461)
date: 2026-09-15T16:10:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP八级
- CSP-S
- 高级图论
- 仙人掌图
- 生成树
- DFS
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 八级
- 高级图论
- CSP-S
slug: gesp-8-luogu-p17461-cactus-spanning-tree
type: docs
weight: 1
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 八级试题，洛谷 P17461。本题严格遵循 CCF GESP 官方大纲规范，重点考察**仙人掌图性质与乘法原理生成树计数**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## P17461 [GESP202609 八级] 生成树计数

> 🔗 **洛谷原题传送门**：[P17461](https://www.luogu.com.cn/problem/P17461)

### 题目描述

给定一张有 $n$ 个顶点 $m$ 条边的无向连通图 $G$，顶点依次以 $1, 2, \dots, n$ 编号。$G$ 有以下特殊的性质：

* $G$ 中的每条边至多属于一个简单环。
* $G$ 中没有重边与自环。

简单环是指环中顶点互不相同，且不经过重复边的回路。

请你求出 $G$ 的不同生成树的数量。两棵生成树不同，当且仅当存在一条边在其中一棵生成树中出现，而不在另一棵生成树中出现。

由于答案可能很大，你只要求出答案对 $998244353$ 取模的结果。

### 输入格式

第一行，两个正整数 $n, m$，分别表示 $G$ 的顶点数与边数。

接下来 $m$ 行，每行两个整数 $u_i, v_i$，表示一条连接顶点 $u_i, v_i$ 的无向边。

### 输出格式

输出一行，一个整数，表示 $G$ 的不同生成树的数量对 $998244353$ 取模的结果。

### 输入输出样例

#### 输入 #1

```text
7 8
1 2
2 3
3 1
3 4
4 5
5 6
6 7
7 4
```

#### 输出 #1

```text
12
```

#### 输入 #2

```text
5 4
1 2
1 3
2 4
2 5
```

#### 输出 #2

```text
1
```

### 说明/提示

#### 数据范围

对于 $40\%$ 的测试点，保证 $1 \le n \le 8$，$1 \le m \le 10$。

对于 $60\%$ 的测试点，保证 $1 \le n \le 2000$，$1 \le m \le 2000$。

对于所有测试点，保证 $1 \le n \le 10^5$，$1 \le m \le 10^5$，$1 \le u_i, v_i \le n$。

---

### 题目分析与解题思路

1. **仙人掌图生成树核心定理**：
   - 在仙人掌图（Cactus Graph）中，任意两个简单环不共享边。
   - 为了消除所有的环且保持全图连通，对于每个长度为 $L$ 的简单环，**必须且只能恰好删去环上的一条边**（有 $L$ 种独立的选择）；
   - 不属于任何环的边（桥边，Bridge）必须保留在生成树中；
   - 由乘法原理，生成树总数严格等于所有简单环长度的乘积：
     $$\text{Spanning Trees} = \prod_{C \in \text{Cycles}} |C| \pmod{998244353}$$
2. **线性 DFS 环长提取**：
   在 DFS 搜索树中，每条反向返祖边（Back-edge）$(u, v)$ 与树边路径恰好构成一个简单环，其环长即为深度差加一：$L = depth[u] - depth[v] + 1$。
   单次线性遍历即可求得所有环长，时间复杂度完美 $\mathcal{O}(n + m)$。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-P17461
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <vector>

using namespace std;

const int MAXN = 100005;
const int MOD = 998244353;

vector<int> adj[MAXN];
int depth_arr[MAXN];
bool visited[MAXN];
long long ans = 1;

void dfs(int u, int p, int d) {
    depth_arr[u] = d;
    visited[u] = true;
    for (int v : adj[u]) {
        if (v == p) continue;
        if (visited[v]) {
            if (depth_arr[v] < depth_arr[u]) {
                // 返祖边：找到一个简单环
                int cycle_len = depth_arr[u] - depth_arr[v] + 1;
                ans = (ans * cycle_len) % MOD;
            }
        } else {
            dfs(v, u, d + 1);
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    if (!(cin >> n >> m)) return 0;

    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }

    dfs(1, 0, 1);

    cout << ans << "\n";

    return 0;
}
```
