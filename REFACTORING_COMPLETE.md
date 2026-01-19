# PlaneMotion 引擎重构完成

## 概述

PlaneMotion 已成功重构为一个可复用的2D组件引擎库，可被其他Python项目作为依赖使用。

## 新架构

### 目录结构

```
planemotion/                    # 核心引擎包
├── __init__.py                # 公共API (PlaneMotionEngine)
├── theme.json                 # UI主题
├── core/                      # 核心功能
│   ├── base_component.py      # Component抽象基类
│   ├── connection.py          # Connection连接类
│   ├── viewmodel.py           # 业务逻辑层
│   ├── view.py                # 视图渲染层
│   └── menu_system.py         # 菜单系统
├── components/                # 内置组件
│   ├── circle.py              # 圆形组件
│   ├── rectangle.py           # 矩形组件
│   └── trapezoid.py           # 梯形组件
└── impl/                      # 实现细节
    ├── default_engine.py      # 默认引擎实现
    └── save_load.py           # 保存/加载功能

examples/                      # 使用示例
├── basic_usage.py            # 基础使用
└── custom_component.py       # 自定义组件

lib/                          # 旧代码（保留）
```

### 核心类

#### PlaneMotionEngine（主API）

```python
from planemotion import PlaneMotionEngine

engine = PlaneMotionEngine(width=1400, height=900, title="My App")
engine.register_component_type('circle', Circle)
engine.run()
```

**方法:**
- `register_component_type(name, class)` - 注册组件类型
- `set_menu_provider(func)` - 自定义菜单
- `set_ui_customizer(func)` - 自定义UI
- `run()` - 启动引擎

#### Component（抽象基类）

所有组件必须继承此类并实现：
- `contains_point(x, y)` - 点击检测
- `get_vertices()` - 返回顶点

基类提供：
- 位置、旋转、缩放
- 序列化/反序列化
- 旋转计算辅助

## 使用方法

### 1. 基础使用

```python
from planemotion import PlaneMotionEngine
from planemotion.components import Circle, Rectangle, Trapezoid

engine = PlaneMotionEngine(1400, 900, "My Application")
engine.register_component_type('circle', Circle)
engine.register_component_type('rectangle', Rectangle)
engine.register_component_type('trapezoid', Trapezoid)
engine.run()
```

### 2. 创建自定义组件

```python
from planemotion import Component
import math

class Triangle(Component):
    def __init__(self, x, y, size=50):
        super().__init__(x, y)
        self.size = size
        self.color = (255, 100, 50)
    
    def contains_point(self, x, y):
        # 实现点在三角形内的检测
        ...
        return False
    
    def get_vertices(self):
        # 返回三角形顶点
        local_vertices = [
            (0, -self.size/2),
            (-self.size/2, self.size/2),
            (self.size/2, self.size/2)
        ]
        # 应用旋转和缩放
        vertices = []
        for lx, ly in local_vertices:
            rx, ry = self._rotate_point(lx, ly, self.rotation_deg)
            vertices.append((self.x + rx * self.scale, 
                           self.y + ry * self.scale))
        return vertices

# 注册使用
engine.register_component_type('triangle', Triangle)
```

### 3. 自定义菜单

```python
def custom_menu_provider(engine):
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
                    {"type": "item", "label": "Triangle", 
                     "action": lambda: engine.insert_component_at_click('triangle')},
                ]
            },
        ]
    }

engine.set_menu_provider(custom_menu_provider)
```

### 4. 自定义UI

```python
def ui_customizer(view):
    view.background_color = (240, 248, 255)  # Alice blue

engine.set_ui_customizer(ui_customizer)
```

## 功能特性

### 组件操作
- ✅ 拖拽移动
- ✅ 边缘调整大小
- ✅ 旋转
- ✅ 缩放
- ✅ 选中/取消选中

### 连接功能
- ✅ 连接模式切换（Connect按钮）
- ✅ 左键点击连接组件
- ✅ 可视化连接线
- ✅ 删除连接

### 视口控制
- ✅ 中键拖拽平移
- ✅ 滚轮缩放
- ✅ Ctrl+0 重置视图

### 场景管理
- ✅ Ctrl+O 打开文件
- ✅ Ctrl+S 保存文件
- ✅ JSON格式序列化

### 菜单系统
- ✅ File菜单 (Open/Save/Exit)
- ✅ Edit菜单 (Insert/Delete/Rotate)
- ✅ 右键上下文菜单
- ✅ 子菜单支持
- ✅ 自定义菜单提供者

## 安装

### 开发模式

```bash
cd PlaneMotion
uv pip install -e .
```

### 作为依赖

```bash
# 使用 pip
pip install git+https://github.com/your-repo/PlaneMotion.git

# 或在 pyproject.toml 中
dependencies = [
    "planemotion @ git+https://github.com/your-repo/PlaneMotion.git"
]
```

## 依赖项

- pygame-ce >= 2.5.0
- pygame-gui >= 0.6.0
- Python >= 3.8

## 示例程序

### basic_usage.py
演示基础功能和内置组件的使用。

```bash
python examples/basic_usage.py
```

### custom_component.py
演示如何创建自定义组件（Triangle, Star）和自定义菜单。

```bash
python examples/custom_component.py
```

## 技术细节

### MVVM架构
- **Model**: Component, Connection (数据模型)
- **ViewModel**: PlaneMotionViewModel (业务逻辑)
- **View**: PlaneMotionView (渲染)
- **Engine**: DefaultPlaneMotionEngine (控制器)

### 插件系统
- 组件注册表：支持动态注册新组件类型
- 菜单提供者回调：自定义菜单结构
- UI定制器回调：自定义视图属性

### 序列化
- 组件实现 `to_dict()` 和 `from_dict()`
- 支持保存/加载完整场景（组件+连接）
- JSON格式，人类可读

## 迁移指南

### 从旧main.py迁移

**旧代码:**
```python
from engine import PlaneMotionEngine

engine = PlaneMotionEngine()
engine.run()
```

**新代码:**
```python
from planemotion import PlaneMotionEngine
from planemotion.components import Circle, Rectangle, Trapezoid

engine = PlaneMotionEngine()
engine.register_component_type('circle', Circle)
engine.register_component_type('rectangle', Rectangle)
engine.register_component_type('trapezoid', Trapezoid)
engine.run()
```

### 从lib.model.component导入

**旧代码:**
```python
from lib.model import Component, Circle
```

**新代码:**
```python
from planemotion import Component
from planemotion.components import Circle
```

## 测试状态

✅ 基础示例运行成功
✅ 组件创建/移动/选中工作正常
✅ 菜单系统功能正常
✅ 包安装成功 (pip install -e .)

## 下一步

### 可选增强
1. 添加单元测试
2. CI/CD 配置
3. 发布到 PyPI
4. 添加更多内置组件
5. 性能优化（大量组件时）
6. 导出/导入其他格式（PNG, SVG）
7. 撤销/重做功能
8. 组件分组
9. 图层系统

## 文档

- `README_ENGINE.md` - 完整使用文档
- `examples/` - 可运行示例
- 代码内 docstrings - API文档

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
