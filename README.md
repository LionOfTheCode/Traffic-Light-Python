# Traffic Light (Python)

A console-based simulation of a traffic light controller for a junction where several roads converge into one. Only one road is open to traffic at a time; the system cycles through all added roads, keeping each one open for a fixed interval before moving to the next, exactly as a real automated traffic light would.

## Features

- At startup, you set the maximum number of roads (queue capacity) and the interval (in seconds) each road stays open.
- Add roads one at a time via the menu, up to the configured capacity, and delete the oldest road from the rotation.
- Live, color-coded status view: **green** while a road is open, **yellow** during its last second before closing, **red** while closed, each with a countdown in seconds.
- A background thread keeps recalculating road states while the live view is open; returning to the menu (press Enter) stops the live updates.
- Graceful shutdown that stops the background thread cleanly.

## How it works

The system runs two cooperating threads:

- **Main thread** — shows the text menu and handles adding/deleting roads and switching to the live view. While the live view is open, the main thread is blocked waiting for Enter, so roads can only be added or deleted from the menu, not during the live view.
- **Background thread** (`print_system_settings`) — started once at launch and, while the live view is active, wakes up roughly once per second to recompute and print every road's status.

Roads are stored in a custom **circular queue** (`CircularQueue.py`), a fixed-capacity ring buffer that avoids shifting elements on insert/remove:

- `enqueue` / `dequeue` add/remove roads in FIFO order, raising `OverflowError` / `IndexError` when the queue is full or empty, respectively.
- `peek_front` / `peek_back` inspect the next road to close and the most recently added road without removing them.
- The queue also supports `len()` and iteration in front-to-rear order.

Each road is a small `Road` dataclass holding its `name` and `opens_at`, the timestamp at which it's scheduled to open. When a road is added, its `opens_at` is derived from the previously queued road's `opens_at + interval`, chaining roads one after another automatically; the first road added opens immediately.

On every tick of the live view, the background thread walks the whole queue once:

- If a road's open window has already fully expired, its `opens_at` is advanced to continue the rotation after the last road currently in the queue.
- The road is then printed as open or closed depending on whether the current time falls inside its `[opens_at, opens_at + interval]` window.

A `threading.Lock` guards access to the circular queue so that adding/deleting roads from the menu and the background thread's queue updates don't interleave unsafely.

## Menu options

| Key | Action |
|-----|--------|
| `1` | Add a road (prompts for a name) |
| `2` | Delete the road at the front of the queue |
| `3` | Open the live system view (press Enter to return to the menu) |
| `0` | Quit the application |

## Example session

Welcome to the traffic management system!
Input the number of roads:
2
Input the interval:
5
Menu:
1: Add
2: Delete
3: System
0: Quit
1
Input road name:
Main St
Main St Added!

Switching to the live view (`3`) shows each road's open/closed status, refreshed every second, until Enter is pressed to return to the menu.

## Project structure

Traffic Light (Python)/
└── task/
    ├── traffic_light.py    # TrafficLight class: menu, threading, and scheduling logic
    └── CircularQueue.py    # CircularQueue class used to store and rotate roads

## Requirements

- Python 3.14+
- No third-party packages are required to run the application itself.

## Running it

cd "Traffic Light (Python)/task"
python traffic_light.py

You'll first be asked for the maximum number of roads and the interval (in seconds) each road stays open. After that, use the menu to add roads, delete roads, or switch to the live system view.

## Links

Project page: https://hyperskill.org/projects/351

My profile: https://hyperskill.org/profile/629163740