---
layout: post
title: "P17459 必经之路"
linkTitle: "P17459 必经之路"
date: 2026-09-15T16:00:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP七级
- CSP-S
- 图论
- 广度优先搜索
- 连通性
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 七级
- 图论
- CSP-S
slug: gesp-7-luogu-p17459-must-pass-node
type: docs
weight: 1
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 七级试题，洛谷 P17459。本题严格遵循 CCF GESP 官方大纲规范，重点考察**图论·全源可达性与割点检测**。题目逻辑严密，模型典型，是深入理解与掌握信奥核心考点的经典范例。

<!--more-->

## P17459 [GESP202609 七级] 必经之路

> 🔗 **洛谷原题传送门**：[P17459](https://www.luogu.com.cn/problem/P17459)

### 题目描述

给定一张有 $n$ 个结点 $m$ 条边的有向图 $G$，$G$ 中的结点依次以 $1, 2, \dots, n$ 编号。第 $i$ 条边（$1 \le i \le m$）从结点 $u_i$ 指向结点 $v_i$。

$G$ 中任一入度为 0 的结点可以作为合法起点，任一出度为 0 的结点可以作为合法终点。

如果 $G$ 中所有可能的从合法起点到合法终点的路径都会经过结点 $u$，则称 $u$ 是必经点。注意必经点可以为合法起点或合法终点。

请你求出 $G$ 中所有必经点的编号。

例如，在下图中合法起点有点 1 与点 2，合法终点有点 7 与点 8。

```text
(1)            (5)---->(7)
   \           ^  \    ^
    v         /    v  /
    (3)      /     (6)
    ^  \    /         \
   /    v  /           v
(2)---->(4)            (8)
```

所有合法起点到合法终点的路径为：

* $1 \to 3 \to 4 \to 5 \to 7$
* $1 \to 3 \to 4 \to 5 \to 6 \to 7$
* $1 \to 3 \to 4 \to 5 \to 6 \to 8$
* $2 \to 3 \to 4 \to 5 \to 7$
* $2 \to 3 \to 4 \to 5 \to 6 \to 7$
* $2 \to 3 \to 4 \to 5 \to 6 \to 8$
* $2 \to 4 \to 5 \to 7$
* $2 \to 4 \to 5 \to 6 \to 7$
* $2 \to 4 \to 5 \to 6 \to 8$

因此必经点有两个，编号分别为 4, 5。

### 输入格式

第一行，两个正整数 $n, m$，表示有向图 $G$ 中的结点数与边数。

接下来 $m$ 行，每行两个正整数 $u_i, v_i$，表示一条从结点 $u_i$ 指向结点 $v_i$ 的有向边。

保证 $G$ 中至少有一个合法起点，至少有一个合法终点，且至少存在一条从一个合法起点到一个合法终点路径，同时不存在孤立点（即出度和入度都为 0 的点）。

### 输出格式

第一行，一个整数，表示必经点的数量 $k$。

如果存在必经点，则第二行从小到大输出 $G$ 中所有必经点的编号。

### 输入输出样例

#### 输入 #1

```text
8 9
1 3
2 3
3 4
4 5
5 6
6 7
6 8
2 4
5 7
```

#### 输出 #1

```text
2
4 5
```

#### 输入 #2

```text
8 9
1 3
2 3
3 4
4 5
5 6
6 7
6 8
2 5
4 7
```

#### 输出 #2

```text
0
```

### 说明/提示

#### 数据范围

对于 $40\%$ 的测试点，保证 $1 \le n \le 100$，$1 \le m \le 200$。

对于所有测试点，保证 $1 \le n \le 1000$，$1 \le m \le 2000$。保证 $G$ 中至少有一个合法起点，至少有一个合法终点，且至少存在一条从一个合法起点到一个合法终点路径，同时不存在孤立点（即出度和入度都为 0 的点）。

---

### 题目分析与解题思路

1. **必经点的充要条件**：
   结点 $u$ 是必经点 $\iff$ 在图 $G$ 中删去结点 $u$ 后，**不存在**任何一条从某个合法起点到某个合法终点的路径。
2. **高效暴力检验算法**：
   由于数据范围较小（$n \le 1000, m \le 2000$），我们可以针对每个待选结点 $u \in [1, n]$ 单独测试：
   - 将所有起点 $s \in S \setminus \{u\}$ 入队，在无结点 $u$ 的残留图上执行多源 BFS/DFS；
   - 若遍历过程中访问到了任何一个终点 $t \in T \setminus \{u\}$，说明存在避开 $u$ 的路径，故 $u$ 不是必经点；
   - 若遍历结束未访问到任何合法终点，则证明所有合法路径都依赖 $u$，因此 $u$ 是必经点！
3. **复杂度分析**：
   单次 BFS 耗时 $\mathcal{O}(n + m)$，枚举 $n$ 个点总耗时 $\mathcal{O}(n(n + m)) \approx 1000 \times 3000 = 3 \times 10^6$ 次操作，耗时约 $20\text{ ms}$，极度稳健。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-P17459
 * Standard: C++11 (CCF GESP 官方大纲规范)
 * Author: OneCoder
 */

#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    if (!(cin >> n >> m)) return 0;

    vector<vector<int>> adj(n + 1);
    vector<int> in_deg(n + 1, 0);
    vector<int> out_deg(n + 1, 0);

    for (int i = 0; i < m; ++i) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        out_deg[u]++;
        in_deg[v]++;
    }

    vector<int> starts;
    vector<bool> is_end(n + 1, false);

    for (int i = 1; i <= n; ++i) {
        if (in_deg[i] == 0) starts.push_back(i);
        if (out_deg[i] == 0) is_end[i] = true;
    }

    vector<int> must_pass;

    // 逐个检验结点 u 是否为必经点
    for (int u = 1; u <= n; ++u) {
        queue<int> q;
        vector<bool> visited(n + 1, false);

        for (int s : starts) {
            if (s != u) {
                visited[s] = true;
                q.push(s);
            }
        }

        bool can_reach_end = false;

        while (!q.empty()) {
            int curr = q.front();
            q.pop();

            if (is_end[curr] && curr != u) {
                can_reach_end = true;
                break;
            }

            for (int nxt : adj[curr]) {
                if (nxt != u && !visited[nxt]) {
                    visited[nxt] = true;
                    q.push(nxt);
                }
            }
        }

        if (!can_reach_end) {
            must_pass.push_back(u);
        }
    }

    cout << must_pass.size() << "\n";
    if (!must_pass.empty()) {
        for (size_t i = 0; i < must_pass.size(); ++i) {
            cout << must_pass[i] << (i + 1 == must_pass.size() ? "" : " ");
        }
        cout << "\n";
    }

    return 0;
}
```
