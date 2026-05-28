# workout-tracker
Workout and exercise progression tracker

## Installation & Running

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

1. **Clone the repository**
```bash
   git clone https://github.com/Zasajin/workout-tracker.git
   cd workout-tracker
```

2. **Create and activate virtual environment** (recommended)
```bash
   python -m venv venv
   
   # Linux/macOS
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
```

3. **Install dependencies**
```bash
   cd wt25
   pip install -e .
```

4. **Run the application**
```bash
   briefcase dev
```

The app will create a database file automatically at:
- **Linux:** `~/.local/share/wt25/workouts.db`
- **macOS:** `~/Library/Application Support/wt25/workouts.db`
- **Windows:** `%APPDATA%\wt25\workouts.db`

### Building for Distribution

To create a standalone executable:
```bash
briefcase build
briefcase package
```

Scheduled changes:
- refining add_exercise()
- adjusting display boxes (width/height, e.g calender box)
- refactoring code base
