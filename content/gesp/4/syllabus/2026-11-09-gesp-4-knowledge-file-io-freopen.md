---
layout: post
title: "文件读写(freopen)与缓冲区机制"
linkTitle: "文件读写(freopen)与缓冲区机制"
date: 2026-11-09T08:00:00+0800
author: OneCoder
comments: true
categories:
- GESP
- 四级
tags:
- GESP
- CSP-J
- C++
- 考点精讲
slug: gesp-4-knowledge-file-io-freopen
type: docs
weight: 116
math: true
---

为什么每年 CSP-J/S 第二轮复赛成绩公布后，总有一大批平时模拟赛能拿二三百高分的选手，打开成绩单却看到刺眼的 **4 题全 0 分（爆零）**？为什么你的算法逻辑完美无缺、本地小样例全过，仅仅因为在交卷前忘记删掉 `// freopen("apple.in", "r", stdin);` 前面的两道斜杠 `//`，或者把 `"apple.in"` 顺手写成了 `"apple1.in"`、`"apple.txt"`，评测机就直接判定全盘零分？而在 GESP 四级客观题与阅读程序题中，当一段程序抛出 `throw -1;` 或 `throw runtime_error("err");` 时，为什么紧跟在 `throw` 后面的 `cout` 语句会像人间蒸发一样永远无法执行，控制流瞬间跨越数层函数直接跳进匹配的 `catch` 块？在 GESP 四级认证以及 CSP-J/S 复赛实战中，**标准输入输出流（`stdin` / `stdout`）的管道重定向原理、`freopen` 文件读写模式 `"r"` 与 `"w"` 的黄金铁律、输出缓冲区（Output Buffer）的刷新机制，以及 C++ 异常捕获（`try-throw-catch`）的栈展开（Stack Unwinding）控制流**，是决定考场生死存亡的底线工程规范。本文将带你从操作系统文件描述符与缓冲区的底层视角，彻底扫清文件读写与异常处理的所有盲区。

<!--more-->

## 🎯 考纲锚点与核心痛点

> 📍 **对应考点**：掌握 C/C++ 文件读写操作与标准流重定向函数 `freopen` 的参数规范（`"r"` 只读模式、`"w"` 只写覆写模式、`stdin` / `stdout` 流指针）及 I/O 缓冲区机制；理解 C++ 异常处理结构（`try`、`throw`、`catch`）的执行流跳转规则与类型匹配机制。
> 🎯 **适用等级**：`GESP 四级考点 | CSP-J/S 初赛/复赛必考`

在考场做客观题、阅读程序和参加 CSP-J/S 复赛上机时，同学们最容易在以下三个地方栽跟头：
1. **“CSP-J/S 复赛 `freopen` 四大爆零惨案”**：① 本地调试时注释了 `// freopen(...)` 或重定向到了测试样例文件 `"apple1.in"`，交卷前忘还原；② 把第二个模式参数单双引号搞混，写成字符 `'r'`（编译报错或指针非法访问），或把 `stdin` 和 `"w"` 错误配对；③ 在 Windows 资源管理器隐藏已知文件扩展名的情况下，把数据文件建成了 `apple.in.txt` 却浑然不知；④ 先读入了一个变量 `cin >> n;`，后面才想起来写 `freopen`，导致第一个关键数据读空；
2. **“误以为 `cout` 或 `printf` 执行完就立刻写进了磁盘文件”**：不知道操作系统为了减少磁盘磁头寻道开销，设立了**输出缓冲区（Output Buffer）**——如果程序在后面发生了除以 `0` 或数组越界崩溃（RE），留在内存缓冲区里还没来得及刷入（Flush）磁盘的数据会瞬间全部丢失，导致看到的 `.out` 文件一片空白；
3. **“搞不清 `try-throw-catch` 的跳转时机与严格类型匹配”**：误以为 `throw` 像普通函数调用一样执行完还会回到原位置继续往下走，或者以为 `catch (double e)` 也能顺便接住 `throw 10;` 抛出的 `int` 类型异常（实际上 `catch` 块的匹配**不进行常规算术隐式类型转换**，接不住就会触发 `std::terminate()` 强行终止程序）。

---

## 🧠 一、 核心原理深度拆解（有理论）

### 1. 什么是“标准流重定向”？一张管道图看懂 `freopen` 的底层魔法

在平时做洛谷或 GESP 在线编程题（OJ 模式）时，我们直接写 `cin >> a;` 和 `cout << a;`，从来不用操心文件。这是因为每一个 C++ 程序启动时，操作系统都会自动为它接通**三条默认的工业数据管道（标准流）**：
* **`stdin`（Standard Input，标准输入流）**：默认连接你的**键盘**；`cin` 和 `scanf` 本质上都是从 `stdin` 这根管道里抽水；
* **`stdout`（Standard Output，标准输出流）**：默认连接你的**显示器屏幕（控制台黑框）**；`cout` 和 `printf` 都是往 `stdout` 这根管道里注水；
* **`stderr`（Standard Error，标准错误流）**：默认也连接**显示器屏幕**，专门用来输出报错与调试信息（对应 `cerr`）。

而在 **CSP-J/S、NOIP 等传统 NOI 系列复赛**中，评测机在后台批改你的程序时，根本不会派一个机器人去敲键盘，也不会拿摄像头去拍屏幕！评测机只做一件事：**把测试数据放在当前目录的 `<题目英文名>.in` 文件里，运行你的程序，然后去检查当前目录下生成的 `<题目英文名>.out` 文件内容是否正确！**

如果让你把代码里成百上千处的 `cin` / `cout` 全部改成 `ifstream` / `ofstream`，既繁琐又容易改错。为此，头文件 `<cstdio>` 提供了神器 **`freopen`（File Re-open，文件流重新打开/重定向）**——它就像一个**管道扳手**，在不改动后面任何一行 `cin`/`cout`/`scanf`/`printf` 代码的前提下，直接把 `stdin` 的进水口从“键盘”拧到 `.in` 磁盘文件上，把 `stdout` 的出水口从“屏幕”拧到 `.out` 磁盘文件上！

```text
================================================================================
【默认模式（不加 freopen）】—— GESP 线上编程题 / 日常 OJ 刷题
   [ 键盘输入 ] ═══► ( stdin 管道 )  ═══► cin / scanf  ═══► 【你的 C++ 程序】
   [ 屏幕黑框 ] ◄═══ ( stdout 管道 ) ◄═══ cout / printf ◄═══ 【你的 C++ 程序】
--------------------------------------------------------------------------------
【文件重定向模式（加上 freopen）】—— CSP-J/S 复赛 / NOIP 考场强制要求
   执行：freopen("apple.in", "r", stdin);
         freopen("apple.out", "w", stdout);

   [ 键盘输入 ] ─── (已断开 ❌)
   [ 磁盘文件 apple.in  ] ═══► ( stdin 管道 )  ═══► cin / scanf  ═══► 【你的程序】
   [ 磁盘文件 apple.out ] ◄═══ ( stdout 管道 ) ◄═══ cout / printf ◄═══ 【你的程序】
   [ 屏幕黑框 ] ◄───────────── ( stderr 管道 ) ◄═══ cerr (唯一还能往屏幕打印的通道!)
================================================================================
```

---

### 2. `freopen` 函数的三大参数与常用模式表

在 `<cstdio>` 头文件中，`freopen` 的标准函数原型为：
```cpp
FILE *freopen(const char *filename, const char *mode, FILE *stream);
```
我们在 `main()` 函数的**最开头第一行、第二行**固定写下这两句黄金咒语：

```cpp
freopen("title.in", "r", stdin);
freopen("title.out", "w", stdout);
```

三个参数必须严丝合缝，错一个字母就是 0 分：

| 参数位置 | 输入重定向写法 | 输出重定向写法 | 参数底层含义与考场铁律 |
| :---: | :---: | :---: | :--- |
| **第 1 参数**<br>`filename` | `"title.in"` | `"title.out"` | **目标文件名字符串（双引号）**：严格对照试卷首页表格中的“输入文件名 / 输出文件名”，**全小写**，绝不能带路径（如 `D:\title.in` 必爆零），也绝不能写成 `"title1.in"`！ |
| **第 2 参数**<br>`mode` | **`"r"`**<br>*(Read 只读)* | **`"w"`**<br>*(Write 只写覆写)* | **打开模式字符串（必须是双引号 `""`，严禁单引号 `''`）**：<br>• `"r"`：以只读方式打开已存在的文件（若文件不存在则返回 `NULL` 失败）；<br>• `"w"`：以只写方式打开文件（若文件不存在则**自动新建**；若文件已存在则**瞬间清空原有内容**从头写入）；<br>• `"a"`：追加模式（Append，在文件末尾接着写，考场不用，但初赛客观题常考）。 |
| **第 3 参数**<br>`stream` | **`stdin`** | **`stdout`** | **被重定向的标准流指针**：读文件对应 `stdin`（标准输入），写文件对应 `stdout`（标准输出）。切记不可将 `"r"` 与 `stdout` 乱配！ |

---

### 3. 为什么程序崩溃（RE）会导致 `.out` 文件一片空白？（I/O 缓冲区机制）

很多同学在考场调试时遇到过一个极其诡异的现象：自己在循环里写了 `printf("step %d\n", i);` 想看看程序是在哪一步数组越界崩溃的，结果程序崩溃退出后，打开 `title.out` 文件一看——**里面竟然一个字都没有（0 字节）**！于是误以为程序连第一轮循环都没进去！

#### 🔍 揭秘操作系统与 C/C++ 的“输出缓冲区（Output Buffer）”
磁盘（硬盘）的读写速度比内存慢成千上万倍。如果程序每执行一次 `cout << x;` 就让操作系统立刻驱动硬盘写一次文件，程序就会慢如蜗牛。因此，C/C++ 标准库在内存里开辟了一块**输出缓冲区（通常为 $4\text{ KB}$ 或 $8\text{ KB}$ 的内存暂存池）**：
1. 当你调用 `cout` 或 `printf` 时，字符只是先被放进了**内存缓冲区**里排队，并没有真正写进磁盘上的 `.out` 文件；
2. 只有触发以下**四大刷新（Flush）条件之一**时，缓冲区里的数据才会真正落盘写入 `.out` 文件：
   * **程序正常执行到 `return 0;` 结束**（C++ 运行时库会自动调用 `fclose` 将所有残留缓冲区刷入磁盘）；
   * **缓冲区被塞满了**（达到 $4\text{ KB}/8\text{ KB}$ 上限，自动倾倒一次）；
   * **显式调用了刷新指令**：如 **`cout << endl;`**（`endl` 不仅输出换行符 `'\n'`，还会强制执行 `flush` 刷新缓冲区！而单输出 `'\n'` 在文件重定向的全缓冲模式下不会立即落盘）或 **`fflush(stdout);`**；
   * **程序正常调用 `fclose(stdout);`** 关闭文件流。

> ⚠️ **破案了**：如果你的全篇输出用的都是 `printf("...\n")` 或 `cout << "...\n"`，且总输出量不到 $4\text{ KB}$，一旦程序在跑到 `return 0;` 之前因为**除以 `0` 或数组越界触发了段错误（RE）被操作系统强行杀死**，内存缓冲区里攒着的所有答案就会随进程灰飞烟灭，`.out` 文件自然一片空白！

---

### 4. GESP 四级必考：异常处理机制（`try - throw - catch`）

除了文件流操作，GESP 四级考纲明确要求掌握 C++ 的**结构化异常处理（Exception Handling）**。当程序在运行期遇到“除数为 `0`”、“数组下标非法”、“内存分配失败”等无法在当前函数内部处理的危机时，可以通过三个关键字完成**跨函数的紧急避险跳转**：

```cpp
#include <iostream>
#include <stdexcept> // 标准异常类头文件（如 runtime_error, out_of_range）
using namespace std;
```

#### ① 三大关键字的分工与“栈展开（Stack Unwinding）”铁律
* **`try { ... }`（监控保护区）**：把可能出现运行期错误的代码段（或函数调用）包裹在 `try` 花括号内进行实时监控；
* **`throw 表达式;`（抛出异常信号弹）**：一旦检测到错误（如 `if (b == 0) throw -1;`），立即发射一枚异常对象。
  * **⚡ 铁律 A（瞬间截断）**：`throw` 语句一旦执行，**当前函数内位于 `throw` 下方的所有代码全部作废、绝不执行**！控制流立刻中断当前函数，沿着函数调用栈向上层层回退（这个过程叫**栈展开 Stack Unwinding**，沿途局部对象会被自动析构），直接寻找外层最近的 `try` 块；
* **`catch (类型 形参) { ... }`（异常捕手）**：紧跟在 `try` 块后面（可以并联多个不同参数类型的 `catch` 块）。
  * **⚡ 铁律 B（自上而下、严格类型匹配）**：异常抛出后，会按从上到下的顺序逐个比对 `catch` 块的形参类型。注意：**这里绝不进行普通算术类型的隐式转换**！例如 `throw 404;`（抛出 `int`）**绝对不会被 `catch (double e)` 或 `catch (long long e)` 捕获**！只能被 `catch (int e)` 或兜底的万能捕手 **`catch (...)`**（三个英文句点，捕获任意类型异常）接住；
  * **⚡ 铁律 C（无人捕获即崩溃）**：如果找遍整个调用栈都没有匹配的 `catch` 块，C++ 会自动调用系统函数 `std::terminate()` 强行终止程序（表现为考场上的 **RE**）。

> 💡 **考场黄金法则（背诵直接套用）**：
> 1. **【复赛 `freopen` 保命口诀】**：**“头文件必加 `<cstdio>`，进 `main` 头两行写死 `freopen("题名.in", "r", stdin);` 与 `freopen("题名.out", "w", stdout);`；交卷前查三遍：注释删没删？题名对不对？是不是双引号 `"r"` 和 `"w"`？”**
> 2. **【`try-catch` 阅读程序口诀】**：**“`throw` 之后全跳过，直奔 `catch` 看类型；算术类型不隐转，`catch(...)` 兜底接万物，接完继续往下走！”**

---

## 🔍 二、 具象代码与数据推演（有举例）

### 示例 1：CSP-J/S 复赛满分标准骨架（含 `freopen` 与本地调试条件编译技巧）

很多同学问：“平时在本地想用键盘输入测小样例，怎么避免交卷时忘记把 `// freopen` 取消注释？”
除了养成交卷前最后 10 分钟统一用文件测大样例的铁律外，下面展示最标准的复赛代码骨架：

```cpp
#include <iostream>
#include <cstdio> // ⚠️ 使用 freopen 必须包含 <cstdio> 头文件！
using namespace std;

int main() {
    // 1. 进 main 第一件事：重定向标准输入输出流（严禁在此之前 cin 任何数据！）
    freopen("apple.in", "r", stdin);
    freopen("apple.out", "w", stdout);

    // 2. 后续代码完全照常使用 cin / cout，它们会自动从 apple.in 读、往 apple.out 写
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;

    // 3. 正常返回 0，系统自动刷新缓冲区并关闭文件
    return 0;
}
```

---

### 示例 2：`try - throw - catch` 跨函数跳转与多分支匹配推演

阅读下面这段标准 C++11 程序，观察当数组元素依次为 `{45, -5, 120, 30}` 时，程序是如何在正常流与两个不同 `catch` 分支之间精准切换的：

```cpp
#include <iostream>
#include <cstdio>
#include <stdexcept>
using namespace std;

int check_score(int x) {
    if (x < 0) {
        throw -1; // 抛出 int 类型异常，下方代码直接跳过！
    }
    if (x > 100) {
        throw runtime_error("OVERFLOW"); // 抛出标准库异常对象
    }
    return x * 2;
}

int main() {
    int a[4] = {45, -5, 120, 30};
    for (int i = 0; i < 4; i++) {
        try {
            int res = check_score(a[i]);
            cout << "OK:" << res << " ";
        } catch (int code) {
            cout << "NEG:" << code << " ";
        } catch (const runtime_error &e) {
            cout << "ERR:" << e.what() << " ";
        }
    }
    cout << endl;
    return 0;
}
```

### 异常控制流分步追踪表

| 循环轮次 `i` | 传入实参 `a[i]` | `check_score` 内部执行情况 | `try` 块剩余语句 (`cout << "OK:"...`) | 命中的 `catch` 分支 | 本轮实际打印输出 |
| :---: | :---: | :--- | :---: | :---: | :--- |
| **`i = 0`** | `45` | 两个 `if` 均不满足，正常返回 `45 * 2 = 90` | **正常执行** | 无异常，跳过所有 `catch` | **`OK:90 `** |
| **`i = 1`** | `-5` | 触发 `x < 0`，执行 **`throw -1;`**（抛出 `int`），函数瞬间中断返回！ | **被直接跳过 ❌** | 命中第 1 个：<br>`catch (int code)` | **`NEG:-1 `** |
| **`i = 2`** | `120` | 触发 `x > 100`，执行 **`throw runtime_error("OVERFLOW");`**，函数瞬间中断！ | **被直接跳过 ❌** | 跳过 `int`，命中第 2 个：<br>`catch (const runtime_error &e)` | **`ERR:OVERFLOW `** |
| **`i = 3`** | `30` | 上一轮异常已被捕获处理完毕，循环继续！正常返回 `30 * 2 = 60` | **正常执行** | 无异常，跳过所有 `catch` | **`OK:60 `** |
| **汇总输出** | — | — | — | — | **`OK:90 NEG:-1 ERR:OVERFLOW OK:60`** |

---

## ⚡ 三、 考场高频避坑指南（正误辨析）

在 GESP 四级真题与 CSP-J 考场上，以下三个陷阱每年都会收割大量分数：

### ❌ 易错点 1：在 `freopen` 之前提前执行了 `cin`，或把文件名写成带编号的样例名
* **错误写法 A（先读入后重定向）**：
  ```cpp
  int n;
  cin >> n; // 致命错误！此时还没写 freopen，程序死等键盘输入，直接 TLE / 读入垃圾值！
  freopen("bus.in", "r", stdin);
  freopen("bus.out", "w", stdout);
  ```
* **错误写法 B（直接照抄大样例文件名）**：下发的大样例文件叫 `bus1.in`、`bus2.in`，选手为了测试把代码改成了 `freopen("bus2.in", "r", stdin);`，测完直接交卷！
* **为什么错**：评测机目录下只有标准名字 **`bus.in`**！去找 `bus2.in` 必定打开失败返回 `NULL`，后续所有 `cin` 全部失效，10 个测试点全盘 **0 分**！
* **正确做法**：`freopen` 必须雷打不动地焊死在 `main()` 函数的**第一行和第二行**！测试大样例时，把下发的 `bus2.in` 复制重命名为 `bus.in` 来测，**永远不要去改代码里的 `"bus.in"` 字符串**！

### ❌ 易错点 2：把 `freopen` 的模式参数写成单引号字符 `'r'`，或忘记包含 `<cstdio>`
* **错误写法**：
  ```cpp
  #include <iostream> // 漏了 #include <cstdio>！
  using namespace std;
  int main() {
      freopen("game.in", 'r', stdin); // 致命错误：把双引号 "r" 写成了单引号 'r'！
  }
  ```
* **为什么错**：
  1. 在某些本地旧版 IDE 中，`<iostream>` 可能会间接包含 `<cstdio>` 让你侥幸编译通过，但在 CCF 标准 NOI Linux 评测机（GCC 编译器）下，不写 `#include <cstdio>` 直接调 `freopen` 极易触发 **编译错误（CE：`freopen was not declared in this scope`）**；
  2. `freopen` 的第二个参数类型是 `const char*`（C 风格字符串首地址），必须用**双引号 `"r"`**；如果写成单引号 `'r'`（ASCII 码为整数 `114`），会直接导致类型不匹配编译报错（CE）。
* **正确写法**：包含 `#include <cstdio>`，模式参数严格使用双引号 `"r"` 和 `"w"`。

### ❌ 易错点 3：误以为 `catch (double)` 能自动隐式转换接住 `throw 1`（`int` 异常）
* **错误认知**：在普通函数调用 `void func(double x)` 中，传入整数 `func(1)` 会自动把 `int` 隐式提升为 `double(1.0)`。于是很多同学在做阅读程序题时认为：
  ```cpp
  try {
      throw 1; // 抛出的是 int 常量 1
  } catch (double d) {
      cout << "Caught double: " << d << endl;
  }
  ```
  也能顺利进入 `catch (double d)` 分支。
* **为什么错**：C++ 标准严格规定：**异常捕获的 `catch` 类型匹配绝不执行算术类型的隐式转换（No arithmetic conversions）**！`throw 1;` 抛出的精确类型是 `int`，而下面的捕手只有 `double`，两者类型不匹配！程序会直接越过这个 `catch` 块，最终因为无人捕获而调用 `std::terminate()` 异常崩溃！
* **正确认知**：抛出 `int` 就必须用 `catch (int)`（或 `const int&`、兜底的 `catch (...)`）来捕获；抛出字符串字面量 `throw "error";` 则必须用 `catch (const char* msg)` 来捕获。

---

## 📝 四、 真题实战演练与精析（有例题：3 道）

### 【例题 1 · 单选题】（GESP 四级 / CSP-J 初赛高频题：`freopen` 参数规范与 `try-catch` 输出预测）

**题目**：阅读以下 C++11 程序片段，请问关于文件流操作与异常捕获的说法正确，且该程序在标准控制台运行后的输出结果是（ ）。
```cpp
#include <iostream>
#include <cstdio>
using namespace std;

void calc(int k) {
    if (k == 0) {
        throw 404;
        cout << "AfterThrow ";
    }
    cout << 10 / k << " ";
}

int main() {
    try {
        calc(2);
        calc(0);
        calc(5);
    } catch (double e) {
        cout << "Double:" << e << " ";
    } catch (int e) {
        cout << "Int:" << e << " ";
    }
    cout << "End" << endl;
    return 0;
}
```
* **A.** `5 AfterThrow Int:404 2 End`
* **B.** `5 Double:404 End`
* **C.** `5 Int:404 End`
* **D.** `5 Int:404 2 End`

**🔍 答案与逐项排除解析**：
* **正确答案**：**C**
* **解析过程**：
  1. **第一步执行 `calc(2);`**：在 `calc` 函数中 `k = 2 != 0`，正常计算 `10 / 2` 并输出 **`5 `**，函数顺利返回 `try` 块。
  2. **第二步执行 `calc(0);`**：在 `calc` 函数中触发 `k == 0`，立即执行 **`throw 404;`**（抛出一个 `int` 类型的异常值 `404`）：
     * 根据“瞬间截断铁律”，`throw 404;` 下方的 `cout << "AfterThrow ";` 和 `cout << 10 / k;` **全部被跳过不执行**（直接**排除 A**）；
     * 同时，回到 `main` 函数的 `try` 块后，位于 `calc(0);` 下方的 **`calc(5);` 也会因为异常中断而被彻底跳过，绝不会再回来执行**（直接**排除 D**）。
  3. **第三步匹配 `catch` 块**：抛出的 `404` 是 `int` 类型。首先检查第一个捕手 `catch (double e)`——由于异常处理**不进行 `int` 到 `double` 的算术隐式转换**，第一个 `catch` 匹配失败跳过（**排除 B**）；接着检查第二个捕手 `catch (int e)`，精确匹配成功！输出 **`Int:404 `**。
  4. **第四步收尾**：异常已被成功消化处理，程序脱离 `try-catch` 结构继续向下正常执行 `cout << "End" << endl;`，输出 **`End`**。故最终完整输出为 **`5 Int:404 End`**，选 **C**。

---

### 【例题 2 · 判断题】（GESP 四级官方考纲辨析：`freopen` 读写模式与文件创建行为）

**题目**：在 C++ 程序中需要将数据写入同目录下的 `result.out` 文件时，使用语句 `freopen("result.out", "w", stdout);` 重定向标准输出流。如果程序运行前磁盘当前目录下并**不存在** `result.out` 这个文件，那么 `freopen` 函数会因为找不到文件而打开失败并返回空指针 `NULL`。（ ）

**🔍 答案与反例证明**：
* **结论**：**错误（$\times$）**
* **反例证明**：本题精准考察 `freopen` 中只读模式 `"r"` 与只写模式 `"w"` 的核心区别：
  * 当第二个参数为**只读模式 `"r"`**（如 `freopen("data.in", "r", stdin);`）时，要求目标文件必须已经存在；如果文件不存在，确实会打开失败并返回 `NULL`；
  * 但当第二个参数为**只写模式 `"w"`**（Write）时，操作系统的底层规则是：**如果目标文件 `result.out` 不存在，则自动在当前目录下新建一个名为 `result.out` 的空文件**；如果该文件已经存在，则将其原有内容全部清空（截断为 0 字节）并从头开始写入！因此 `"w"` 模式下文件不存在绝不会报错失败，而是会自动创建新文件。故原命题错误。

---

### 【例题 3 · 微代码实战】（GESP 四级考纲综合实战：带多重异常捕获的安全整除校验器）

**题目描述**：在开发自动化评测脚本时，我们需要对 $n$（$1 \le n \le 100$）组整数除法运算 $a \div b$ 进行安全审计。请你编写一个函数 `int safe_divide(int a, int b)` 并配合 `main` 函数中的 `try-catch` 结构完成校验：
1. 若除数 $b = 0$，属于致命算术错误，请在 `safe_divide` 函数中直接执行 `throw -1;`（抛出 `int` 类型错误码）；
2. 若 $b \neq 0$ 但 $a$ 不能被 $b$ 整除（即 `a % b != 0`），属于精度截断警告，请执行 `throw runtime_error("NOT_EXACT");`（抛出 `<stdexcept>` 中的标准运行时异常对象）；
3. 若 $b \neq 0$ 且 $a$ 能被 $b$ 整除，则正常返回商 `a / b`。

在 `main` 函数中，请依次对每组 $(a, b)$ 调用 `safe_divide(a, b)`：
* 若未发生异常，输出一行 `OK ` 加上计算出的商，并将该商累加到有效商总和 `total_sum` 中，同时有效组数 `valid_cnt` 加 $1$；
* 若捕获到 `int` 类型异常，输出一行 `ERR_DIV_ZERO`；
* 若捕获到 `const runtime_error&` 类型异常，输出一行 `ERR_REMAINDER`。
所有 $n$ 组数据处理完毕后，在最后一行输出有效组数 `valid_cnt` 与有效商总和 `total_sum`（以单个空格分隔）。

**输入格式**：
第一行包含一个正整数 $n$，表示待校验的除法运算组数。
接下来 $n$ 行，每行包含两个整数 $a$ 和 $b$（$-10^6 \le a, b \le 10^6$），以空格分隔。

**输出格式**：
前 $n$ 行依次输出每组数据的校验结果（`OK 商`、`ERR_DIV_ZERO` 或 `ERR_REMAINDER`）。
第 $n + 1$ 行输出两个整数，分别表示有效整除组数 `valid_cnt` 和有效商总和 `total_sum`，以单个空格分隔。

**💡 建模思路**：
1. **异常抛出设计**：在 `safe_divide(int a, int b)` 中，必须**先判断 `b == 0`** 并 `throw -1;`！因为如果在 `b == 0` 时先去算 `a % b != 0`，CPU 执行取模指令 `a % 0` 会当场触发硬件级除零崩溃（Floating point exception），根本来不及进 `throw`！
2. **多捕手并联拦截**：在 `for` 循环内部放置 `try { ... }` 块（这样某一组抛出异常被捕获后，下一轮循环仍能继续正常执行）。下方依次挂载 `catch (int err_code)` 拦截除零错误，挂载 `catch (const runtime_error &e)` 拦截余数非零错误；
3. **累加防溢出**：有效商总和 `total_sum` 声明为 `long long` 并初始化为 `0`，确保累加安全。

```cpp
#include <iostream>
#include <cstdio>
#include <stdexcept>
using namespace std;

int safe_divide(int a, int b) {
    if (b == 0) {
        throw -1;
    }
    if (a % b != 0) {
        throw runtime_error("NOT_EXACT");
    }
    return a / b;
}

int main() {
    // 💡 提示：若在 CSP-J 复赛考场，只需取消下面两行注释即可切换为文件读写：
    // freopen("divide.in", "r", stdin);
    // freopen("divide.out", "w", stdout);

    int n;
    cin >> n;
    int valid_cnt = 0;
    long long total_sum = 0;
    for (int i = 1; i <= n; i++) {
        int a, b;
        cin >> a >> b;
        try {
            int q = safe_divide(a, b);
            cout << "OK " << q << endl;
            valid_cnt++;
            total_sum += q;
        } catch (int err_code) {
            cout << "ERR_DIV_ZERO" << endl;
        } catch (const runtime_error &e) {
            cout << "ERR_REMAINDER" << endl;
        }
    }
    cout << valid_cnt << " " << total_sum << endl;
    return 0;
}
```

* **输入样例 1**：
  ```text
  5
  20 4
  15 0
  17 5
  -18 6
  0 9
  ```
* **输出样例 1**：
  ```text
  OK 5
  ERR_DIV_ZERO
  ERR_REMAINDER
  OK -3
  OK 0
  3 2
  ```
  *（样例 1 解释：第 1 组 $20 \div 4 = 5$ 整除成功，输出 `OK 5`；第 2 组除数为 $0$，触发 `throw -1` 被 `catch (int)` 捕获，输出 `ERR_DIV_ZERO`；第 3 组 $17 \div 5$ 余 $2$，触发 `runtime_error` 异常，输出 `ERR_REMAINDER`；第 4 组 $-18 \div 6 = -3$ 整除成功；第 5 组 $0 \div 9 = 0$ 整除成功。共有 $3$ 组有效整除，商总和为 $5 + (-3) + 0 = 2$。）*
* **输入样例 2**：
  ```text
  3
  10 3
  0 0
  100 -25
  ```
* **输出样例 2**：
  ```text
  ERR_REMAINDER
  ERR_DIV_ZERO
  OK -4
  1 -4
  ```
