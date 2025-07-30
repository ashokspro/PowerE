# ⚡ PowerE

A Python application for automated task scheduling with both command-line and graphical user interface options.

---

## ✨ Features

- 🖥️ **Dual Interface**: Run in headless mode for background operations or with GUI for interactive scheduling
- ⏱️ **Task Scheduling**: Schedule and manage automated tasks with precise timing control
- 💻 **Cross-Platform**: Available as Python script and Windows executable
- 🔄 **Background Processing**: Designed for continuous background operation
- 👨‍💻 **User-Friendly**: Intuitive GUI for easy task configuration and monitoring

---

## 🛠️ Installation

### 📋 Prerequisites

- 🐍 Python 3.7 or higher
- 📦 Required dependencies (see `requirements.txt`)

### 🔧 Setup

1. Clone the repository:
```bash
git clone https://github.com/ashokspro/PowerE.git
cd PowerE
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface (Headless Mode)

Run the application in background mode without GUI:

```bash
python PowerE.py
```

This mode is ideal for:
- Server deployments
- Background automation
- Scheduled system tasks
- Continuous operation without user interaction

### Graphical User Interface

Launch the application with GUI for interactive scheduling:

```bash
python PowerE.py --head
```

The GUI provides:
- Visual task scheduling interface
- Real-time status monitoring
- Easy configuration management
- Interactive timing controls

### Executable Distribution

For systems without Python installed, use the provided executable:

#### Windows

1. **Headless Mode**: Double-click `POWER-E.exe` or run from command prompt
2. **GUI Mode**: Use the provided batch file or run:
```cmd
POWER-E.exe --head
```

Or use the convenience batch file:
```cmd
PowerE_GUI.bat
```

#### Auto-Start Setup (Windows)

To run PowerE automatically at system startup:

1. **Press `Win + R`** and type `shell:startup`, then press Enter
2. **Copy `POWER-E.exe`** to the startup folder that opens
3. **Create a shortcut** (optional) and modify properties to add `--head` argument for GUI mode

This ensures PowerE runs automatically when Windows starts, perfect for continuous background automation.


## Scheduling Tasks

### Via GUI
1. Launch the application with `--head` argument
2. Use the scheduling interface to set up your tasks
3. Configure timing, frequency, and other parameters
4. Save and activate your schedule

## Development

### Running from Source

```bash
# Headless mode
python main.py

# GUI mode
python main.py --head
```

### Building Executable

[Add instructions for building the executable using PyInstaller or similar]

```bash
pyinstaller --onefile --windowed PowerE.py
```


### Areas for Contribution

- [ ] Additional scheduling algorithms
- [ ] Enhanced GUI features
- [ ] Cross-platform executable support
- [ ] Performance optimizations
- [ ] Documentation improvements
- [ ] Bug fixes and testing


## Roadmap

- [ ] Web-based interface
- [ ] API integration
- [ ] Enhanced logging and monitoring
- [ ] Plugin system

gelog

### Version 1.0.0
- Initial release with CLI and GUI modes
- Basic task scheduling functionality
- Windows executable distribution

---

**Made with ❤️ by [ashokspro](https://github.com/ashokspro)**

For questions or suggestions, feel free to reach out or open an issue!
