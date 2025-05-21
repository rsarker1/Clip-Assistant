# Clip Assistant

This application runs in your system tray and listens for voice commands to control OBS Studio for recording and creating video clips.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Table of Contents
- [Clip Assistant](#clip-assistant)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [End‑User Installation](#enduser-installation)
    - [Developer Installation](#developer-installation)
  - [Usage](#usage)
  - [Troubleshooting](#troubleshooting)
  - [Future Features](#future-features)

## Features

- **System Tray Integration**: Runs quietly in the background
- **Voice Activation**: Start/stop recording and clipping with voice commands
- **Status Notifications**: Notifications for application state via TTS or notification tray

## Getting Started

### Prerequisites

- **Python 3.10+** (for developer/source)  

## Installation

### End‑User Installation

1. Download the latest release from [Releases](https://github.com/\<username\>/\<repo\>/releases).  
2. Double‑click **`Freya.exe`**.  
3. The app will launch — no further setup required!

### Developer Installation 

1. **Install dependencies**:
   ```bash
   pip install vosk simpleobsws PyQt6 pyttsx3 sounddevice
   ```

2. **Download a Vosk model**:
   - Get a model from https://alphacephei.com/vosk/models
   - Extract to a folder named "model" in the same directory as the application


3. **Configure OBS**:
   - Enable WebSocket server in OBS (Tools → WebSocket Server Settings)
   - Note the port and password if you've set one

4. **Configure the application**:
   - Edit **`yaml_config.py`** to match your settings. You could also modify **`config.yaml`**, which is generated on the first run of the application. 

## Usage

1. **Start the application**:
   ```bash
   python main.py
   ```
   **OR**
   Double-click **`Freya.exe`**

2. **Using voice commands**:
   - Say "Freya start recording" to start recording
   - Say "Freya stop recording" to stop recording
   - Say "Freya start replay" to start the replay buffer
   - Say "Freya stop replay" to stop the replay buffer
   - Say "Freya start everything" to start both recording and the replay buffer
   - Say "Freya stop everything" to stop both recording and the replay buffer
   - Say "Freya clip it" or "Freya clip that" to clip the last 30 seconds of video

3. **Managing the application**:
   - Access settings from the context menu
     - Here you can also manage OBS specific settings
   - Exit the application from the context menu

## Troubleshooting

- **No audio detection**: Verify microphone settings. The application will use your primary microphone for input. 
- **OBS connection issues**: Ensure OBS is running and WebSocket is enabled
- **Voice commands not recognized**: Try adjusting your microphone

## Future Features

- Fully integrated startup functionality. Currently you would have to do it yourself for your operating system
- The ability to change the activation phrase