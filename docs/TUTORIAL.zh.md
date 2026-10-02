# 📘 教程（中文）— Auto Mouse & Keyboard Macro

> 中文完整教程：从安装到复杂脚本，附动手练习。
> （泰语完整版：[TUTORIAL.md](TUTORIAL.md) · 英语版：[TUTORIAL.en.md](TUTORIAL.en.md) — 各章节一一对应）

---

## 第 1 章 — 安装与首次运行

**现成 .exe（推荐）：** 从 [Releases](https://github.com/NarDecH/Python_Mouse_Keyboard_Macro/releases/latest)
页面下载 `AutoMouseMacro.exe`，双击即可运行 — 无需安装 Python。

**从源码运行：**

```bash
py -m pip install -r requirements.txt   # pynput（图像点击需另装 opencv-python 与 Pillow）
py auto_macro.py                        # 或 run.bat
```

主窗口是一张表格 — 一行 = 一个事件：
`启用(☑) / # / X / Y / 动作 / 附加参数 / 分 / 秒 / 重复`

安全起步：加载 `examples/01_auto_typer.json`（只打字、不点击），然后按 ▶ START。

---

## 第 2 章 — 录制第一个脚本

1. 按 **RECORD**（F9）— 监听器捕获每一次鼠标点击、按键和滚轮。
2. 做一遍你的操作，再按一次 F9（或 STOP）。
3. 检查各行：空闲间隔变成延时（秒），滚轮变成 Scroll Up/Down 行。
4. 双击任意单元格微调坐标/延时，然后按 **START**（F6）。

---

## 第 3 章 — 播放选项

| 控件 | 含义 |
|---|---|
| START / F6 | 播放已勾选（☑）的行一次 |
| REPEAT | 一直重复直到 STOP |
| "Loop forever" / F10 | 无限循环 |
| Loops 框（0 = 不限） | 整个脚本播放 N 遍 |
| 速度 0.25×–4× | 延时除以该倍数 |
| Shuffle / 行百分比 (v1.10) | 每轮随机顺序 / 随机子集 |
| 恢复鼠标位置 | 结束后光标回到按 START 时的位置 |

停止通道 — 全部约 50 ms 内响应：**STOP 按钮 / 任意位置 F8 / Esc / Ctrl+C**，
卡住的按键或鼠标按钮会自动释放。

---

## 第 4 章 — 动作参考

**鼠标：** 左/右/中键 + 按下/抬起、双击、Ctrl/Shift/Alt+点击、
Scroll Up/Down（格数写在附加参数）、移动鼠标、按偏移移动、
保存/恢复光标。

**键盘：** 敲击/按下/松开按键 — 附加参数接受 `a`、`5`、`space`、`enter`、`esc`、
`ctrl`、`shift`、`alt`、`win`、`f1`–`f12`、方向键、`pgup`、`prtsc`、VK 码如 `27`，
以及组合键 `Ctrl+W`、`Ctrl+Shift+T`、`Win+D`（v1.20.4）。物理按键与键盘布局无关。

**扩展 (v1.5+)：** 输入文字（泰语+emoji，Unicode 输入 — 任何键盘布局都正确）、
启动程序（`notepad.exe` 或 `https://...`）、Beep、设置/读取剪贴板 (v1.20)、
设置变量 (v1.19)、图像点击 / 等待图像（需 `opencv-python Pillow`）、
等待像素颜色 (v1.18)、If Pixel Color / Read Pixel Color / If Variable (v2.5)、
自定义插件 (v1.16)。

图像动作的搜索区域语法：`button.png@100,200,300,400` = 只在这个框内搜索，
`#90` = 阈值 90%。

---

## 第 5 章 — 条件：If Image / Else If Image (v1.17–1.18)

让脚本**自己做决定**：

```text
行 1   If Image (btn.png)       ← 判断
行 2-3 ...A 组（找到时播放）
行 4   Else If Image (btn.png) 重复 = 2
行 5-6 ...B 组（没找到时播放）
```

- 找到 → 播放 A 组，Else 行随后跳过 B 组。
- 没找到 → 跳过 A 组（按 If 行的重复数），播放 B 组。
- 全局唯一规则：**条件行的"重复"列 = 要跳过的行数。**

等待像素颜色：附加参数 `x,y #RRGGBB`，如 `300,300 #ffffff` — 等待（最长 30 秒，
`60s` 可覆盖）直到像素匹配再继续。

**If Image 重试窗口 (v2.4)：** 在附加参数末尾加 `Ns`，如 `img.png 5s` =
决定前最多重查 5 秒 — 解决页面还在加载的问题。

---

## 第 5B 章 — 轮次/时间条件 + 分节标题 (v1.21–1.22)

**If Loop** — 附加参数 = 轮次 `3`：第 3 轮起跳过后面 N 行（重复数）。
适合"第一轮做设置，之后跳过"。

**If Time** — 附加参数 = `HH:MM` 如 `22:30`：今天过了这个时间就跳过 N 行。
用工具栏的 **🕐 当前时间 (+15 分)** 按钮 (v1.22) 一键填入。

**分节标题** — 右键 → "转换为 Section header"：一个永不播放、不计数、不延时的分组标题行。
**折叠/展开分组** (v1.22)：右键标题 → 折叠 — 成员从表格里消失（标题显示 `(ย่อ N แถว)`）
但**播放完全不受影响**；再展开时保持原顺序。删除折叠的标题会先自动展开 — 行绝不丢失。

**行颜色 (v1.22)：** 条件 = 浅黄 · 键盘 = 浅紫 · 特殊动作 = 浅蓝 · 鼠标行保持斑马纹 — 纯视觉。

**练习：** 运行 `py auto_macro.py examples/10_conditions_v21.json --loops 3` —
第 3 轮时"round 3+"那行消失了：这就是 If Loop。

---

## 第 6 章 — 变量与剪贴板 (v1.19–1.20)

- **设置变量** — 附加参数 `名字 = 值`、`名字 += 5`、`名字 -= 5`。
- 在任意 X / Y / 附加参数 / 分 / 秒 / 重复单元格里用 `{名字}`。
- **设置/读取剪贴板** — 把文本放到剪贴板，或读进变量。
- 每次按播放时变量重置。

演示：`examples/08_variables.json`、`examples/09_clipboard.json`。

---

## 第 7 章 — 配置文件与定时

- **配置文件栏** — 保存多套脚本随时切换；自动保存在 `macro_profiles.json`。
- **热键配置 (v1.9)** — 选一个文件夹，F1–F4 按文件名顺序加载第 1–4 个 .json 并立即播放。
- **定时** — "每 N 分钟"或"每天 HH:MM"，多个时刻用逗号分隔如 `08:00,12:30,22:00` (v2.7)；
  后台线程通过队列把命令推给 UI（线程安全）。

---

## 第 8 章 — 命令行 (CLI)

```bash
py auto_macro.py script.json                 # 不开 GUI 直接播放
py auto_macro.py script.json --loops 5 --speed 2
py auto_macro.py script.json --loop          # 无限循环
py auto_macro.py script.json --watchdog 3    # 播完自动重启 (v1.10)
py auto_macro.py script.json --max-minutes 60  # v2.4: 安全超时 — 60 分钟后自动停
py auto_macro.py script.json --validate      # v2.4: 逐行校验，不播放（有问题退出码 1）
py auto_macro.py --version                   # 打印版本号
py engine_cli.py script.json                 # v2.1: 纯引擎 CLI（完全不碰 GUI 代码）
py engine_cli.py script.jsonl --json-lines   # v2.2: 每行一条 JSON（跳过 #注释）
```

停止方式：任意位置 F8/Esc、控制台 Esc/q、Ctrl+C，或 `--stop-file 路径`
（创建该文件即停止）。
**图像动作自 v2.2 起在 CLI 可用** — Image Click、If Image、Else If Image、Wait for Image
与 GUI 用同一套 OpenCV 搜索（缺图会报告并继续运行）。

---

## 第 9 章 — 统计、日志与备份

- 每次播放追加到 `macro_log_YYYY-MM-DD.txt`（在设置里开关，CLI 用 `--no-log`）。
- **📊 统计** — 总计、每日柱状图（14 天）、每月总计，以及 **总耗时前 5 的动作** (v1.18)
  用于找瓶颈。
- **📝 日志查看器** — 在程序内阅读日志。
- **自动备份 (v1.13)** — 每次关闭把整个工作区+配置+设置存进 `backups/`
  （默认 7 天，设置里可调 1–90 天）。
- **导出/导入设置** — 一个文件搬家。

---

## 第 10 章 — 插件 (v1.16+)

项目内置 10 个插件：Sleep、Message Box、Play Sound、Webhook、Multi Image Click、
**Screenshot**、**Toast**（Windows 10/11 通知）、**Write Log** 与
**Ask Input**（询问用户并把值存进变量）。

把一个简短的 Python 文件放进 `plugins/` — 它就会出现在动作下拉框里：

```python
ACTION_NAME = "打开记事本并等待"

def run(ctx, row):
    import os, time
    os.startfile("notepad.exe")
    time.sleep(1.5)
```

`ctx` 提供 `mouse`、`kb`、`log()`、`cfg`、`stop_check()`（STOP 时提前返回）与
`ui`（msg/beep）。坏文件会被跳过 — 插件永远不会让程序崩溃。
完整 API 与创意：[PLUGINS.md](PLUGINS.md)。工具栏的 **🔌 plugins** 按钮直接打开文件夹。

---

## 第 11 章 — 疑难排查

| 症状 | 解决 |
|---|---|
| 鼠标不动 | 以管理员运行（游戏/管理员窗口拦截输入）；在设置里跑 🧪 自检 |
| F6/F8 没反应 | 设置里的全局热键状态；日志会说明 — 程序特意用 `keyboard.Listener` 而非 `GlobalHotKeys` |
| 打出的字不对 | v1.20.2 直接发送 Unicode；确认目标窗口有焦点且加载完成 |
| 找不到图像 | 检查搜索区域、明暗/阈值；模板 .png 要和屏幕上完全一致 |
| 延时中途 STOP "卡住" | 不该发生 — 所有延时按 50 ms 分片睡眠；带日志文件来报告 |
| Ctrl / 鼠标键卡住 | STOP 自动释放 Press Key / Down 跟踪的一切 |

---

## 第 12 章 — 快捷键

| 按键 | 作用 |
|---|---|
| F6 / F8 | 播放 / 停止（全局 — 无需焦点） |
| F9 / F10 | 录制 / 切换无限循环 |
| F1–F4 | 热键配置 1–4 立即播放 |
| Delete | 删除选中行（Ctrl/Shift+点击多选，v2.4） |
| Ctrl+F / Ctrl+Z | 查找并全部替换 / 撤销（50 层） |
| Ctrl+Y | 重做 — 单元格编辑也可撤销 (v2.5) |
| Alt+↑/↓ | 上下移动选中行 (v2.5) |

### AND 条件 (v2.6.0)

在任意主条件的附加参数里用 `&&` 连接 — **每一部分都必须为真**才继续，
否则跳过后面 N 行（重复数），与之前的唯一规则一致：

```text
If Image        img.png && 300,300 #ffffff && n > 5
                ← 图像找到 且 像素颜色匹配 且 变量 n > 5
If Pixel Color  300,300 #ffffff && 400,400 #000000   ← 两点都必须匹配
If Variable     n > 5 && code = A-1                  ← 同时比较多个变量
```

超时 token 与 `&&` 兼容（`img.png 5s && ...` 决定前重查 5 秒），
`--validate` 理解 `&&` 并逐行报告每个坏掉的部件。

### Block Start / Block End — 条件块与子循环 (v2.6.0)

`🔷 Block Start` → `🔷 Block End` 动作对把一组行包起来（最多嵌套 8 层）—
命令写在 Block Start 的附加参数里：

```text
(留空)              总是打开 — 只为结构
if img.png          条件为假 → 跳过整个块（用括号计数找到配对的 End）
if n > 5            变量 / 像素 / 图像条件，可混用 &&
until img.png       子循环：到 End 后跳回去重复，直到找到图像（最多 1000）
until n >= 5 max 20  循环直到 n >= 5，最多 20 轮 — 然后离开
max 10              无条件 — 把块体重复 10 次
```

与 If Image 不同，你**永远不用数行数** — 跳过/回跳跟随 Start/End 配对，
在块内增删行都安全。`--validate` 会在播放前检查配对、嵌套深度与附加参数格式。
试试演示：`py auto_macro.py examples/12_blocks.json`
（跳过块 / 数到 5 的子循环 / 2 层嵌套 — 只有 Beep，安全）。

---

## 第 13 章 — v2.x 新功能速览

### 13.1 扩展 (v2.0–2.3)
- **引擎与 GUI 分离** — `macro_engine.py` 是纯 Python（无 Tk）；精简的
  `engine_cli.py` 直接运行它 · 🔌 工具栏按钮打开插件文件夹 ·
  插件市场：[PLUGINS.md](PLUGINS.md)。
- **📤 Export Bat 菜单** — 在已保存的脚本旁边生成 `.bat`（Windows）+ `.sh`（Linux/macOS）
  启动器；双击运行（`--loop` 等参数原样转发）。

### 13.2 稳健性 (v2.4)
- **自愈全局热键** — 失效的监听器会被检测到并自动重启（限每 10 秒一次），
  在状态栏/日志里公告。原则：STOP 必须永远可用。
- **安全超时** — 设置"播放 N 分钟后自动停止"（1–720）· CLI：`--max-minutes N`。
- **If Image 重试窗口** — 追加 `Ns`（如 `img.png 5s`）决定前重查。
- **多选行** — Ctrl/Shift+点击后 Delete 整组删除（可撤销）。
- **定时选择配置文件** — 播放时加载哪个配置；设置里显示当前预约。
- **`--validate`** — 不播放、只报告每个有问题的行（发现时退出码 1）。
- 图像搜索的模板缓存 — 1000 轮不再读 .png 1000 次。

### 13.3 完整条件 + 更好用的表格 (v2.5)
- **If Pixel Color** — 点颜色条件：匹配 → 继续，不匹配 → 跳过 N 行（`Ns` 先重查）。
- **Read Pixel Color** — 把点的颜色存进 `{名字}`（附加参数：`名字 x,y`）。
- **If Variable** — 比较变量：数字（`round > 5`）或文本（`code = A-1`、`msg ~ failed`）。
- **Image Click 设置 `{img_x}/{img_y}`** — 相对找到的图像点击。
- **Set Variable 支持 `rand a-b`** — `luck = rand 1-100` 存一个随机数。
- **拖拽排序** — 按住拖动；按光标在上/下半行决定放在前面/后面；自动滚动；
  整个选区一起拖；不允许放到折叠的分组上。
- **重做 (Ctrl+Y) + 完整撤销** — 单元格编辑可撤销 · 每行有 **Note 列** ·
  Ctrl+F 里 **查找并全部替换**。
- **4 个新插件** — Screenshot · Toast · Write Log · Ask Input
  （`ctx["vars"]` 与脚本共享变量）。

### v2.7–v2.8 新增
- **四种语言文档** — 泰语/英语/中文/日语。
- **.ahk 互通** — 菜单 🔀 导出/导入（Send/Click/MouseMove/Sleep/Run）·
  v2.8 变量双向：`Set Variable` → `n := 5`，`If Variable` → `if (n > 5)`；
  导入 `n := 0` / `n += 2` / `if (n > 5)` 可还原为行（`x := y` → `x = {y}`）。
- **每个时间可选配置文件** — `08:00, 12:30=早班, 22:00`（到点自动加载该配置文件）。
- **社区插件 3 个** — Random Pause（随机暂停）· Counter（计数变量）· Open URL（打开网页）
  + 用于提交插件的 issue 模板（标准见 docs/PLUGINS.md）。

---

- **折叠代码块 (v2.8.1)** — 右键 Block Start 行可折叠到配对 Block End 之间的行
  （与分区相同的机制）— 隐藏的行仍会正常播放和保存；拒绝嵌套折叠。
- **校验按钮 (v2.8.1)** — 菜单 🔍 Validate 用与 `--validate` 相同的引擎检查整个脚本，
  并在窗口中报告 "第 N 行：原因"，无需命令行。

---

- **START 播放前校验 (v2.9.0)** — 按 START 时自动运行 `validate_rows`：发现问题时询问
  "跳过有问题的行继续播放？"— 确认 = 只播放正常的行，拒绝 = 回去修改；全部行都有问题时
  什么都不播放（不再静默失败）。
- **全部折叠 / 全部展开 (v2.9.0)** — 右键菜单："全部折叠" 一次折叠所有分区 + 代码块
  （外层组按顺序包含内层组）；"全部展开" 逐个展开直到表格完全恢复原始顺序。
- **.ahk 双向支持代码块 (v2.9.0)** — 导出：`if n > 5` → `if (n > 5) { … }`、`max 3` →
  `Loop, 3 {`、`until n >= 5` → `Loop { … } Until, n >= 5`（条件用 `&&` 连接，文本搜索
  `~` → `InStr()`）；无法翻译的图像/颜色条件整块变成注释，不会留下孤立大括号 ·
  导入时三种形式都会转换回 Block Start/End 行。

*对应代码 v2.10.0 · 泰语完整教程（更多练习）：[TUTORIAL.md](TUTORIAL.md) ·
项目文档：[README.md](README.md) · 插件市场：[PLUGINS.md](PLUGINS.md)*
