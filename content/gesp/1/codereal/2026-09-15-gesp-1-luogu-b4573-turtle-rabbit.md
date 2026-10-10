---
layout: post
title: "B4573 新龟兔赛跑"
linkTitle: "B4573 新龟兔赛跑"
date: 2026-09-15T15:01:00+0800
author: OneCoder
comments: true
tags:
- GESP
- C++
- GESP一级
- 分支结构
- 浮点数
- 格式化输出
- 真题
- 2026年9月
- GESP202609
categories:
- GESP
- 一级
- 基础语法
slug: gesp-1-luogu-b4573-turtle-rabbit
type: docs
weight: 30
math: true
---


CCF GESP 2026年9月认证（第十五次认证）C++ 一级编程题第一题，洛谷 B4573。本题紧密围绕 CCF GESP 一级大纲核心考点，重点考察**基础浮点数除法计算（$t = s / v$）**、**变量累加**、**多分支 `if / else if / else` 条件判断**以及**浮点数保留两位小数的格式化输出**。题目贴合经典童话寓言背景，逻辑清晰，是检验编程启蒙阶段基本语法掌握度的优质试题。题目难度等级为`入门`（难度评级★☆☆☆☆）。

<!--more-->

## B4573 [GESP202609 一级] 新龟兔赛跑

> 🔗 **洛谷原题传送门**：[luogu-B4573 [GESP202609 一级] 新龟兔赛跑](https://www.luogu.com.cn/problem/B4573)

### 题目描述

自从上次龟兔赛跑，兔子因为轻敌而惨败后，一直心有不甘，因此有了新一届龟兔赛跑。

乌龟和上次一样，将会以恒定的速度往终点爬行，题目将给出乌龟从起点到终点所需时间；

兔子并没有吸取教训，只是打算在终点前少睡一会儿，题目将给出兔子的速度，和兔子打算在终点前睡觉的时间；

起点和终点之间的距离固定为 $1000.0$，请帮忙计算乌龟和兔子谁会获胜？

### 输入格式

输入包含 3 行，每行一个浮点数：

* 第 1 行的浮点数表示乌龟从起点到终点所需时间；
* 第 2 行的浮点数表示兔子的速度；
* 第 3 行的浮点数表示兔子打算在终点前睡觉的时间。

### 输出格式

输出包含 2 行：

* 第 1 行，如果乌龟获胜，输出 `turtle`；如果兔子获胜，输出 `rabbit`；如果平局，输出 `tie`；
* 第 2 行，输出兔子到达终点所需的总时间（含兔子睡觉的时间），保留两位小数。

### 输入输出样例

#### 输入 #1

```text
20.0
100.0
11.0
```

#### 输出 #1

```text
turtle
21.00
```

#### 输入 #2

```text
20.0
100.0
9.0
```

#### 输出 #2

```text
rabbit
19.00
```

### 说明/提示

#### 样例解释 1

兔子跑完全程所需时间是 $1000.0 \div 100.0 = 10.0$，而兔子要睡觉 $11.0$ 单位时间，所以兔子一共需要 $21.0$ 单位时间才能到达终点，这大于乌龟所需时间。

#### 样例解释 2

与样例 1 类似，兔子跑完全程所需时间是 $1000.0 \div 100.0 = 10.0$，但兔子仅睡觉 $9.0$ 单位时间，所以兔子一共需要 $19.0$ 单位时间就能到达终点，这小于乌龟所需时间。

#### 数据范围

所有输入均有且仅有一位小数，且是不超过 $1000.0$ 的正数。

本题默认给出的数值均为龟兔世界中的标准单位，不需要进行任何单位换算。

路程 $=$ 速度 $\times$ 时间

---

### 题目分析与核心考点

#### 1. 物理公式与总时间拆解

赛跑模型遵循经典运动学公式：

$$\text{时间} = \frac{\text{路程}}{\text{速度}}$$

- **路程（$S$）**：题目明确固定为常量 $1000.0$；
- **乌龟总时间（$T_{\text{turtle}}$）**：输入第 1 行直接给出，无需额外计算；
- **兔子总时间（$T_{\text{rabbit}}$）**：由两部分组成：
  1. 纯奔跑时间：$t_{\text{run}} = \frac{1000.0}{v_{\text{rabbit}}}$；
  2. 睡觉时间：$t_{\text{sleep}}$（输入第 3 行给出）。
  因此：
  $$T_{\text{rabbit}} = \frac{1000.0}{v_{\text{rabbit}}} + t_{\text{sleep}}$$

#### 2. 胜负判定逻辑

赛跑胜负的准则是：**谁用时少，谁先到达终点，谁获胜**。

- 若 $T_{\text{turtle}} < T_{\text{rabbit}}$：乌龟用时更少，乌龟获胜，输出 `turtle`；
- 若 $T_{\text{rabbit}} < T_{\text{turtle}}$：兔子用时更少，兔子获胜，输出 `rabbit`；
- 若 $T_{\text{turtle}} = T_{\text{rabbit}}$：两者同时到达，平局，输出 `tie`。

#### 3. C++ 格式化输出规范

根据输出要求，第 2 行必须输出兔子总耗时且**保留两位小数**。在 C++（严格遵循 GESP 考纲要求的 C++11 标准）中，推荐引入 `<iomanip>` 头文件：

```cpp
#include <iomanip>

cout << fixed << setprecision(2) << rabbit_total_time << "\n";
```

- `fixed`：指定浮点数以定点形式输出（避免极大或极小数退化为科学计数法）；
- `setprecision(2)`：精确锁定小数点后输出 2 位数字，自动执行四舍五入对齐。

---

### 完整参考代码 (C++11)

```cpp
/**
 * Problem: luogu-B4573 [GESP202609 一级] 新龟兔赛跑
 * Standard: C++11 (CCF GESP 官方大纲推荐标准)
 * Author: OneCoder
 */

#include <iostream>
#include <iomanip>

using namespace std;

int main() {
    // 基础流加速
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    // 定义双精度浮点型变量，输入乌龟时间、兔子速度、兔子睡眠时间
    double turtle_time = 0.0;
    double rabbit_speed = 0.0;
    double rabbit_sleep = 0.0;

    if (!(cin >> turtle_time >> rabbit_speed >> rabbit_sleep)) {
        return 0;
    }

    // 常量定义：全程固定距离 1000.0
    const double DISTANCE = 1000.0;

    // 1. 计算兔子纯奔跑时间与总耗时
    double rabbit_run_time = DISTANCE / rabbit_speed;
    double rabbit_total_time = rabbit_run_time + rabbit_sleep;

    // 2. 第一行：判定胜负（时间短者获胜）
    if (turtle_time < rabbit_total_time) {
        cout << "turtle\n";
    } else if (rabbit_total_time < turtle_time) {
        cout << "rabbit\n";
    } else {
        cout << "tie\n";
    }

    // 3. 第二行：格式化输出兔子总耗时，保留两位小数
    cout << fixed << setprecision(2) << rabbit_total_time << "\n";

    return 0;
}
```

---

### 复杂度分析

- **时间复杂度**：$\mathcal{O}(1)$。程序只涉及常数次基本四则运算与多分支比较，耗时小于 $1\text{ ms}$，瞬间完成。
- **空间复杂度**：$\mathcal{O}(1)$。只开辟了若干标量 `double` 变量，内存消耗不足几字节，远低于题目给定的 $512\text{ MB}$ 限制。

---

### 考点归纳与避坑提醒

1. **类型选用**：输入含有一位小数，计算涉及除法，因此必须全部使用浮点型 `double`，切忌使用整型 `int` 截断小数部分导致精度丢失；
2. **胜负条件正反向**：在赛跑比赛中，“数值更小”代表速度更快、成绩更好，切勿把条件写反成大于号；
3. **平局特判**：分支结构必须完整包含 `turtle`、`rabbit` 和 `tie` 三种互斥状态，养成写完 `if` 和 `else if` 后补充 `else` 处理边界兜底的优秀编码习惯。
