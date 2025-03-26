import numpy as np
import random

class AnimationTransition:
    """
    Handles smooth transitions between different animation states.
    """
    
    def __init__(self, settings):
        """
        Initialize the transition handler.
        
        Args:
            settings (AnimationSettings): The animation settings
        """
        self.settings = settings
        
        # Transition state
        self.active = False
        self.start_frame = 0
        self.duration = 30  # frames (about 1 second at 30 FPS)
        self.from_state = None
        self.to_state = None
        
        # Frozen state for transitions
        self.frozen_matrix = None
        self.frozen_dots = []
    
    def start_transition(self, from_state, to_state, duration=30):
        """
        Start a transition between animation states.
        
        Args:
            from_state (str): The state to transition from
            to_state (str): The state to transition to
            duration (int): Duration of the transition in frames
        """
        self.active = True
        self.start_frame = self.settings.frame_count
        self.duration = duration
        self.from_state = from_state
        self.to_state = to_state
    
    def is_active(self):
        """Check if a transition is currently active"""
        return self.active
    
    def get_progress(self):
        """
        Get the current transition progress.
        
        Returns:
            float: Progress from 0.0 to 1.0
        """
        if not self.active:
            return 1.0
        
        frames_since_start = self.settings.frame_count - self.start_frame
        progress = min(1.0, frames_since_start / self.duration)
        
        # If transition is complete, deactivate it
        if progress >= 1.0:
            self.active = False
        
        return progress
    
    def freeze_matrix(self, matrix):
        """
        Freeze the current matrix state for transition effects.
        
        Args:
            matrix (numpy.ndarray): The current animation matrix
        """
        # Store a copy of the current matrix
        self.frozen_matrix = matrix.copy()
        
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
    
    def apply_transition(self, current_matrix, target_matrix):
        """
        Apply transition effects between matrices.
        
        Args:
            current_matrix (numpy.ndarray): The current animation matrix
            target_matrix (numpy.ndarray): The target animation matrix
            
        Returns:
            numpy.ndarray: The blended matrix
        """
        if not self.active:
            return target_matrix
        
        # Get transition progress
        progress = self.get_progress()
        
        # Create a result matrix
        result_matrix = np.zeros_like(current_matrix)
        
        # Apply different transition effects based on the states
        if self.from_state == "speaking" and self.to_state == "listening":
            # Blue matrix dots gracefully transform to white listening state
            self._apply_speaking_to_listening_transition(result_matrix, current_matrix, target_matrix, progress)
        
        elif self.from_state == "listening" and self.to_state == "processing":
            # White dots float upward and turn light blue
            self._apply_listening_to_processing_transition(result_matrix, current_matrix, target_matrix, progress)
        
        elif self.from_state == "processing" and self.to_state == "speaking":
            # Light blue rings transform into blue matrix
            self._apply_processing_to_speaking_transition(result_matrix, current_matrix, target_matrix, progress)
        
        else:
            # Default crossfade transition
            self._apply_crossfade_transition(result_matrix, current_matrix, target_matrix, progress)
        
        return result_matrix
    
    def _apply_speaking_to_listening_transition(self, result_matrix, current_matrix, target_matrix, progress):
        """Apply transition from speaking to listening state"""
        # Instead of a full-screen fade, we'll transform the blue dots directly to white
        
        # Create a mask of active dots from the speaking animation
        active_dots = current_matrix > 0.2
        
        # For active dots, transition from blue to white
        if progress < 0.6:
            # Keep the blue matrix pattern but gradually change color (handled in rendering)
            # Just slightly reduce intensity to prepare for pattern change
            fade_factor = 1.0 - (progress / 0.6) * 0.3  # Fade to 70% intensity
            result_matrix[active_dots] = current_matrix[active_dots] * fade_factor
        
        # Middle to final phase: blend the pattern from speaking to listening
        else:
            # Calculate blend factor for the final transition
            blend_factor = (progress - 0.6) / 0.4  # 0 at 0.6, 1.0 at 1.0
            
            # Apply crossfade only to areas with active dots in either animation
            combined_active = np.logical_or(active_dots, target_matrix > 0.2)
            
            # For active areas, blend between the patterns
            result_matrix[combined_active] = (
                current_matrix[combined_active] * (1.0 - blend_factor) + 
                target_matrix[combined_active] * blend_factor
            )
            
            # For areas that are becoming active in the listening pattern but weren't in speaking,
            # fade them in more gradually to avoid sudden appearance
            new_active = np.logical_and(target_matrix > 0.2, ~active_dots)
            if np.any(new_active):
                # Apply a more gradual fade-in
                fade_in = blend_factor * blend_factor  # Quadratic ease-in
                result_matrix[new_active] = target_matrix[new_active] * fade_in
    
    def _apply_listening_to_processing_transition(self, result_matrix, current_matrix, target_matrix, progress):
        """Apply transition from listening to processing state"""
        # Early phase: white dots start to float and fade
        if progress < 0.4:
            # Keep the white dots but start subtle movement
            result_matrix[:] = current_matrix * (1.0 - progress * 0.5)
            
            # Apply floating effect to frozen dots
            if self.frozen_dots:
                for dot in self.frozen_dots:
                    # Calculate floating effect - dots move upward
                    float_speed = dot['speed'] * progress * 3.0
                    new_y = dot['y'] - float_speed * 0.1  # Move upward
                    
                    # Add some horizontal drift
                    drift = 0.2 * np.sin(self.settings.frame_count * 0.05 + dot['offset']) * progress
                    new_x = dot['x'] + drift
                    
                    # Convert to integer coordinates
                    int_x = int(new_x)
                    int_y = int(new_y)
                    
                    # Check if the new position is valid
                    if (0 <= int_x < self.settings.dots_x and 
                        0 <= int_y < self.settings.dots_y and
                        self.settings.dot_mask[int_y, int_x]):
                        
                        # Calculate fading effect
                        fade = 1.0 - progress * 0.5
                        intensity = dot['intensity'] * fade
                        
                        # Apply the effect
                        result_matrix[int_y, int_x] = max(result_matrix[int_y, int_x], intensity)
        
        # Middle to final phase: blend in the processing rings
        else:
            blend_factor = (progress - 0.4) / 0.6  # 0 at 0.4, 1.0 at 1.0
            result_matrix[:] = target_matrix * blend_factor
            
            # Add some residual floating dots that continue to fade
            if self.frozen_dots and progress < 0.7:
                fade_factor = 1.0 - (progress - 0.4) / 0.3  # 1.0 at 0.4, 0.0 at 0.7
                for dot in self.frozen_dots:
                    if random.random() > 0.7:  # Only keep some dots for a sparser effect
                        # More pronounced floating
                        float_speed = dot['speed'] * progress * 5.0
                        new_y = dot['y'] - float_speed * 0.15
                        
                        # More pronounced drift
                        drift = 0.3 * np.sin(self.settings.frame_count * 0.05 + dot['offset']) * progress
                        new_x = dot['x'] + drift
                        
                        # Convert to integer coordinates
                        int_x = int(new_x)
                        int_y = int(new_y)
                        
                        # Check if the new position is valid
                        if (0 <= int_x < self.settings.dots_x and 
                            0 <= int_y < self.settings.dots_y and
                            self.settings.dot_mask[int_y, int_x]):
                            
                            # Apply fading effect
                            intensity = dot['intensity'] * 0.3 * fade_factor
                            result_matrix[int_y, int_x] = max(result_matrix[int_y, int_x], intensity)
    
    def _apply_processing_to_speaking_transition(self, result_matrix, current_matrix, target_matrix, progress):
        """Apply transition from processing to speaking state"""
        # Smooth transition from concentric rings to matrix pattern
        
        # Calculate easing function for smoother transition
        ease_factor = progress * (2 - progress)  # Quadratic ease-in-out
        
        # Blend the matrices
        for y in range(result_matrix.shape[0]):
            for x in range(result_matrix.shape[1]):
                if not self.settings.dot_mask[y, x]:
                    continue
                
                # Get normalized position and distance
                nx, ny, dist = self.settings.get_normalized_position(x, y)
                
                # Apply different blending based on distance from center
                if dist < 0.3:
                    # Center area transitions faster
                    center_blend = min(1.0, progress * 1.5)
                    result_matrix[y, x] = current_matrix[y, x] * (1.0 - center_blend) + target_matrix[y, x] * center_blend
                else:
                    # Outer area follows the ease factor
                    result_matrix[y, x] = current_matrix[y, x] * (1.0 - ease_factor) + target_matrix[y, x] * ease_factor
                
                # Add some "data bits" emerging as we transition to speaking
                if progress > 0.5 and random.random() > 0.97:
                    result_matrix[y, x] += random.random() * 0.2 * (progress - 0.5) * 2.0
    
    def _apply_crossfade_transition(self, result_matrix, current_matrix, target_matrix, progress):
        """Apply a simple crossfade transition between matrices"""
        # Simple linear blend
        result_matrix[:] = current_matrix * (1.0 - progress) + target_matrix * progress

# Example usage in animation classes:
"""
# In animation class initialization:
from animation_settings import AnimationSettings
from transitions import AnimationTransition

self.settings = AnimationSettings(width, height)
self.transition = AnimationTransition(self.settings)

# When changing states:
self.transition.freeze_matrix(self.matrix)
self.transition.start_transition(from_state="listening", to_state="processing")

# In update method:
target_matrix = self.create_target_animation_matrix()
if self.transition.is_active():
    self.matrix = self.transition.apply_transition(self.matrix, target_matrix)
else:
    self.matrix = target_matrix
"""
