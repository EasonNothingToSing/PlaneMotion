# PlaneMotion 快速入门

## 10分钟上手

### 1. 安装 (1分钟)

```bash
cd PlaneMotion
uv pip install -e .
```

### 2. 运行示例 (2分钟)

```bash
python examples/basic_usage.py
```

### 3. 基础操作 (3分钟)

**创建组件:**
- File → Insert → Circle/Rectangle/Trapezoid
- 或右键 → Insert Here

**移动组件:**
- 左键拖拽组件

**调整大小:**
- 鼠标悬停在组件边缘，光标变成调整大小图标
- 拖拽边缘

**连接组件:**
1. 点击 "Connect" 按钮进入连接模式
2. 左键点击第一个组件
3. 左键点击第二个组件
4. 点击 "Disconnect" 或 ESC 退出连接模式

**视口控制:**
- 中键拖拽：平移视口
- 滚轮：缩放视口
- Ctrl+0：重置视图

**保存/加载:**
- Ctrl+S：保存场景
- Ctrl+O：打开场景

### 4. 创建自己的应用 (4分钟)

创建 `my_app.py`:

```python
from planemotion import PlaneMotionEngine
from planemotion.components import Circle, Rectangle

# 创建引擎
engine = PlaneMotionEngine(
    width=1400,
    height=900,
    title="我的2D应用"
)

# 注册组件类型
engine.register_component_type('circle', Circle)
engine.register_component_type('rectangle', Rectangle)

# 运行
engine.run()
```

运行:
```bash
python my_app.py
```

### 5. 创建自定义组件 (可选)

```python
from planemotion import Component

class MyComponent(Component):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = (200, 100, 150)
    
    def contains_point(self, x, y):
        # 简单的矩形检测
        return (self.x - 25 < x < self.x + 25 and
                self.y - 25 < y < self.y + 25)
    
    def get_vertices(self):
        # 返回4个顶点
        return [
            (self.x - 25, self.y - 25),
            (self.x + 25, self.y - 25),
            (self.x + 25, self.y + 25),
            (self.x - 25, self.y + 25)
        ]

# 注册
engine.register_component_type('mycomponent', MyComponent)
```

## 完整示例

查看 `examples/` 目录:
- `basic_usage.py` - 基础功能
- `custom_component.py` - 自定义组件和菜单

## 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+O | 打开文件 |
| Ctrl+S | 保存文件 |
| Ctrl+0 | 重置视图 |
| Delete | 删除选中组件 |
| ESC | 取消连接 |

## 鼠标操作

| 操作 | 功能 |
|------|------|
| 左键拖拽 | 移动组件 |
| 左键边缘 | 调整大小 |
| 中键拖拽 | 平移视口 |
| 滚轮 | 缩放视口 |
| 右键 | 上下文菜单 |

## 下一步

- 阅读 [README_ENGINE.md](README_ENGINE.md) 了解详细文档
- 查看 [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) 了解架构
- 运行 `examples/custom_component.py` 学习自定义

## 遇到问题？

1. 确保 pygame-gui 正确安装: `uv pip install pygame-gui`
2. 检查 Python 版本 >= 3.8
3. 查看完整文档或提交 Issue

Happy coding! 🚀
