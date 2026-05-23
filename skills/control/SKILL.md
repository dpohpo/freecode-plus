---
name: control
description: |
user-invocable: "true"
  Mac 电脑操控技能集 - 指哪儿打哪儿

  集成三神器：Hammerspoon + Karabiner-Elements + yabai
  实现完全键盘驱动的电脑操控

  使用场景：
  - 用户说 "/control" - 查看操控速查表
  - 用户说 "/control status" - 检查服务状态
  - 用户说 "/control restart" - 重启所有服务
  - 用户说 "/control edit" - 打开配置文件
---

# 🎮 Control — Mac 指哪儿打哪儿操控系统

> **版本**: v1.0 | **创建日期**: 2026-03-09

---

## 三神器架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL 系统架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Hammerspoon │  │  Karabiner  │  │    yabai    │         │
│  │   (自动化)   │  │ (键盘映射) │  │ (窗口管理) │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│                   ┌──────▼──────┐                           │
│                   │    skhd     │                           │
│                   │ (快捷键守护)│                            │
│                   └─────────────┘                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 组件职责

| 组件 | 职责 | 配置文件 |
|------|------|----------|
| **Hammerspoon** | 自动化引擎、鼠标控制、窗口管理、应用启动 | `~/.hammerspoon/init.lua` |
| **Karabiner-Elements** | 键盘重映射、Hyper键、Vim模式 | `~/.config/karabiner/karabiner.json` |
| **yabai** | 瓦片式窗口管理、空间管理 | `~/.yabairc` |
| **skhd** | 快捷键守护进程 | `~/.skhdrc` |

---

## 🔧 服务管理

```bash
# 检查服务状态
pgrep -fl "yabai|skhd|Hammerspoon|Karabiner"

# 启动服务
yabai --start-service
skhd --start-service
# Hammerspoon 通过应用启动

# 重启服务
yabai --restart-service
skhd --restart-service

# 停止服务
yabai --stop-service
skhd --stop-service
```

---

## ⌨️ 快捷键速查表

### 超键 (Hyper Key)
**Hyper = Cmd + Alt + Shift + Ctrl** (四键合一)

> 通过 Karabiner-Elements 实现：**Caps Lock 单按 = Escape，按住 = Hyper**

---

### 🖱️ 鼠标控制 (Hammerspoon)

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `Hyper + h` | 鼠标左移 | 20px/步，可按住连续移动 |
| `Hyper + j` | 鼠标下移 | 20px/步 |
| `Hyper + k` | 鼠标上移 | 20px/步 |
| `Hyper + l` | 鼠标右移 | 20px/步 |
| `Cmd+Alt+Ctrl + h/j/k/l` | 精细移动 | 5px/步，像素级控制 |
| `Hyper + f` | 左键点击 | 点击当前位置 |
| `Hyper + d` | 右键点击 | 右键菜单 |
| `Hyper + c` | 鼠标居中 | 移到屏幕中心 |
| `Hyper + 1` | 左上角 | 瞬移到左上 |
| `Hyper + 2` | 右上角 | 瞬移到右上 |
| `Hyper + 3` | 左下角 | 瞬移到左下 |
| `Hyper + 4` | 右下角 | 瞬移到右下 |

---

### 🪟 窗口管理 (yabai + skhd)

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| `⌃⌘ + h/j/k/l` | 切换焦点 | 在窗口间移动焦点 |
| `⇧⌃⌘ + h/j/k/l` | 交换窗口 | 交换当前窗口与目标窗口 |
| `⌥⌃⌘ + h/j/k/l` | 调整大小 | 调整窗口边界 |
| `⌃⌘ + f` | 全屏 | 窗口占满屏幕 |
| `⌃⌘ + space` | 浮动 | 切换浮动/平铺模式 |
| `⌃⌘ + r` | 旋转 | 顺时针旋转90° |
| `⌃⌘ + x` | X轴镜像 | 水平镜像 |
| `⌃⌘ + y` | Y轴镜像 | 垂直镜像 |
| `⌃⌘ + b` | 平衡 | 等分窗口空间 |
| `⌃⌘ + c` | 居中 | 窗口居中 |
| `⌃⌘ + 1~9` | 切换空间 | 跳转到指定桌面 |
| `⇧⌃⌘ + 1~5` | 发送窗口 | 把窗口移到指定桌面 |

---

### 🪟 窗口管理 (Hammerspoon 备用)

| 快捷键 | 功能 |
|--------|------|
| `⌃⌘ + ←` | 左半屏 |
| `⌃⌘ + →` | 右半屏 |
| `⌃⌘ + ↑` | 上半屏 |
| `⌃⌘ + ↓` | 下半屏 |
| `⌃⌘ + m` | 最大化 |

---

### ⌨️ 键盘增强 (Karabiner-Elements)

| 原键 | 映射 | 说明 |
|------|------|------|
| `Caps Lock` 单按 | `Escape` | Vim 风格 |
| `Caps Lock` 按住 | `Hyper` | 四修饰键合一 |
| `左 Control` 单按 | `Escape` | 双 Escape |
| `Fn + h/j/k/l` | `←/↓/↑/→` | Vim 方向键 |

---

### 🚀 应用启动 (skhd + Hammerspoon)

| 快捷键 | 应用 |
|--------|------|
| `Cmd + Alt + t` | Terminal |
| `Cmd + Alt + v` | VS Code |
| `Cmd + Alt + b` | Chrome |
| `Cmd + Alt + f` | Finder |
| `Hyper + Return` | Terminal |
| `Hyper + b` | Chrome |
| `Hyper + v` | VS Code |

---

## 📁 配置文件位置

```
~/.hammerspoon/init.lua      # Hammerspoon 配置
~/.config/karabiner/karabiner.json  # Karabiner-Elements 配置
~/.yabairc                   # yabai 配置
~/.skhdrc                    # skhd 配置
```

---

## 🔧 维护命令

```bash
# 编辑配置
open -e ~/.hammerspoon/init.lua
open -e ~/.yabairc
open -e ~/.skhdrc
open ~/.config/karabiner/karabiner.json

# 重新加载 Hammerspoon 配置
hs -c "hs.reload()"

# 查看 yabai 日志
tail -f /tmp/yabai_$(whoami).out.log
tail -f /tmp/yabai_$(whoami).err.log

# 查看 skhd 日志
tail -f /tmp/skhd_$(whoami).out.log
tail -f /tmp/skhd_$(whoami).err.log

# 检查 yabai 状态
yabai -m query --spaces
yabai -m query --windows
yabai -m query --displays
```

---

## ⚠️ 系统权限要求

以下应用需要 **辅助功能** 权限：
- 系统设置 → 隐私与安全性 → 辅助功能
- 添加：yabai, skhd, Hammerspoon, Karabiner-Elements

**yabai scripting addition** (可选，增强功能):
```bash
# 需要 SIP 部分禁用或签名
sudo visudo -f /private/etc/sudoers.d/yabai
# 添加:
# $(whoami) ALL=(root) NOPASSWD: sha256:$(shasum -a 256 $(which yabai) | cut -d " " -f 1) $(which yabai) --load-sa
```

---

## 🛠️ 安装命令

```bash
# 一键安装
brew install --cask hammerspoon karabiner-elements
brew install koekeishiya/formulae/yabai koekeishiya/formulae/skhd

# 启动服务
yabai --start-service
skhd --start-service
# Hammerspoon 从 Applications 启动
```

---

## 📚 进阶资源

| 资源 | 链接 |
|------|------|
| Hammerspoon 文档 | https://www.hammerspoon.org/ |
| Hammerspoon API | https://www.hammerspoon.org/docs/ |
| Karabiner-Elements | https://karabiner-elements.pqrs.org/ |
| yabai Wiki | https://github.com/koekeishiya/yabai/wiki |
| skhd | https://github.com/koekeishiya/skhd |

---

## 🔗 相关工具

| 工具 | 用途 | 安装 |
|------|------|------|
| **Rectangle** | 简单窗口管理 | `brew install --cask rectangle` |
| **LinearMouse** | 鼠标加速控制 | `brew install --cask linearmouse` |
| **Mac Mouse Fix** | 平滑滚动 | `brew install --cask mac-mouse-fix` |
| **Mos** | 平滑滚动 | `brew install --cask mos` |

---

## 🛡️ 冗余方案 (故障转移)

当硬核方案出现问题时，使用这套简单可靠的备用方案：

### 方案对比

| 方案 | 组件 | 复杂度 | 可靠性 | 适用场景 |
|------|------|:------:|:------:|----------|
| **硬核方案** | Hammerspoon + yabai + skhd + Karabiner | 高 | 中 | 极客、全键盘操作 |
| **冗余方案** | Rectangle + Karabiner + Mac Mouse Fix | 低 | 高 | 日常使用、故障转移 |

### Rectangle 快捷键 (⌃⌘ 组合)

| 快捷键 | 功能 |
|--------|------|
| `⌃⌘ ←` | 左半屏 |
| `⌃⌘ →` | 右半屏 |
| `⌃⌘ ↑` | 上半屏 |
| `⌃⌘ ↓` | 下半屏 |
| `⌃⌘ ↩` | 最大化 |
| `⌃⌘ C` | 居中 |
| `⌃⌘ U` | 左上 1/4 |
| `⌃⌘ I` | 右上 1/4 |
| `⌃⌘ J` | 左下 1/4 |
| `⌃⌘ K` | 右下 1/4 |
| `⌃⌘⇧ ←` | 左 1/3 |
| `⌃⌘⇧ →` | 右 2/3 |

> **注意**: 使用`⌃⌘` 避免和 macOS 空间切换 (`⌃←/→`) 冲突

### Mac Mouse Fix 功能

- **平滑滚动**: 原生触控板般的滚动体验
- **按钮自定义**: 鼠标按钮可映射任意功能
- **点击增强**: 轻点/长按/双击动作自定义

### 故障转移检查

```bash
# 检查冗余方案状态
pgrep -fl "Rectangle|Mac Mouse"

# 启动冗余方案
open -a Rectangle
open -a "Mac Mouse Fix"
```

---

## 💡 使用技巧

### 1. 鼠标 + 窗口组合技
```
1. Hyper + c (鼠标居中)
2. Alt + f (窗口全屏)
3. 完成：鼠标和窗口都在屏幕中心
```

### 2. 快速窗口归位
```
1. Alt + space (浮动模式)
2. 拖拽到目标位置
3. Alt + space (恢复平铺)
```

### 3. 跨桌面移动窗口
```
1. Shift + Alt + 2 (发送到桌面2)
2. Alt + 2 (跟随到桌面2)
```

### 4. 精确鼠标定位
```
1. Hyper + 1 (瞬移左上角)
2. Cmd+Alt+Ctrl + l (精细右移到目标)
3. Hyper + f (点击)
```

---

## ⚡ 性能优化

```lua
-- Hammerspoon 性能优化
hs.timer.delay = 0.001  -- 最小延迟
hs.hotkey.modalDelay = 0  -- 禁用模态延迟
```

```bash
# yabai 性能优化
yabai -m config window_shadow float  -- 禁用窗口阴影提升性能
```

---

*此技能由硬核玩家配置生成*
