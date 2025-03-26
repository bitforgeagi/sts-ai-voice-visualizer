import numpy as np
import pygame
import random
import time
from animation_settings import AnimationSettings

class ListeningAnimation:
    """
    Animation for visualizing the listening state with a dynamic white matrix-like effect
    that emphasizes radial waves and vertical data streams.
    """
    
    def __init__(self, width=600, height=600):
        """
        Initialize the listening animation.
        
        Args:
            width (int): Width of the animation window
            height (int): Height of the animation window
        """
        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()
        
        # Use shared animation settings
        self.settings = AnimationSettings(width, height)
        
        # Display settings
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Use settings for dot grid
        self.dot_size = self.settings.dot_size
        self.dot_spacing = self.settings.dot_spacing
        self.dots_x = self.settings.dots_x
        self.dots_y = self.settings.dots_y
        self.dot_mask = self.settings.dot_mask
        
        # Use settings for center and radius
        self.center_x = self.settings.center_x
        self.center_y = self.settings.center_y
        self.radius = self.settings.radius
        
        # Animation state
        self.matrix = np.zeros((self.dots_y, self.dots_x))
        self.prev_matrix = None
        self.frame_count = 0
        self.animation_speed = self.settings.animation_speed
        
        # Color for listening (white)
        self.color = self.settings.colors["listening"]
    
    def set_color(self, color):
        """Set the color of the animation"""
        self.color = color
    
    def resize(self, width, height):
        """Resize the animation surface"""
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Update settings
        self.settings.resize(width, height)
        
        # Update local references to settings
        self.dot_size = self.settings.dot_size
        self.dot_spacing = self.settings.dot_spacing
        self.dots_x = self.settings.dots_x
        self.dots_y = self.settings.dots_y
        self.dot_mask = self.settings.dot_mask
        self.center_x = self.settings.center_x
        self.center_y = self.settings.center_y
        self.radius = self.settings.radius
        
        # Reset the matrix
        self.matrix = np.zeros((self.dots_y, self.dots_x))
    
    def update(self):
        """Update the animation state for the next frame"""
        # Update frame counter
        self.frame_count = self.settings.increment_frame()
        
        # Create a new matrix
        matrix = np.zeros((self.dots_y, self.dots_x))
        
        # Update the matrix with listening animation
        self._update_listening_matrix(matrix)
        
        # Update the animation matrix
        self.matrix = matrix
        
        # Draw the frame
        self.draw()
        
        return self.surface
    
    def _update_listening_matrix(self, matrix):
        """Update matrix based on the listening state animation pattern"""
        # Get time for animation
        t = self.frame_count * self.animation_speed
        
        # First, clear the matrix
        matrix.fill(0)
        
        # Create a pattern that emphasizes radial waves and vertical data streams
        for y in range(self.dots_y):
            for x in range(self.dots_x):
                if not self.dot_mask[y, x]:
                    continue
                
                # Get normalized position using settings
                nx, ny, dist = self.settings.get_normalized_position(x, y)
                
                if dist > 1.0:
                    continue
                
                # Apply a soft edge fade near the boundary
                edge_fade = 1.0
                if dist > 0.75:
                    edge_fade = max(0.0, 1.0 - (dist - 0.75) / 0.25)
                    edge_fade = edge_fade ** 1.5
                
                # Vertical data streams
                stream_y = (ny * 0.5 + 0.5) * 10
                stream_phase = (stream_y + t * 1.2) % 3
                stream_intensity = 0.5 + 0.5 * np.sin(stream_phase * np.pi)
                
                # Horizontal bands
                freq_bands = 0.5 + 0.5 * np.sin(ny * 12 + t * 0.6)
                
                # Radial waves (stronger in listening mode)
                radial = 0.5 + 0.5 * np.sin(dist * 15 - t * 1.2)
                
                # Center pulse
                center_pulse = np.exp(-dist * 3) * (0.5 + 0.5 * np.sin(t * 2))
                
                # Combine with weights for listening state
                intensity = (
                    stream_intensity * 0.3 + 
                    freq_bands * 0.2 + 
                    radial * 0.4 +  # More emphasis on radial waves
                    center_pulse * 0.1
                ) * (1.0 - dist * 0.5)
                
                # Add random "data bits"
                if random.random() > 0.97:
                    intensity += random.random() * 0.2
                
                # Apply threshold with hysteresis
                if intensity > 0.35 or (matrix[y, x] > 0 and intensity > 0.2):
                    matrix[y, x] = min(1.0, intensity)
        
        # Apply temporal smoothing for less flickering
        if hasattr(self, 'prev_matrix') and self.prev_matrix is not None:
            # Check if matrices have the same shape
            if self.prev_matrix.shape == matrix.shape:
                # Blend with previous frame
                blend_factor = 0.4
                for y in range(min(matrix.shape[0], self.prev_matrix.shape[0])):
                    for x in range(min(matrix.shape[1], self.prev_matrix.shape[1])):
                        if matrix[y, x] > 0 or self.prev_matrix[y, x] > 0:
                            matrix[y, x] = matrix[y, x] * (1.0 - blend_factor) + self.prev_matrix[y, x] * blend_factor
        
        # Store current matrix for next frame
        self.prev_matrix = matrix.copy()
    
    def draw(self):
        """Draw the current animation frame to the surface"""
        # Clear the surface
        self.surface.fill((0, 0, 0))
        
        # Draw each dot based on the matrix intensity
        for y in range(self.dots_y):
            for x in range(self.dots_x):
                if not self.dot_mask[y, x]:
                    continue
                
                intensity = self.matrix[y, x]
                if intensity > 0:
                    # Get dot position using settings
                    pos_x, pos_y = self.settings.get_dot_position(x, y)
                    
                    # Calculate dot color based on intensity
                    # Ensure color values are valid integers between 0-255
                    if intensity > 1.0:
                        # White-hot effect for intensity > 1.0
                        white_factor = min(1.0, intensity - 1.0)
                        r = max(0, min(255, int(self.color[0] * (1.0 - white_factor) + 255 * white_factor)))
                        g = max(0, min(255, int(self.color[1] * (1.0 - white_factor) + 255 * white_factor)))
                        b = max(0, min(255, int(self.color[2] * (1.0 - white_factor) + 255 * white_factor)))
                    else:
                        # Normal color with intensity scaling
                        r = max(0, min(255, int(self.color[0] * intensity)))
                        g = max(0, min(255, int(self.color[1] * intensity)))
                        b = max(0, min(255, int(self.color[2] * intensity)))
                    
                    # Ensure we have valid integers for the color
                    dot_color = (int(r), int(g), int(b))
                    
                    # Calculate dot size based on intensity
                    dot_size = max(1, int(self.dot_size * (0.8 + 0.4 * intensity)))
                    
                    # Draw the dot
                    pygame.draw.circle(self.surface, dot_color, (pos_x, pos_y), dot_size)
        
        return self.surface

# Example usage
if __name__ == "__main__":
    # Initialize pygame
    pygame.init()
    
    # Create a window
    screen = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Listening Animation")
    
    # Create the animation
    animation = ListeningAnimation(600, 600)
    
    # Set up a clock for controlling the frame rate
    clock = pygame.time.Clock()
    
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
                animation.resize(event.w, event.h)
        
        # Update the animation
        animation_surface = animation.update()
        
        # Draw the animation to the screen
        screen.blit(animation_surface, (0, 0))
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(30)
    
    # Clean up
    pygame.quit()
