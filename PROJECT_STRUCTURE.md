# PlaneMotion - Project Structure

## Directory Organization

```
PlaneMotion/
├── lib/                          # Library root directory
│   ├── __init__.py              # Library package initialization
│   ├── model/                   # Model layer (Data)
│   │   ├── __init__.py         # Model exports
│   │   ├── component.py        # Component data models (Circle, Rectangle)
│   │   └── connection.py       # Connection data model
│   ├── viewmodel/              # ViewModel layer (Business Logic)
│   │   ├── __init__.py         # ViewModel exports
│   │   └── plane_motion_viewmodel.py  # Application business logic
│   ├── view/                   # View layer (Rendering)
│   │   ├── __init__.py         # View exports
│   │   └── plane_motion_view.py       # Pygame rendering
│   └── utils/                  # Utilities
│       ├── __init__.py         # Utils exports
│       └── save_load.py        # Save/Load functionality
├── engine.py                   # Engine (Controller/Coordinator)
├── main.py                     # Application entry point
├── MVVM_Architecture.md        # Architecture documentation
└── README.md                   # Project documentation
```

## Layer Responsibilities

### Model Layer (`lib/model/`)
**Pure data structures with no UI or business logic**

- `component.py`: Abstract `Component` class, `Circle`, and `Rectangle` implementations
- `connection.py`: `Connection` data model

**Key Features:**
- Geometric calculations (contains_point, get_connection_point)
- Data serialization/deserialization
- No pygame dependencies
- No business logic

### ViewModel Layer (`lib/viewmodel/`)
**Business logic and state management**

- `plane_motion_viewmodel.py`: `PlaneMotionViewModel` class

**Responsibilities:**
- Component creation and deletion
- Selection management
- Dragging operations
- Connection creation logic
- Scaling operations
- Status message management

### View Layer (`lib/view/`)
**Pygame rendering implementation**

- `plane_motion_view.py`: `PlaneMotionView` class

**Responsibilities:**
- Render components (circles, rectangles)
- Render connections
- Render UI overlays (help text, status messages)
- Selection visualization
- Connection preview rendering

### Utils Layer (`lib/utils/`)
**Utility functions and helpers**

- `save_load.py`: `SaveLoadManager` for scene persistence

**Responsibilities:**
- JSON serialization/deserialization
- File I/O operations

### Engine (`engine.py`)
**Controller that coordinates MVVM components**

**Responsibilities:**
- Game loop management
- Event handling
- Input delegation to ViewModel
- Rendering coordination

## Usage Example

```python
from lib.viewmodel import PlaneMotionViewModel
from lib.view import PlaneMotionView
from lib.model import Circle, Rectangle

# Create ViewModel
viewmodel = PlaneMotionViewModel()

# Create components
circle = viewmodel.create_circle(100, 100, radius=30)
rectangle = viewmodel.create_rectangle(200, 100, width=60, height=40)

# Create View
view = PlaneMotionView(viewmodel, width=1280, height=720)

# Render
view.render()
view.flip()
```

## Import Structure

### From Application Code
```python
# Import entire layers
from lib.model import Component, Circle, Rectangle, Connection
from lib.viewmodel import PlaneMotionViewModel
from lib.view import PlaneMotionView
from lib.utils import SaveLoadManager
```

### Within Library
```python
# Model layer (self-contained)
from lib.model import Component

# ViewModel layer (depends on Model)
from lib.model import Component, Circle, Rectangle, Connection

# View layer (depends on Model and ViewModel)
from lib.model import Component, Circle, Rectangle, Connection
from lib.viewmodel import PlaneMotionViewModel
```

## Benefits of This Structure

1. **Clear Separation**: Each layer has a dedicated folder
2. **Easy Navigation**: Files are organized by responsibility
3. **Import Clarity**: Package structure makes dependencies obvious
4. **Scalability**: Easy to add new components, views, or utilities
5. **Testability**: Each layer can be tested independently
6. **Reusability**: lib/ can be used in other projects

## Adding New Features

### Adding a New Component
1. Add class to `lib/model/component.py`
2. Export from `lib/model/__init__.py`
3. Add creation method in `lib/viewmodel/plane_motion_viewmodel.py`
4. Add rendering method in `lib/view/plane_motion_view.py`

### Adding a New Interaction
1. Add business logic to `lib/viewmodel/plane_motion_viewmodel.py`
2. Add event handling in `engine.py`
3. Add visual feedback in `lib/view/plane_motion_view.py` (if needed)

### Adding a New Utility
1. Create module in `lib/utils/`
2. Export from `lib/utils/__init__.py`
3. Use in engine or other components as needed
