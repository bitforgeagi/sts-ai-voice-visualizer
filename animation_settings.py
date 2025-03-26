import numpy as np

class AnimationSettings:
    """
    Standardized settings for animations to ensure consistent dot layouts
    and smooth transitions between different animation states.
    """
    
    def __init__(self, width=600, height=600):
        """
        Initialize animation settings with default values.
        
        Args:
            width (int): Initial width of the animation
            height (int): Initial height of the animation
        """
        # Display settings
        self.width = width
        self.height = height
        
        # Dot grid settings - these will be calculated based on window size
        self._calculate_dot_settings()
        
        # Calculate center and radius
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2 - 20
        
        # Create a circular mask for the dots
        self.dot_mask = self._create_dot_mask()
        
        # Animation parameters
        self.animation_speed = 0.05
        self.frame_count = 0
        
        # Color settings
        self.colors = {
            "idle": (80, 80, 100),         # Soft blue-gray
            "listening": (220, 220, 220),  # White
            "recording": (220, 60, 60),    # Vibrant red
            "processing": (180, 200, 240), # Light blue
            "speaking": (60, 180, 255)     # Vibrant blue
        }
    
    def _calculate_dot_settings(self):
        """Calculate dot size and spacing based on window dimensions"""
        min_dimension = min(self.width, self.height)
        
        # Define size ranges with more granular scaling
        if min_dimension <= 300:  # Very small window
            self.dot_size = 1
            self.dot_spacing = 3
        elif min_dimension <= 500:  # Small window
            self.dot_size = 2
            self.dot_spacing = 6
        elif min_dimension <= 800:  # Medium window
            self.dot_size = 3
            self.dot_spacing = 9
        elif min_dimension <= 1200:  # Large window
            self.dot_size = 4
            self.dot_spacing = 12
        else:  # Extra large window
            self.dot_size = 5
            self.dot_spacing = 15
            
        # Calculate grid dimensions
        self.dots_x = self.width // self.dot_spacing
        self.dots_y = self.height // self.dot_spacing
    
    def _create_dot_mask(self):
        """Create a circular mask for the dots"""
        dot_mask = np.zeros((self.dots_y, self.dots_x), dtype=bool)
        for y in range(self.dots_y):
            for x in range(self.dots_x):
                nx = (x * self.dot_spacing - self.center_x) / self.radius
                ny = (y * self.dot_spacing - self.center_y) / self.radius
                dist = np.sqrt(nx*nx + ny*ny)
                dot_mask[y, x] = dist <= 1.0
        return dot_mask
    
    def resize(self, width, height):
        """
        Resize the animation settings.
        
        Args:
            width (int): New width of the animation
            height (int): New height of the animation
        """
        self.width = width
        self.height = height
        
        # Recalculate dot settings based on new dimensions
        self._calculate_dot_settings()
        
        # Recalculate center and radius
        self.center_x = width // 2
        self.center_y = height // 2
        self.radius = min(width, height) // 2 - 20
        
        # Recreate the circular mask
        self.dot_mask = self._create_dot_mask()
        
        # Return self to allow method chaining
        return self
    
    def get_normalized_position(self, x, y):
        """
        Get normalized position (-1 to 1) for a dot.
        
        Args:
            x (int): X coordinate in the dot grid
            y (int): Y coordinate in the dot grid
            
        Returns:
            tuple: (nx, ny, dist) normalized x, y coordinates and distance from center
        """
        nx = (x * self.dot_spacing - self.center_x) / self.radius
        ny = (y * self.dot_spacing - self.center_y) / self.radius
        dist = np.sqrt(nx*nx + ny*ny)
        return nx, ny, dist
    
    def get_dot_position(self, x, y):
        """
        Get the pixel position for a dot.
        
        Args:
            x (int): X coordinate in the dot grid
            y (int): Y coordinate in the dot grid
            
        Returns:
            tuple: (pos_x, pos_y) pixel coordinates
        """
        pos_x = x * self.dot_spacing
        pos_y = y * self.dot_spacing
        return pos_x, pos_y
    
    def create_empty_matrix(self):
        """Create an empty matrix for the animation"""
        return np.zeros((self.dots_y, self.dots_x))
    
    def get_color_for_state(self, state):
        """Get the color for a specific animation state"""
        return self.colors.get(state, self.colors["idle"])
    
    def increment_frame(self):
        """Increment the frame counter"""
        self.frame_count += 1
        return self.frame_count

    def get_animation_size_for_window(window_width, window_height, sidebar_width=200, padding=40):
        """
        Calculate the appropriate animation size for a given window size.
        
        Args:
            window_width (int): Width of the window
            window_height (int): Height of the window
            sidebar_width (int): Width of the sidebar
            padding (int): Padding around the animation
            
        Returns:
            tuple: (width, height) dimensions for the animation
        """
        available_width = window_width - sidebar_width - padding
        available_height = window_height - padding
        
        # Use the smaller dimension to ensure the animation fits
        animation_size = min(available_width, available_height)
        
        # Ensure minimum size
        animation_size = max(animation_size, 200)
        
        return animation_size, animation_size
