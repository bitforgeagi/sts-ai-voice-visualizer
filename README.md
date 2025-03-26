# AI Voice Visualization Animations

This project provides a set of dynamic, responsive animations for visualizing different AI voice interaction states. The animations use a dot matrix visualization with smooth transitions between states to create an engaging user experience. You can use the animations in your own projects by integrating the `animation_settings.py` and `transitions.py` modules.
<img width="1379" alt="Screenshot 2025-03-26 at 8 59 48 AM" src="https://github.com/user-attachments/assets/2273825c-6bff-4178-8821-f776f7c2a66b" />

This is a a free open source project for anyone wanting to animmate speech to speech AI applications in python. Its not optimized for production use and is a work in progress. You can support the project by starring the repo or following [Bitforge Dynamics](www.bitforgedynamics.com) on [X](https://x.com/bitforgeagi) 
## Features

- **Multiple Animation States**:
  - **Listening**: White dot matrix animation that responds to user input
  <img width="398" alt="Screenshot 2025-03-26 at 8 57 57 AM" src="https://github.com/user-attachments/assets/1e242897-c3ce-4a52-a421-a9188f0bfbe7" />

  - **Processing**: Light blue concentric rings that flow inward
  <img width="401" alt="Screenshot 2025-03-26 at 8 58 01 AM" src="https://github.com/user-attachments/assets/0f898272-8e08-48bc-85a6-11216c68f3c8" />

  - **Speaking**: Vibrant blue matrix-like effect that responds to audio
  <img width="396" alt="Screenshot 2025-03-26 at 8 58 06 AM" src="https://github.com/user-attachments/assets/f4826663-d5e0-4814-beae-dc0a9bdeb446" />

  - **Idle**: Subtle blue-gray ambient animation for transitioning (see demo)
    

- **Smooth Transitions**: Elegant transitions between all animation states
- **Audio Responsiveness**: Speaking animation reacts to audio input features
- **Modular Design**: Can be used as a standalone widget or integrated into larger applications
- **Responsive Sizing**: Automatically adjusts to different window sizes

## Demo

The project includes two demo applications:

1. **GUI Manager**: A test interface with buttons to switch between animation states
2. **Voice Widget Example**: A more polished example showing how to integrate the animations into an application

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/bitforgeagi/sts-ai-voice-visualizer.git
   cd sts-ai-voice-visualizer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Demo


To run the Voice Widget Example:

```
python -m voice_widget_example
```

or
```
python3 -m voice_widget_example
```

You may use these designs for any purpose, granted you credit the authors

Open Sourced by Brock Daily &

██████╗ ██╗████████╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗   
██╔══██╗██║╚══██╔══╝██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝   
██████╔╝██║   ██║   █████╗  ██║   ██║██████╔╝██║  ███╗█████╗     
██╔══██╗██║   ██║   ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝     
██████╔╝██║   ██║   ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗   
╚═════╝ ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   
                                                                 
██████╗ ██╗   ██╗███╗   ██╗ █████╗ ███╗   ███╗██╗ ██████╗███████╗
██╔══██╗╚██╗ ██╔╝████╗  ██║██╔══██╗████╗ ████║██║██╔════╝██╔════╝
██║  ██║ ╚████╔╝ ██╔██╗ ██║███████║██╔████╔██║██║██║     ███████╗
██║  ██║  ╚██╔╝  ██║╚██╗██║██╔══██║██║╚██╔╝██║██║██║     ╚════██║
██████╔╝   ██║   ██║ ╚████║██║  ██║██║ ╚═╝ ██║██║╚██████╗███████║
╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝ ╚═════╝╚══════╝


