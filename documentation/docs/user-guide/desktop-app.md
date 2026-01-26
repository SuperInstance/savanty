# Desktop App

The Savanty desktop app provides a native GUI for solving optimization problems.

## Installation

```bash
# Run directly
uvx --from 'savanty[desktop]' savanty-desktop

# Or install permanently
pip install 'savanty[desktop]'
savanty-desktop
```

## Interface Overview

### Main Window

The desktop app provides a clean interface with:

- **Problem Input** - Text area for your problem description
- **Example Selector** - Dropdown with pre-built examples
- **Solve Button** - Submits your problem
- **Results Panel** - Shows solution, ASP code, and visualization

### Built-in Examples

Select from ready-made examples:

1. **Nurse Scheduling** - Hospital shift scheduling with constraints
2. **Bakery Delivery** - Route planning with time windows
3. **Support Tickets** - Task assignment with skills
4. **Wedding Seating** - Event seating with relationships
5. **Course Timetabling** - University scheduling
6. **Startup Team** - Team formation with skills

### Results Tabs

After solving, switch between:

- **Solution** - The assignments and schedule
- **ASP Code** - The generated logic program
- **Visualization** - Formatted display

## Workflow

1. **Select an example** or write your own problem
2. **Click "Solve"** to process
3. **Answer questions** if Savanty needs clarification
4. **Review results** in the tabbed panel

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Solve problem |
| `Ctrl+N` | Clear input |
| `Ctrl+Q` | Quit application |

## Configuration

The desktop app uses the same environment variables as other interfaces:

```bash
export OPENAI_API_KEY=your_key_here
export SAVANTY_LLM_MODEL=openai/gpt-4o
```

## Requirements

The desktop app requires the Slint UI library:

- **Linux**: Works on most distributions with X11 or Wayland
- **macOS**: macOS 11 (Big Sur) or later
- **Windows**: Windows 10 or later with Visual C++ Redistributable

## Troubleshooting

### "Slint not found"

Reinstall with desktop extras:

```bash
pip install 'savanty[desktop]' --force-reinstall
```

### Window doesn't appear

Check your display environment:

```bash
# Linux
echo $DISPLAY

# If using Wayland
export QT_QPA_PLATFORM=wayland
```

### High DPI scaling issues

Set scaling factor:

```bash
# Linux
export QT_SCALE_FACTOR=1.5

# Windows (set in system settings)
```
