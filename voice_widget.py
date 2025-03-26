import pygame
import numpy as np
import time
import random
from enum import Enum
from ai_speaking_animation import AISpeakingAnimation
from listening_animation import ListeningAnimation
from processing_animation import ProcessingAnimation
from animation_settings import AnimationSettings
from transitions import AnimationTransition

class AnimationState(Enum):
    """Enum representing the different states of the voice widget"""
    IDLE = 0
    LISTENING = 1
    PROCESSING = 2
    SPEAKING = 3

class VoiceWidget:
    """
    A modular voice widget that visualizes different AI states with smooth transitions.
    Can be embedded in any pygame-based application or used standalone.
    """
    
    def __init__(self, width=200, height=200):
        """
        Initialize the voice widget.
        
        Args:
            width (int): Width of the widget
            height (int): Height of the widget
        """
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Create the surface
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Create shared animation settings
        self.settings = AnimationSettings(width, height)
        
        # Create the animations
        self.speaking_animation = AISpeakingAnimation(width, height)
        self.listening_animation = ListeningAnimation(width, height)
        self.processing_animation = ProcessingAnimation(width, height)
        
        # Create transition handler
        self.transition = AnimationTransition(self.settings)
        
        # Current state
        self.current_state = AnimationState.LISTENING
        self.previous_state = None
        
        # Simulated audio features for the speaking animation
        self.last_audio_update = 0
        self.audio_update_interval = 0.05  # 50ms
        
        # For capturing real audio features
        self.live_audio_features = None
    
    def resize(self, width, height):
        """
        Resize the widget.
        
        Args:
            width (int): New width
            height (int): New height
        """
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Resize animations
        self.settings.resize(width, height)
        self.speaking_animation.resize(width, height)
        self.listening_animation.resize(width, height)
        self.processing_animation.resize(width, height)
    
    def set_state(self, state):
        """
        Set the current animation state with a smooth transition.
        
        Args:
            state (AnimationState): The new state
        """
        if state == self.current_state:
            return
        
        # Store the previous state for transition
        self.previous_state = self.current_state
        
        # Start the transition
        self.transition.start_transition(
            from_state=self.current_state.name.lower(),
            to_state=state.name.lower(),
            duration=45  # About 1.5 seconds at 30 FPS
        )
        
        # Freeze the current matrix for transition effects
        current_matrix = self._get_current_matrix()
        if current_matrix is not None:
            self.transition.freeze_matrix(current_matrix)
        
        # Update the current state
        self.current_state = state
        
        # Special case for processing to speaking transition
        if self.previous_state == AnimationState.PROCESSING and state == AnimationState.SPEAKING:
            self._start_processing_to_speaking_transition()
    
    def _start_processing_to_speaking_transition(self):
        """Start a smooth transition from processing to speaking animation"""
        # Capture the current processing animation state
        self.transition.processing_matrix = self.processing_animation.matrix.copy()
        self.transition.processing_to_speaking_start_frame = self.settings.frame_count
        self.transition.processing_to_speaking_active = True
    
    def _get_current_matrix(self):
        """Get the matrix from the current animation"""
        if self.current_state == AnimationState.SPEAKING:
            return self.speaking_animation.matrix
        elif self.current_state == AnimationState.LISTENING:
            return self.listening_animation.matrix
        elif self.current_state == AnimationState.PROCESSING:
            return self.processing_animation.matrix
        return None
    
    def set_audio_features(self, features):
        """
        Set audio features for visualization during speaking.
        
        Args:
            features (dict): Dictionary containing audio features:
                - 'spec': Mel spectrogram (2D array)
                - 'energy': Overall audio energy (float)
                - 'onset': Onset detection value (float)
        """
        self.live_audio_features = features
        if self.current_state == AnimationState.SPEAKING:
            self.speaking_animation.set_audio_features(features)
    
    def update_simulated_audio(self):
        """Update simulated audio features for the speaking animation"""
        current_time = time.time()
        if current_time - self.last_audio_update > self.audio_update_interval:
            # Create simulated audio features
            t = current_time
            simulated_features = {
                'spec': np.random.rand(64, 1),  # Random spectrogram
                'energy': 0.5 + 0.5 * np.sin(t * 0.5),  # Oscillating energy
                'onset': 0.1 + 0.1 * np.sin(t * 2.0)  # Oscillating onset detection
            }
            self.speaking_animation.set_audio_features(simulated_features)
            self.last_audio_update = current_time
    
    def update(self):
        """
        Update the widget animation.
        
        Returns:
            pygame.Surface: The updated surface
        """
        # Increment the frame counter
        self.settings.increment_frame()
        
        # Update simulated audio if no real audio is provided
        if self.current_state == AnimationState.SPEAKING and self.live_audio_features is None:
            self.update_simulated_audio()
        
        # Get the target animation surface
        target_surface = None
        
        if self.current_state == AnimationState.SPEAKING:
            target_surface = self.speaking_animation.update()
        elif self.current_state == AnimationState.LISTENING:
            target_surface = self.listening_animation.update()
        elif self.current_state == AnimationState.PROCESSING:
            target_surface = self.processing_animation.update()
        elif self.current_state == AnimationState.IDLE:
            # For idle state, use a dimmed version of the listening animation
            self.listening_animation.set_color((80, 80, 100))  # Soft blue-gray
            target_surface = self.listening_animation.update()
            self.listening_animation.set_color(self.settings.colors["listening"])  # Reset color
        
        # Apply transition effects if needed
        if self.transition.is_active() and self.previous_state:
            # Apply matrix-level transition
            prev_matrix = None
            target_matrix = None
            
            # Get the previous animation matrix
            if self.previous_state == AnimationState.SPEAKING:
                prev_matrix = self.speaking_animation.matrix
            elif self.previous_state == AnimationState.LISTENING:
                prev_matrix = self.listening_animation.matrix
            elif self.previous_state == AnimationState.PROCESSING:
                prev_matrix = self.processing_animation.matrix
            
            # Get the target animation matrix
            if self.current_state == AnimationState.SPEAKING:
                target_matrix = self.speaking_animation.matrix
            elif self.current_state == AnimationState.LISTENING:
                target_matrix = self.listening_animation.matrix
            elif self.current_state == AnimationState.PROCESSING:
                target_matrix = self.processing_animation.matrix
            
            # Apply the transition
            if prev_matrix is not None and target_matrix is not None:
                blended_matrix = self.transition.apply_transition(prev_matrix, target_matrix)
                
                # Apply the blended matrix to the current animation
                if self.current_state == AnimationState.SPEAKING:
                    self.speaking_animation.matrix = blended_matrix
                    target_surface = self.speaking_animation.draw()
                elif self.current_state == AnimationState.LISTENING:
                    self.listening_animation.matrix = blended_matrix
                    target_surface = self.listening_animation.draw()
                elif self.current_state == AnimationState.PROCESSING:
                    self.processing_animation.matrix = blended_matrix
                    target_surface = self.processing_animation.draw()
        
        # Update the surface
        if target_surface:
            self.surface = target_surface
        
        return self.surface
    
    def get_surface(self):
        """
        Get the current surface.
        
        Returns:
            pygame.Surface: The current surface
        """
        return self.surface

# Example usage
if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    
    # Create a window
    screen = pygame.display.set_mode((400, 400), pygame.RESIZABLE)
    pygame.display.set_caption("Voice Widget Demo")
    
    # Create the widget
    widget = VoiceWidget(400, 400)
    
    # Set up a clock for controlling the frame rate
    clock = pygame.time.Clock()
    
    # Demo sequence
    demo_sequence = [
        {"state": AnimationState.LISTENING, "duration": 3.0},
        {"state": AnimationState.PROCESSING, "duration": 3.0},
        {"state": AnimationState.SPEAKING, "duration": 5.0},
        {"state": AnimationState.LISTENING, "duration": 3.0}
    ]
    
    # Demo state
    demo_current_step = 0
    demo_step_start_time = time.time()
    
    # Main loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                widget.resize(event.w, event.h)
            elif event.type == pygame.KEYDOWN:
                # Change state with keyboard
                if event.key == pygame.K_1:
                    widget.set_state(AnimationState.LISTENING)
                elif event.key == pygame.K_2:
                    widget.set_state(AnimationState.PROCESSING)
                elif event.key == pygame.K_3:
                    widget.set_state(AnimationState.SPEAKING)
                elif event.key == pygame.K_0:
                    widget.set_state(AnimationState.IDLE)
        
        # Update demo sequence
        current_time = time.time()
        current_step = demo_sequence[demo_current_step]
        
        if current_time - demo_step_start_time > current_step["duration"]:
            # Move to the next step
            demo_current_step = (demo_current_step + 1) % len(demo_sequence)
            demo_step_start_time = current_time
            
            # Change to the next state
            next_step = demo_sequence[demo_current_step]
            widget.set_state(next_step["state"])
        
        # Update the widget
        widget_surface = widget.update()
        
        # Draw the widget to the screen
        screen.fill((30, 30, 40))
        screen.blit(widget_surface, (0, 0))
        
        # Display current state
        font = pygame.font.SysFont('Arial', 18)
        state_text = f"State: {widget.current_state.name}"
        text_surface = font.render(state_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(30)
    
    # Clean up
    pygame.quit()
