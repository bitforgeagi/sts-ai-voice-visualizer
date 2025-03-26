# gui_manager.py

# This file is responsible for managing the GUI for the application.
# It will handle the creation and updating of the GUI elements.
# It will also handle the communication between the GUI and the other components of the application.

# I want to use this to test our animations. We should have a pannel of buttons to test each animation.

import pygame
import sys
import time
import numpy as np
import random
from ai_speaking_animation import AISpeakingAnimation
from listening_animation import ListeningAnimation
from processing_animation import ProcessingAnimation
from animation_settings import AnimationSettings
from transitions import AnimationTransition

class GUIManager:
    """
    GUI Manager for testing and demonstrating the different animation states with
    smooth transitions between states that match the original implementation.
    """
    
    def __init__(self, width=800, height=600):
        """
        Initialize the GUI Manager.
        
        Args:
            width (int): Width of the window
            height (int): Height of the window
        """
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Create the window
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Animation Test GUI")
        
        # Set up the font
        self.font = pygame.font.SysFont('Arial', 18)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        
        # Create shared animation settings
        animation_size = min(width - 200, height - 40)  # Leave space for buttons
        self.animation_width = animation_size
        self.animation_height = animation_size
        self.settings = AnimationSettings(animation_size, animation_size)
        
        # Animation position (centered in the main area)
        self.animation_x = (width - 200) // 2 - animation_size // 2
        self.animation_y = height // 2 - animation_size // 2
        
        # Create the animations
        self.speaking_animation = AISpeakingAnimation(animation_size, animation_size)
        self.listening_animation = ListeningAnimation(animation_size, animation_size)
        self.processing_animation = ProcessingAnimation(animation_size, animation_size)
        
        # Create transition handler
        self.transition = AnimationTransition(self.settings)
        
        # Current animation state
        self.current_animation = "listening"
        self.previous_animation = None
        
        # Transition-specific variables
        self.frozen_matrix = None
        self.frozen_dots = []
        self.transition_active = False
        self.transition_start_frame = 0
        self.transition_duration = 30  # frames (about 1 second at 30 FPS)
        
        # Processing to speaking transition
        self.processing_to_speaking_active = False
        self.processing_to_speaking_start_frame = 0
        self.processing_to_speaking_duration = 45  # frames (about 1.5 seconds at 30 FPS)
        self.processing_matrix = None
        
        # Button definitions
        button_width = 180
        button_height = 40
        button_x = width - 190
        button_y_start = 50
        button_spacing = 20
        
        self.buttons = [
            {
                "rect": pygame.Rect(button_x, button_y_start, button_width, button_height),
                "text": "Listening Animation",
                "action": "listening",
                "color": (220, 220, 220),
                "hover_color": (240, 240, 240),
                "text_color": (20, 20, 20)
            },
            {
                "rect": pygame.Rect(button_x, button_y_start + button_height + button_spacing, 
                                   button_width, button_height),
                "text": "Processing Animation",
                "action": "processing",
                "color": (180, 200, 240),
                "hover_color": (200, 220, 255),
                "text_color": (20, 20, 20)
            },
            {
                "rect": pygame.Rect(button_x, button_y_start + 2 * (button_height + button_spacing), 
                                   button_width, button_height),
                "text": "AI Speaking Animation",
                "action": "speaking",
                "color": (60, 180, 255),
                "hover_color": (80, 200, 255),
                "text_color": (20, 20, 20)
            },
            {
                "rect": pygame.Rect(button_x, button_y_start + 3 * (button_height + button_spacing), 
                                   button_width, button_height),
                "text": "Run Demo Sequence",
                "action": "demo",
                "color": (100, 180, 100),
                "hover_color": (120, 200, 120),
                "text_color": (255, 255, 255)
            },
            {
                "rect": pygame.Rect(button_x, button_y_start + 4 * (button_height + button_spacing), 
                                   button_width, button_height),
                "text": "Exit",
                "action": "exit",
                "color": (200, 80, 80),
                "hover_color": (220, 100, 100),
                "text_color": (255, 255, 255)
            }
        ]
        
        # Simulated audio features for the speaking animation
        self.last_audio_update = 0
        self.audio_update_interval = 0.05  # 50ms
        
        # Demo sequence settings
        self.demo_active = False
        self.demo_sequence = [
            {"state": "listening", "duration": 3.0},
            {"state": "processing", "duration": 3.0},
            {"state": "speaking", "duration": 5.0},
            {"state": "listening", "duration": 3.0}
        ]
        self.demo_current_step = 0
        self.demo_step_start_time = 0
        
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
    
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
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN and not self.demo_active:
                # Check if any button was clicked
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["action"] == "exit":
                            return False
                        elif button["action"] == "demo":
                            self.start_demo_sequence()
                        else:
                            self.change_animation(button["action"])
            
            if event.type == pygame.VIDEORESIZE:
                # Update window size
                self.width = event.w
                self.height = event.h
                
                # Calculate new animation size
                animation_size = min(self.width - 200, self.height - 40)
                self.animation_width = animation_size
                self.animation_height = animation_size
                
                # Update animation position
                self.animation_x = (self.width - 200) // 2 - animation_size // 2
                self.animation_y = self.height // 2 - animation_size // 2
                
                # Resize animations
                self.settings.resize(animation_size, animation_size)
                self.speaking_animation.resize(animation_size, animation_size)
                self.listening_animation.resize(animation_size, animation_size)
                self.processing_animation.resize(animation_size, animation_size)
                
                # Update button positions
                button_x = self.width - 190
                for i, button in enumerate(self.buttons):
                    button_y = 50 + i * (40 + 20)  # button_height + button_spacing
                    button["rect"] = pygame.Rect(button_x, button_y, 180, 40)
        
        return True
    
    def _freeze_current_matrix(self):
        """Freeze the current matrix state for transition effects, matching original implementation"""
        # Determine which matrix to freeze based on current animation
        current_matrix = None
        if self.current_animation == "speaking":
            current_matrix = self.speaking_animation.matrix
        elif self.current_animation == "listening":
            current_matrix = self.listening_animation.matrix
        elif self.current_animation == "processing":
            current_matrix = self.processing_animation.matrix
        
        if current_matrix is not None:
            # Store a copy of the current matrix
            self.frozen_matrix = current_matrix.copy()
            
            # Store the positions of active dots
            self.frozen_dots = []
            for y in range(self.settings.dots_y):
                for x in range(self.settings.dots_x):
                    if self.frozen_matrix[y, x] > 0.2:  # Lower threshold to capture more dots
                        nx, ny, dist = self.settings.get_normalized_position(x, y)
                        self.frozen_dots.append({
                            'x': x,
                            'y': y,
                            'intensity': self.frozen_matrix[y, x],
                            'nx': nx,
                            'ny': ny,
                            'dist': dist,
                            'offset': random.random() * 2 * np.pi,  # Random phase offset for animation
                            'speed': 0.5 + random.random() * 1.0,   # Random speed for floating effect
                        })
            
            # If we don't have enough dots, add some based on the current state's pattern
            if len(self.frozen_dots) < 50 and self.current_animation == "speaking":
                # Add additional dots in a pattern matching the speaking animation
                for _ in range(25):
                    # Random position within the circle
                    angle = random.random() * 2 * np.pi
                    dist = random.random() * 0.9
                    nx = np.cos(angle) * dist
                    ny = np.sin(angle) * dist
                    
                    # Convert to matrix coordinates
                    x = int((nx * self.settings.radius + self.settings.center_x) / self.settings.dot_spacing)
                    y = int((ny * self.settings.radius + self.settings.center_y) / self.settings.dot_spacing)
                    
                    # Check if coordinates are valid
                    if (0 <= x < self.settings.dots_x and 
                        0 <= y < self.settings.dots_y and 
                        self.settings.dot_mask[y, x]):
                        
                        self.frozen_dots.append({
                            'x': x,
                            'y': y,
                            'intensity': 0.5 + 0.3 * random.random(),
                            'nx': nx,
                            'ny': ny,
                            'dist': dist,
                            'offset': random.random() * 2 * np.pi,
                            'speed': 0.5 + random.random() * 1.0,
                        })
            
            self.transition_start_frame = self.settings.frame_count
            self.transition_active = True
    
    def _start_processing_to_speaking_transition(self):
        """Start a smooth transition from processing to speaking animation"""
        # Capture the current processing animation state
        self.processing_matrix = self.processing_animation.matrix.copy()
        self.processing_to_speaking_start_frame = self.settings.frame_count
        self.processing_to_speaking_active = True
        print("Starting processing to speaking transition")
    
    def change_animation(self, new_animation):
        """
        Change to a new animation state with transition.
        
        Args:
            new_animation (str): The new animation state to transition to
        """
        if new_animation == self.current_animation:
            return
        
        # Store the previous animation for transition
        self.previous_animation = self.current_animation
        
        # Start the transition in the transitions module
        self.transition.start_transition(
            from_state=self.current_animation,
            to_state=new_animation,
            duration=45  # About 1.5 seconds at 30 FPS
        )
        
        # Freeze the current matrix for transition effects
        self.transition.freeze_matrix(self._get_current_matrix())
        
        # Update the current animation
        self.current_animation = new_animation
        
        # Reset transition-specific variables
        self.transition_active = True
        self.transition_start_frame = self.settings.frame_count
        
        # Special case for processing to speaking transition
        if self.previous_animation == "processing" and new_animation == "speaking":
            self._start_processing_to_speaking_transition()
    
    def _get_current_matrix(self):
        """Get the matrix from the current animation"""
        if self.current_animation == "speaking":
            return self.speaking_animation.matrix
        elif self.current_animation == "listening":
            return self.listening_animation.matrix
        elif self.current_animation == "processing":
            return self.processing_animation.matrix
        return None
    
    def start_demo_sequence(self):
        """Start the demo sequence that cycles through all animations"""
        self.demo_active = True
        self.demo_current_step = 0
        self.demo_step_start_time = time.time()
        
        # Start with the first animation in the sequence
        self.change_animation(self.demo_sequence[0]["state"])
    
    def update_demo_sequence(self):
        """Update the demo sequence if active"""
        if not self.demo_active:
            return
        
        # Check if it's time to move to the next step
        current_time = time.time()
        current_step = self.demo_sequence[self.demo_current_step]
        
        if current_time - self.demo_step_start_time > current_step["duration"]:
            # Move to the next step
            self.demo_current_step = (self.demo_current_step + 1) % len(self.demo_sequence)
            self.demo_step_start_time = current_time
            
            # Change to the next animation
            next_step = self.demo_sequence[self.demo_current_step]
            self.change_animation(next_step["state"])
            
            # If we've completed the sequence, stop the demo
            if self.demo_current_step == 0:
                self.demo_active = False
    
    def _apply_transition_effects(self, target_surface):
        """Apply transition effects between animation states"""
        # Create a blended surface for the transition
        blended_surface = pygame.Surface((self.animation_width, self.animation_height))
        blended_surface.fill((0, 0, 0))
        
        # Get the previous animation surface
        prev_surface = None
        if self.previous_animation == "speaking":
            prev_surface = self.speaking_animation.surface
        elif self.previous_animation == "listening":
            prev_surface = self.listening_animation.surface
        elif self.previous_animation == "processing":
            prev_surface = self.processing_animation.surface
        
        # Special case for speaking to listening transition
        if self.previous_animation == "speaking" and self.current_animation == "listening":
            # Calculate transition progress
            frames_since = self.settings.frame_count - self.transition_start_frame
            progress = min(1.0, frames_since / self.transition_duration)
            
            # Create a new surface for the transition
            transition_surface = pygame.Surface((self.animation_width, self.animation_height))
            transition_surface.fill((0, 0, 0))
            
            # Early phase: keep the speaking animation but start color transition
            if progress < 0.6:
                # Get the speaking animation surface
                speaking_surface = prev_surface.copy()
                
                # Apply a slight fade to prepare for pattern change
                speaking_surface.set_alpha(int(255 * (1.0 - progress * 0.3)))
                transition_surface.blit(speaking_surface, (0, 0))
                
                return transition_surface
            
            # Later phase: blend in the listening animation
            else:
                # Calculate blend factor
                blend_factor = (progress - 0.6) / 0.4  # 0 at 0.6, 1.0 at 1.0
                
                # Draw the speaking animation with fading
                speaking_fade = 1.0 - blend_factor
                if speaking_fade > 0:
                    speaking_surface = prev_surface.copy()
                    speaking_surface.set_alpha(int(255 * speaking_fade))
                    transition_surface.blit(speaking_surface, (0, 0))
                
                # Draw the listening animation with increasing opacity
                listening_fade = blend_factor
                if listening_fade > 0:
                    listening_surface = target_surface.copy()
                    listening_surface.set_alpha(int(255 * listening_fade))
                    transition_surface.blit(listening_surface, (0, 0))
                
                return transition_surface
        
        # If we have a processing to speaking transition
        elif self.processing_to_speaking_active and self.current_animation == "speaking":
            # Calculate transition progress
            frames_since = self.settings.frame_count - self.processing_to_speaking_start_frame
            progress = min(1.0, frames_since / self.processing_to_speaking_duration)
            
            # Print status
            if frames_since == 0:
                print("Starting processing to speaking transition")
            
            # If transition is complete, deactivate it
            if progress >= 1.0:
                self.processing_to_speaking_active = False
                self.processing_matrix = None
                return target_surface
            
            # Create a smooth transition from processing to speaking
            # Use quadratic easing for smoother transition
            ease_factor = progress * (2 - progress)  # Quadratic ease-in-out
            
            # Create a new surface for the transition
            transition_surface = pygame.Surface((self.animation_width, self.animation_height))
            transition_surface.fill((0, 0, 0))
            
            # Draw the processing animation with fading
            processing_fade = 1.0 - ease_factor
            if processing_fade > 0:
                # Get the processing animation surface
                processing_surface = self.processing_animation.surface.copy()
                processing_surface.set_alpha(int(255 * processing_fade))
                transition_surface.blit(processing_surface, (0, 0))
            
            # Draw the speaking animation with increasing opacity
            speaking_fade = ease_factor
            if speaking_fade > 0:
                # Get the speaking animation surface
                speaking_surface = target_surface.copy()
                speaking_surface.set_alpha(int(255 * speaking_fade))
                transition_surface.blit(speaking_surface, (0, 0))
            
            return transition_surface
        
        # For other transitions, use the transition handler
        elif self.transition.is_active() and prev_surface:
            progress = self.transition.get_progress()
            
            # Special transition from speaking to listening
            if self.previous_animation == "speaking" and self.current_animation == "listening":
                # Create a surface for the dots
                dot_surface = pygame.Surface((self.animation_width, self.animation_height), pygame.SRCALPHA)
                dot_surface.fill((0, 0, 0, 0))  # Transparent background
                
                # First, draw the frozen blue matrix dots with fading
                for dot in self.frozen_dots:
                    x, y = dot['x'], dot['y']
                    if 0 <= x < self.settings.dots_x and 0 <= y < self.settings.dots_y:
                        # Calculate position-based effects
                        nx, ny = dot['nx'], dot['ny']
                        dist = np.sqrt(nx*nx + ny*ny)
                        
                        # Dots gradually expand outward from center
                        expansion_factor = 0.2 * progress
                        new_dist = dist * (1.0 + expansion_factor)
                        if new_dist > 1.0:  # Skip if expanded beyond the circle
                            continue
                            
                        # Calculate new position
                        angle = np.arctan2(ny, nx)
                        new_nx = np.cos(angle) * new_dist
                        new_ny = np.sin(angle) * new_dist
                        
                        # Convert back to matrix coordinates
                        new_x = int((new_nx * self.settings.radius + self.settings.center_x) / self.settings.dot_spacing)
                        new_y = int((new_ny * self.settings.radius + self.settings.center_y) / self.settings.dot_spacing)
                        
                        # Check if new position is valid
                        if (0 <= new_x < self.settings.dots_x and 
                            0 <= new_y < self.settings.dots_y):
                            
                            # Calculate intensity with gentle fade
                            fade = 1.0 - progress * 0.5  # Fade to 50% over transition
                            intensity = dot['intensity'] * fade
                            
                            # Add gentle pulsing
                            t = self.settings.frame_count * 0.05
                            pulse = 0.8 + 0.2 * np.sin(t * 2 + dot['offset'])
                            intensity *= pulse
                            
                            # Skip if too faint
                            if intensity < 0.05:
                                continue
                            
                            # Calculate dot position
                            pos_x, pos_y = self.settings.get_dot_position(new_x, new_y)
                            
                            # Calculate color with blending from blue to white
                            from_color = np.array(self.settings.colors["speaking"])
                            to_color = np.array(self.settings.colors["listening"])
                            color_blend = progress * 1.5  # Faster color transition
                            
                            # Ensure color values are valid
                            r = max(0, min(255, int(from_color[0] * (1.0 - color_blend) + to_color[0] * color_blend)))
                            g = max(0, min(255, int(from_color[1] * (1.0 - color_blend) + to_color[1] * color_blend)))
                            b = max(0, min(255, int(from_color[2] * (1.0 - color_blend) + to_color[2] * color_blend)))
                            
                            # Scale by intensity
                            r = max(0, min(255, int(r * intensity)))
                            g = max(0, min(255, int(g * intensity)))
                            b = max(0, min(255, int(b * intensity)))
                            
                            color = (r, g, b)
                            
                            # Calculate dot size
                            dot_size = int(self.settings.dot_size * (0.8 + 0.4 * intensity))
                            
                            # Draw the dot
                            pygame.draw.circle(dot_surface, color, (pos_x, pos_y), dot_size)
                
                # Gradually blend in the listening state animation
                if progress > 0.3:  # Start blending earlier for smoother transition
                    # Calculate blend factor
                    blend_factor = (progress - 0.3) / 0.7  # 0 at 0.3, 1.0 at 1.0
                    
                    # Get the listening animation with adjusted alpha
                    listening_surface = target_surface.copy()
                    listening_surface.set_alpha(int(255 * blend_factor))
                    
                    # Create the blended result
                    blended_surface.fill((0, 0, 0))
                    blended_surface.blit(listening_surface, (0, 0))
                    blended_surface.blit(dot_surface, (0, 0))
                    
                    return blended_surface
                else:
                    # Just return the dot surface in early transition
                    return dot_surface
            
            # Special transition from listening to processing
            elif self.previous_animation == "listening" and self.current_animation == "processing":
                # Create a surface for the dots
                dot_surface = pygame.Surface((self.animation_width, self.animation_height), pygame.SRCALPHA)
                dot_surface.fill((0, 0, 0, 0))  # Transparent background
                
                # Early phase: dots float upward
                if progress < 0.4:
                    # Draw the listening animation with fading
                    listening_fade = 1.0 - (progress / 0.4)
                    blended_surface.fill((0, 0, 0))
                    prev_surface_copy = prev_surface.copy()
                    prev_surface_copy.set_alpha(int(255 * listening_fade))
                    blended_surface.blit(prev_surface_copy, (0, 0))
                    
                    # Draw floating dots
                    for dot in self.frozen_dots:
                        # Calculate floating effect - dots move upward
                        float_speed = dot['speed'] * progress * 5.0
                        new_y = dot['y'] - float_speed * 0.1
                        
                        # Add some horizontal drift
                        t = self.settings.frame_count * 0.05
                        drift = 0.2 * np.sin(t * 2 + dot['offset']) * progress
                        new_x = dot['x'] + drift
                        
                        # Convert to integer coordinates
                        int_x = int(new_x)
                        int_y = int(new_y)
                        
                        # Check if the new position is valid and draw the dot
                        if (0 <= int_x < self.settings.dots_x and 
                            0 <= int_y < self.settings.dots_y):
                            
                            # Apply fading effect
                            fade_factor = 1.0 - progress / 0.4
                            intensity = dot['intensity'] * fade_factor
                            
                            # Skip if too faint
                            if intensity < 0.05:
                                continue
                            
                            # Calculate dot position
                            pos_x, pos_y = self.settings.get_dot_position(int_x, int_y)
                            
                            # Calculate color with blending from white to light blue
                            from_color = np.array(self.settings.colors["listening"])
                            to_color = np.array(self.settings.colors["processing"])
                            color_blend = progress * 2.5  # Faster color transition
                            
                            # Ensure color values are valid
                            r = max(0, min(255, int(from_color[0] * (1.0 - color_blend) + to_color[0] * color_blend)))
                            g = max(0, min(255, int(from_color[1] * (1.0 - color_blend) + to_color[1] * color_blend)))
                            b = max(0, min(255, int(from_color[2] * (1.0 - color_blend) + to_color[2] * color_blend)))
                            
                            # Scale by intensity
                            r = max(0, min(255, int(r * intensity)))
                            g = max(0, min(255, int(g * intensity)))
                            b = max(0, min(255, int(b * intensity)))
                            
                            color = (r, g, b)
                            
                            # Calculate dot size
                            dot_size = int(self.settings.dot_size * (0.8 + 0.4 * intensity))
                            
                            # Draw the dot
                            pygame.draw.circle(dot_surface, color, (pos_x, pos_y), dot_size)
                    
                    # Blend the dot surface on top
                    blended_surface.blit(dot_surface, (0, 0))
                    
                    return blended_surface
                
                # Middle to final phase: blend in the processing rings
                else:
                    # Calculate blend factor
                    blend_factor = (progress - 0.4) / 0.6  # 0 at 0.4, 1.0 at 1.0
                    
                    # Get the processing animation with adjusted alpha
                    processing_surface = target_surface.copy()
                    processing_surface.set_alpha(int(255 * blend_factor))
                    
                    # Create the blended result
                    blended_surface.fill((0, 0, 0))
                    blended_surface.blit(processing_surface, (0, 0))
                    
                    # Add some residual floating dots that continue to fade
                    if self.frozen_dots and progress < 0.7:
                        fade_factor = 1.0 - (progress - 0.4) / 0.3  # 1.0 at 0.4, 0.0 at 0.7
                        
                        for dot in self.frozen_dots:
                            if random.random() > 0.7:  # Only keep some dots for a sparser effect
                                # More pronounced floating
                                float_speed = dot['speed'] * progress * 5.0
                                new_y = dot['y'] - float_speed * 0.15
                                
                                # More pronounced drift
                                t = self.settings.frame_count * 0.05
                                drift = 0.3 * np.sin(t + dot['offset']) * progress
                                new_x = dot['x'] + drift
                                
                                # Convert to integer coordinates
                                int_x = int(new_x)
                                int_y = int(new_y)
                                
                                # Check if the new position is valid and draw the dot
                                if (0 <= int_x < self.settings.dots_x and 
                                    0 <= int_y < self.settings.dots_y):
                                    
                                    # Apply fading effect
                                    intensity = dot['intensity'] * 0.3 * fade_factor
                                    
                                    # Skip if too faint
                                    if intensity < 0.05:
                                        continue
                                    
                                    # Calculate dot position
                                    pos_x, pos_y = self.settings.get_dot_position(int_x, int_y)
                                    
                                    # Calculate color (processing color with fading)
                                    base_color = self.settings.colors["processing"]
                                    r = max(0, min(255, int(base_color[0] * intensity)))
                                    g = max(0, min(255, int(base_color[1] * intensity)))
                                    b = max(0, min(255, int(base_color[2] * intensity)))
                                    color = (r, g, b)
                                    
                                    # Calculate dot size
                                    dot_size = int(self.settings.dot_size * (0.8 + 0.4 * intensity))
                                    
                                    # Draw the dot
                                    pygame.draw.circle(dot_surface, color, (pos_x, pos_y), dot_size)
                        
                        # Blend the dot surface on top
                        blended_surface.blit(dot_surface, (0, 0))
                    
                    return blended_surface
            
            # Simple crossfade for other transitions
            else:
                # Blend the two surfaces with alpha
                blended_surface.blit(prev_surface, (0, 0))
                target_surface.set_alpha(int(255 * progress))
                blended_surface.blit(target_surface, (0, 0))
                target_surface.set_alpha(255)  # Reset alpha
                
                return blended_surface
        
        # No transition active, return the target surface
        return target_surface
    
    def update(self):
        """Update the current animation and handle transitions"""
        # Increment the frame counter
        self.settings.increment_frame()
        
        # Update the demo sequence if active
        if self.demo_active:
            self.update_demo_sequence()
        
        # Get the target animation matrix and surface
        target_matrix = None
        target_surface = None
        
        if self.current_animation == "speaking":
            # Update simulated audio features
            self.update_simulated_audio()
            # Update the speaking animation
            target_surface = self.speaking_animation.update()
            target_matrix = self.speaking_animation.matrix
        elif self.current_animation == "listening":
            # Update the listening animation
            target_surface = self.listening_animation.update()
            target_matrix = self.listening_animation.matrix
        elif self.current_animation == "processing":
            # Update the processing animation
            target_surface = self.processing_animation.update()
            target_matrix = self.processing_animation.matrix
        
        # Apply transition effects if needed
        if self.transition.is_active() and self.previous_animation:
            # Get the previous animation matrix
            prev_matrix = None
            if self.previous_animation == "speaking":
                prev_matrix = self.speaking_animation.matrix
            elif self.previous_animation == "listening":
                prev_matrix = self.listening_animation.matrix
            elif self.previous_animation == "processing":
                prev_matrix = self.processing_animation.matrix
            
            # Apply matrix-level transition
            if prev_matrix is not None and target_matrix is not None:
                blended_matrix = self.transition.apply_transition(prev_matrix, target_matrix)
                
                # Apply the blended matrix to the current animation
                if self.current_animation == "speaking":
                    self.speaking_animation.matrix = blended_matrix
                elif self.current_animation == "listening":
                    self.listening_animation.matrix = blended_matrix
                elif self.current_animation == "processing":
                    self.processing_animation.matrix = blended_matrix
                
                # Redraw the current animation with the blended matrix
                if self.current_animation == "speaking":
                    target_surface = self.speaking_animation.draw()
                elif self.current_animation == "listening":
                    target_surface = self.listening_animation.draw()
                elif self.current_animation == "processing":
                    target_surface = self.processing_animation.draw()
            
            # Apply surface-level transition effects
            return self._apply_transition_effects(target_surface)
        
        # For processing to speaking transition, use the special transition
        elif self.processing_to_speaking_active and self.current_animation == "speaking":
            return self._apply_transition_effects(target_surface)
        
        return target_surface
    
    def draw(self):
        """Draw the GUI"""
        # Clear the screen
        self.screen.fill((30, 30, 40))
        
        # Draw the current animation
        animation_surface = self.update()
        if animation_surface:
            self.screen.blit(animation_surface, (self.animation_x, self.animation_y))
        
        # Draw the sidebar
        pygame.draw.rect(self.screen, (50, 50, 60), 
                         pygame.Rect(self.width - 200, 0, 200, self.height))
        
        # Draw the title
        title_text = self.title_font.render("Animation Test", True, (255, 255, 255))
        self.screen.blit(title_text, (self.width - 190, 15))
        
        # Draw the buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Check if mouse is over button
            if button["rect"].collidepoint(mouse_pos):
                color = button["hover_color"]
            else:
                color = button["color"]
            
            # Highlight the current animation button or demo button if active
            if (button["action"] == self.current_animation or 
                (button["action"] == "demo" and self.demo_active)):
                # Draw a highlight border
                pygame.draw.rect(self.screen, (255, 255, 255), 
                                button["rect"].inflate(4, 4))
            
            # Draw the button
            pygame.draw.rect(self.screen, color, button["rect"])
            
            # Draw the button text
            text = self.font.render(button["text"], True, button["text_color"])
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # Draw the current animation name and transition status
        status_text = ""
        if self.processing_to_speaking_active:
            frames_since = self.settings.frame_count - self.processing_to_speaking_start_frame
            progress = min(100, int(frames_since / self.processing_to_speaking_duration * 100))
            status_text = f"Transition: processing → speaking ({progress}%)"
        elif self.transition.is_active():
            progress = int(self.transition.get_progress() * 100)
            status_text = f"Transition: {self.previous_animation} → {self.current_animation} ({progress}%)"
        else:
            if self.current_animation == "speaking":
                status_text = "Current: AI Speaking"
            elif self.current_animation == "listening":
                status_text = "Current: Listening"
            elif self.current_animation == "processing":
                status_text = "Current: Processing"
        
        status_render = self.font.render(status_text, True, (255, 255, 255))
        self.screen.blit(status_render, (self.width - 190, self.height - 50))
        
        # If demo is active, show the remaining time
        if self.demo_active:
            current_step = self.demo_sequence[self.demo_current_step]
            time_elapsed = time.time() - self.demo_step_start_time
            time_remaining = max(0, current_step["duration"] - time_elapsed)
            demo_text = f"Demo: {current_step['state']} ({time_remaining:.1f}s remaining)"
            demo_render = self.font.render(demo_text, True, (255, 255, 255))
            self.screen.blit(demo_render, (self.width - 190, self.height - 80))
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Run the GUI main loop"""
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Draw the GUI
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(30)
        
        # Clean up
        pygame.quit()
        sys.exit()

# Run the GUI if this file is executed directly
if __name__ == "__main__":
    gui = GUIManager(800, 600)
    gui.run()