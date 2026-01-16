# PlaneMotion - MVVM Architecture Documentation

## Architecture Overview

PlaneMotion采用了MVVM (Model-View-ViewModel) 设计模式，实现了关注点分离和代码的高内聚低耦合。

PlaneMotion uses the MVVM (Model-View-ViewModel) design pattern to achieve separation of concerns and high cohesion with low coupling.

## Layer Structure | 层次结构

```
┌─────────────────────────────────────────────┐
│           Engine (Controller)               │
│  - Game loop coordination                   │
│  - Event handling and delegation            │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌─────▼──────┐
│  ViewModel  │  │    View    │
│  (Business  │◄─┤ (Rendering)│
│   Logic)    │  │            │
└──────┬──────┘  └────────────┘
       │
┌──────▼──────┐
│    Model    │
│   (Data)    │
└─────────────┘
```

## Components | 组件说明

### 1. Model Layer (数据层)

**Files:** `component.py`, `connection.py`

**Responsibilities:**
- Pure data structures | 纯数据结构
- Basic geometric calculations | 基础几何计算
- Serialization/deserialization | 序列化/反序列化
- No UI or business logic | 不包含UI或业务逻辑

**Classes:**
- `Component`: Abstract base class for all components
- `Circle`: Circle component data model
- `Rectangle`: Rectangle component data model
- `Connection`: Connection data model between components

**Key Features:**
- Immutable behavior: Components only store data
- Geometric operations: Contains point checking
- Connection points calculation

### 2. ViewModel Layer (视图模型层)

**File:** `viewmodel.py`

**Responsibilities:**
- Business logic | 业务逻辑
- State management | 状态管理
- User interaction handling | 用户交互处理
- Coordinates between Model and View | 协调Model和View

**Class:** `PlaneMotionViewModel`

**Key Features:**
- **Component Management**: Create, delete, query components
- **Selection System**: Track selected components
- **Dragging System**: Handle drag operations with offset calculation
- **Connection Creation**: Manage two-step connection creation
- **Scaling**: Scale selected components
- **Status Messages**: Provide feedback to users

**Main Methods:**
```python
# Component creation
create_circle(x, y, radius, color)
create_rectangle(x, y, width, height, color)
create_connection(source, target)

# Selection management
select_component_at_point(x, y)
deselect_all()

# Dragging operations
start_drag(x, y)
update_drag(x, y)
stop_drag()

# Scaling
scale_selected(delta)

# Connection creation
start_connection_at_point(x, y)
cancel_connection()

# Deletion
delete_selected()
delete_component(component)
```

### 3. View Layer (视图层)

**File:** `view.py`

**Responsibilities:**
- Pygame rendering | Pygame渲染
- Visual representation | 视觉呈现
- No business logic | 不包含业务逻辑
- Observes ViewModel state | 观察ViewModel状态

**Class:** `PlaneMotionView`

**Key Features:**
- **Component Rendering**: Draw circles and rectangles
- **Connection Rendering**: Draw connection lines
- **Selection Visualization**: Highlight selected components
- **Preview Rendering**: Show connection preview during creation
- **UI Overlays**: Help text and status messages

**Main Methods:**
```python
render(mouse_pos)              # Main render method
_render_components()           # Render all components
_render_connections()          # Render all connections
_render_connection_preview()   # Render connection preview
_render_help_text()           # Render help information
_render_status_message()      # Render status at bottom
```

### 4. Engine (Controller/Coordinator)

**File:** `engine.py`

**Responsibilities:**
- Game loop management | 游戏循环管理
- Event handling | 事件处理
- Coordinate MVVM components | 协调MVVM组件
- Delegate user input to ViewModel | 将用户输入委托给ViewModel

**Class:** `PlaneMotionEngine`

**Key Features:**
- Pygame event loop
- Input delegation to ViewModel
- View rendering coordination
- Save/Load coordination

### 5. SaveLoad (Utility)

**File:** `save_load.py`

**Responsibilities:**
- Scene serialization | 场景序列化
- Scene deserialization | 场景反序列化
- JSON file I/O | JSON文件输入输出

**Class:** `SaveLoadManager`

## Data Flow | 数据流

### User Input Flow (用户输入流程)
```
User Input → Engine → ViewModel → Model
                  ↓
              View observes ViewModel
                  ↓
              Render updated state
```

### Example: Creating a Circle (创建圆形示例)

1. **User** presses 'C' key
2. **Engine** receives keyboard event
3. **Engine** calls `viewmodel.create_circle(x, y)`
4. **ViewModel** creates new `Circle` model
5. **ViewModel** adds to components list
6. **View** queries `viewmodel.get_all_components()`
7. **View** renders the new circle

### Example: Dragging a Component (拖拽组件示例)

1. **User** clicks on component
2. **Engine** receives mouse down event
3. **Engine** calls `viewmodel.start_drag(x, y)`
4. **ViewModel** selects component and stores drag offset
5. **User** moves mouse
6. **Engine** calls `viewmodel.update_drag(x, y)`
7. **ViewModel** updates component position
8. **View** renders component at new position

## Benefits of MVVM | MVVM的优势

### 1. Separation of Concerns (关注点分离)
- Model: Pure data, no rendering code
- ViewModel: Business logic, no rendering code
- View: Pure rendering, no business logic

### 2. Testability (可测试性)
- ViewModel can be unit tested without pygame
- Model operations can be tested independently
- View rendering can be tested separately

### 3. Maintainability (可维护性)
- Changes to rendering don't affect business logic
- Business logic changes don't require View changes
- Model changes are isolated

### 4. Reusability (可重用性)
- Model classes can be used in different contexts
- ViewModel can work with different View implementations
- Components are framework-agnostic

### 5. Scalability (可扩展性)
- Easy to add new component types
- Easy to add new interactions
- Easy to add new rendering styles

## Adding New Features | 添加新功能

### Adding a New Component Type (添加新组件类型)

1. **Model**: Create new class in `component.py`
   ```python
   class Triangle(Component):
       # Implement abstract methods
   ```

2. **ViewModel**: No changes needed (uses generic Component interface)

3. **View**: Add rendering logic in `view.py`
   ```python
   def _render_triangle(self, triangle, is_selected):
       # Pygame rendering code
   ```

4. **Engine**: Add creation hotkey
   ```python
   elif event.key == pygame.K_t:
       self.viewmodel.create_triangle(x, y)
   ```

### Adding New Interactions (添加新交互)

1. **ViewModel**: Add business logic methods
2. **View**: Add visual feedback if needed
3. **Engine**: Add event handling

## File Organization | 文件组织

```
PlaneMotion/
├── lib/                         # Library root
│   ├── __init__.py             # Library package
│   ├── model/                  # Model: Component data structures
│   │   ├── __init__.py
│   │   ├── component.py       # Component, Circle, Rectangle
│   │   └── connection.py      # Connection
│   ├── viewmodel/             # ViewModel: Business logic
│   │   ├── __init__.py
│   │   └── plane_motion_viewmodel.py
│   ├── view/                  # View: Rendering layer
│   │   ├── __init__.py
│   │   └── plane_motion_view.py
│   └── utils/                 # Utility: Serialization
│       ├── __init__.py
│       └── save_load.py
├── engine.py                  # Controller: Coordination
├── main.py                    # Entry point
├── MVVM_Architecture.md       # This file
└── PROJECT_STRUCTURE.md       # Directory structure guide
```

## Best Practices | 最佳实践

1. **Never** import pygame in Model layer
2. **Never** put business logic in View layer
3. **Always** go through ViewModel for state changes
4. **Keep** Model classes as pure data structures
5. **Use** ViewModel as the single source of truth for state
6. **Delegate** all rendering to View layer

## Conclusion | 结论

The MVVM architecture in PlaneMotion provides a clean, maintainable, and extensible codebase. Each layer has clear responsibilities, making the system easy to understand, test, and extend.

PlaneMotion中的MVVM架构提供了一个清晰、可维护和可扩展的代码库。每一层都有明确的职责，使系统易于理解、测试和扩展。
