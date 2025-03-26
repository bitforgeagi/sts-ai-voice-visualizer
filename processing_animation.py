import numpy as np
import pygame
import random
import time
from animation_settings import AnimationSettings

class ProcessingAnimation:
    """
    Animation for visualizing AI processing state with thoughtful concentric rings
    that flow inward with smooth fading effects.
    """
    
    def __init__(self, width=600, height=600):
        """
        Initialize the processing animation.
        
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
        
        # Color for processing (light blue)
        self.color = self.settings.colors["processing"]
    
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
        
        # Update the matrix with processing animation
        self._update_processing_matrix(matrix)
        
        # Update the animation matrix
        self.matrix = matrix
        
        # Draw the frame
        self.draw()
        
        return self.surface
    
    def _update_processing_matrix(self, matrix):
        """Update matrix based on the processing state animation pattern"""
        # Get time for animation
        t = self.frame_count * self.animation_speed
        
        # First, clear the matrix
        matrix.fill(0)
        
        # Create a subtle ambient glow
        for y in range(self.dots_y):
            for x in range(self.dots_x):
                if not self.dot_mask[y, x]:
                    continue
                
                # Get normalized position using settings
                nx, ny, dist = self.settings.get_normalized_position(x, y)
                
                if dist > 1.0:
                    continue
                
                # Create a subtle ambient glow that fades with distance
                ambient_glow = 0.15 * (1.0 - dist**1.5)
                
                # Add subtle pulsing
                ambient_glow *= 0.9 + 0.1 * np.sin(t * 1.2)
                
                # Apply to matrix
                matrix[y, x] = ambient_glow
        
        # Create thoughtful concentric rings that flow inward
        ring_count = 6
        for i in range(ring_count):
            # Calculate ring radius - moves from outside to center
            phase = ((t * 0.4) + i / ring_count) % 1.0
            radius = 1.0 - phase
            
            # Ring width gets narrower as it approaches the center
            width = 0.05 + 0.02 * phase
            
            # Ring intensity increases as it approaches the center
            outer_fade = min(1.0, phase * 5.0)
            inner_fade = min(1.0, (1.0 - phase) * 5.0)
            intensity = 0.4 + 0.3 * (1.0 - phase)
            intensity *= outer_fade * inner_fade
            
            # Apply the ring with smoother gradient
            for y in range(self.dots_y):
                for x in range(self.dots_x):
                    if not self.dot_mask[y, x]:
                        continue
                    
                    # Get normalized position using settings
                    nx, ny, dist = self.settings.get_normalized_position(x, y)
                    
                    # Check if point is on the ring with smoother falloff
                    dist_from_ring = abs(dist - radius)
                    if dist_from_ring < width * 1.5:
                        # Calculate intensity with smoother falloff
                        falloff = dist_from_ring / (width * 1.5)
                        point_intensity = intensity * (1.0 - falloff**2)
                        
                        # Add subtle variation based on angle for more organic feel
                        angle = np.arctan2(ny, nx)
                        angle_variation = 0.05 * np.sin(angle * 4 + t * 1.5)
                        point_intensity *= (1.0 + angle_variation)
                        
                        # Apply to matrix
                        matrix[y, x] = max(matrix[y, x], point_intensity)
                        
                        # Color transition information
                        if point_intensity > 0.3:
                            blue_factor = 1.0 - radius
                            white_blend = 1.0 + (1.0 - blue_factor) * 0.8
                            if white_blend > 1.0 and point_intensity > matrix[y, x]:
                                matrix[y, x] = min(1.8, point_intensity * white_blend)
        
        # Add a calm, pulsing center
        center_radius = 0.2 + 0.05 * np.sin(t * 1.5)
        for y in range(self.dots_y):
            for x in range(self.dots_x):
                if not self.dot_mask[y, x]:
                    continue
                
                # Get normalized position using settings
                nx, ny, dist = self.settings.get_normalized_position(x, y)
                
                # Create a calm glowing core
                if dist < center_radius:
                    core_intensity = (1.0 - (dist/center_radius)**2.0)
                    pulse_factor = 0.9 + 0.1 * np.sin(t * 2.0)
                    core_intensity *= pulse_factor
                    matrix[y, x] = max(matrix[y, x], core_intensity)
                    
                    # Make the very center slightly blue-tinted
                    if dist < center_radius * 0.5:
                        blue_factor = 1.0 - dist/(center_radius * 0.5)
                        matrix[y, x] = max(matrix[y, x], core_intensity * (1.0 - blue_factor * 0.2))
        
        # Add a few subtle "thought particles"
        particle_count = 25
        for i in range(particle_count):
            # Random angle
            angle = random.random() * 2 * np.pi
            
            # Random distance from center
            dist = 0.2 + 0.8 * random.random()
            
            # Calculate position
            nx = np.cos(angle) * dist
            ny = np.sin(angle) * dist
            
            # Add gentle movement toward center
            movement_speed = 0.15 * (1.0 - np.cos(t * 1.5 + i * 0.7))
            nx = nx * (1.0 - movement_speed)
            ny = ny * (1.0 - movement_speed)
            
            # Convert to matrix coordinates using settings
            x = int((nx * self.radius + self.center_x) / self.dot_spacing)
            y = int((ny * self.radius + self.center_y) / self.dot_spacing)
            
            # Check if coordinates are valid
            if (0 <= x < self.dots_x and 
                0 <= y < self.dots_y and 
                self.dot_mask[y, x]):
                
                # Particle intensity
                intensity = 0.4 + 0.2 * random.random()
                
                # Apply to matrix
                matrix[y, x] = max(matrix[y, x], intensity)
        
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
    pygame.display.set_caption("Processing Animation")
    
    # Create the animation
    animation = ProcessingAnimation(600, 600)
    
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
