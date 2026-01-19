# PlaneMotion Engine

一个灵活的2D组件引擎，用于可视化编程和图形交互。

## 特性

- 🎨 **可视化组件系统**: 创建、拖动、缩放、旋转组件
- 🔗 **组件连接**: 通过可视化线条连接组件，建立关系
- 🎯 **自定义组件**: 继承基类创建自己的组件类型
- 🎛️ **可定制UI**: 自定义菜单、按钮和界面布局
- 💾 **场景保存/加载**: JSON格式保存场景状态
- 🖱️ **丰富交互**: 拖拽、缩放、平移视口、边缘调整大小
- ⌨️ **快捷键支持**: 键盘快捷键加速操作

## 安装

```bash
# 使用 pip 安装
pip install -e .

# 或使用 uv
uv pip install -e .
```

## 快速开始

### 基础使用

```python
from planemotion import PlaneMotionEngine
from planemotion.components import Circle, Rectangle

# 创建引擎实例
engine = PlaneMotionEngine(
    width=1400,
    height=900,
    title="My Application"
)

# 注册组件类型
engine.register_component_type('circle', Circle)
engine.register_component_type('rectangle', Rectangle)

# 启动引擎
engine.run()
```

### 创建自定义组件

```python
from planemotion import Component
import math

class Triangle(Component):
    """自定义三角形组件"""
    
    def __init__(self, x: float, y: float, size: float = 50.0):
        super().__init__(x, y)
        self.size = size
        self.color = (255, 100, 50)
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在三角形内"""
        vertices = self.get_vertices()
        # 实现点在多边形内的检测逻辑
        # ...
        return False
    
    def get_vertices(self):
        """返回三角形顶点"""
        half_base = self.size * 0.5
        height = self.size * (math.sqrt(3) / 2)
        
        local_vertices = [
            (0, -height / 2),
            (-half_base, height / 2),
            (half_base, height / 2)
        ]
        
        # 应用旋转和缩放
        rotated = []
        for lx, ly in local_vertices:
            rx, ry = self._rotate_point(lx, ly, self.rotation_deg)
            rotated.append((
                self.x + rx * self.scale,
                self.y + ry * self.scale
            ))
        return rotated

# 注册自定义组件
engine.register_component_type('triangle', Triangle)
```

### 自定义菜单

```python
def custom_menu_provider(engine):
    """提供自定义菜单结构"""
    return {
        'file': [
            {"type": "item", "label": "New", "action": lambda: print("New")},
            {"type": "separator"},
            {"type": "item", "label": "Exit", "action": lambda: setattr(engine, 'running', False)},
        ],
        'edit': [
            {
                "type": "item",
                "label": "Insert",
                "submenu": [
                    {"type": "item", "label": "Triangle", "action": lambda: engine.insert_component_at_click('triangle')},
                ]
            },
        ]
    }

engine.set_menu_provider(custom_menu_provider)
```

### UI定制

```python
def ui_customizer(view):
    """自定义UI外观"""
    view.background_color = (240, 248, 255)  # 设置背景色

engine.set_ui_customizer(ui_customizer)
```

## 核心概念

### Component（组件）

所有可视化元素的基类。自定义组件需要实现：

- `contains_point(x, y)`: 点击检测
- `get_vertices()`: 返回组件顶点用于渲染

基类提供：
- 位置 (`x`, `y`)
- 旋转 (`rotation_deg`)
- 缩放 (`scale`)
- 选中状态 (`selected`)
- 序列化方法 (`to_dict()`, `from_dict()`)

### Connection（连接）

组件之间的连接关系，用线条可视化。

### Engine（引擎）

主控制器，协调所有功能：
- 事件处理
- 渲染循环
- 组件管理
- 场景保存/加载

## 交互操作

### 鼠标操作

- **左键拖拽**: 移动组件
- **左键点击边缘**: 调整组件大小
- **中键拖拽**: 平移视口
- **右键**: 打开上下文菜单
- **滚轮**: 缩放视口

### 连接模式

1. 点击 "Connect" 按钮进入连接模式
2. 左键点击第一个组件
3. 左键点击第二个组件完成连接
4. ESC 取消连接
5. 再次点击 "Connect" 退出连接模式

### 键盘快捷键

- `Ctrl+O`: 打开文件
- `Ctrl+S`: 保存文件
- `Ctrl+0`: 重置视口
- `Delete`: 删除选中组件
- `ESC`: 取消连接

## 示例

查看 `examples/` 目录获取完整示例：

- `basic_usage.py`: 基础使用示例
- `custom_component.py`: 自定义组件示例

运行示例：

```bash
python examples/basic_usage.py
python examples/custom_component.py
```

## 架构

PlaneMotion 采用 MVVM 架构：

- **Model**: 数据层 (Component, Connection)
- **ViewModel**: 业务逻辑层 (PlaneMotionViewModel)
- **View**: 视图层 (PlaneMotionView, MenuManager)
- **Engine**: 控制器 (PlaneMotionEngine)

## 依赖

- pygame-ce >= 2.5.0
- pygame-gui >= 0.6.0
- Python >= 3.8

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 开发

```bash
# 克隆仓库
git clone <repository-url>
cd PlaneMotion

# 安装开发依赖
uv pip install -e ".[dev]"

# 运行测试
pytest

# 运行示例
python examples/basic_usage.py
```
