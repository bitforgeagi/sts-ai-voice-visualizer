# Example integration in another application
import pygame
import numpy as np
import time
import random
from enum import Enum
from voice_widget import VoiceWidget, AnimationState

class VoiceWidgetExample:
    """
    Example application showing the VoiceWidget with a banner and centered animation.
    """
    
    def __init__(self, width=800, height=600):
        """
        Initialize the example application.
        
        Args:
            width (int): Width of the window
            height (int): Height of the window
        """
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Create a window
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Voice Widget Example")
        
        # Set up fonts
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 18)
        
        # Create the voice widget (sized appropriately)
        self.widget_size = min(width, height - 100) - 40  # Leave space for banner
        self.voice_widget = VoiceWidget(self.widget_size, self.widget_size)
        
        # Banner settings
        self.banner_height = 80
        self.banner_color = (40, 40, 50)
        self.banner_highlight = (60, 60, 80)
        
        # Button settings
        self.buttons = [
            {
                "text": "Listening",
                "state": AnimationState.LISTENING,
                "color": (220, 220, 220),
                "text_color": (20, 20, 20),
                "rect": None  # Will be calculated in resize
            },
            {
                "text": "Processing",
                "state": AnimationState.PROCESSING,
                "color": (180, 200, 240),
                "text_color": (20, 20, 20),
                "rect": None
            },
            {
                "text": "Speaking",
                "state": AnimationState.SPEAKING,
                "color": (60, 180, 255),
                "text_color": (20, 20, 20),
                "rect": None
            },
            {
                "text": "Idle",
                "state": AnimationState.IDLE,
                "color": (80, 80, 100),
                "text_color": (220, 220, 220),
                "rect": None
            }
        ]
        
        # Calculate button positions
        self._calculate_button_positions()
        
        # Set up a clock for controlling the frame rate
        self.clock = pygame.time.Clock()
        
        # Demo mode
        self.demo_active = False
        self.demo_sequence = [
            {"state": AnimationState.LISTENING, "duration": 3.0},
            {"state": AnimationState.PROCESSING, "duration": 3.0},
            {"state": AnimationState.SPEAKING, "duration": 5.0},
            {"state": AnimationState.LISTENING, "duration": 3.0}
        ]
        self.demo_current_step = 0
        self.demo_step_start_time = 0
        
        # Demo button
        self.demo_button = {
            "text": "Run Demo",
            "color": (100, 180, 100),
            "text_color": (255, 255, 255),
            "rect": None  # Will be calculated in resize
        }
        self._calculate_demo_button_position()
    
    def _calculate_button_positions(self):
        """Calculate the positions of the buttons in the banner"""
        button_width = 120
        button_height = 40
        button_spacing = 20
        total_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * button_spacing
        start_x = (self.width - total_width) // 2
        
        for i, button in enumerate(self.buttons):
            x = start_x + i * (button_width + button_spacing)
            y = self.height - self.banner_height + (self.banner_height - button_height) // 2
            button["rect"] = pygame.Rect(x, y, button_width, button_height)
    
    def _calculate_demo_button_position(self):
        """Calculate the position of the demo button"""
        button_width = 120
        button_height = 40
        x = self.width - button_width - 20
        y = self.height - self.banner_height + (self.banner_height - button_height) // 2
        self.demo_button["rect"] = pygame.Rect(x, y, button_width, button_height)
    
    def resize(self, width, height):
        """Handle window resize"""
        self.width = width
        self.height = height
        
        # Resize the widget
        self.widget_size = min(width, height - 100) - 40
        self.voice_widget.resize(self.widget_size, self.widget_size)
        
        # Recalculate button positions
        self._calculate_button_positions()
        self._calculate_demo_button_position()
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resize
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.resize(event.w, event.h)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any button was clicked
                mouse_pos = pygame.mouse.get_pos()
                
                # State buttons
                for button in self.buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        self.voice_widget.set_state(button["state"])
                        self.demo_active = False
                        break
                
                # Demo button
                if self.demo_button["rect"].collidepoint(mouse_pos):
                    self.start_demo()
            
            elif event.type == pygame.KEYDOWN:
                # Keyboard shortcuts
                if event.key == pygame.K_1:
                    self.voice_widget.set_state(AnimationState.LISTENING)
                    self.demo_active = False
                elif event.key == pygame.K_2:
                    self.voice_widget.set_state(AnimationState.PROCESSING)
                    self.demo_active = False
                elif event.key == pygame.K_3:
                    self.voice_widget.set_state(AnimationState.SPEAKING)
                    self.demo_active = False
                elif event.key == pygame.K_0:
                    self.voice_widget.set_state(AnimationState.IDLE)
                    self.demo_active = False
                elif event.key == pygame.K_d:
                    self.start_demo()
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        return True
    
    def start_demo(self):
        """Start the demo sequence"""
        self.demo_active = True
        self.demo_current_step = 0
        self.demo_step_start_time = time.time()
        self.voice_widget.set_state(self.demo_sequence[0]["state"])
    
    def update_demo(self):
        """Update the demo sequence if active"""
        if not self.demo_active:
            return
        
        current_time = time.time()
        current_step = self.demo_sequence[self.demo_current_step]
        
        if current_time - self.demo_step_start_time > current_step["duration"]:
            # Move to the next step
            self.demo_current_step = (self.demo_current_step + 1) % len(self.demo_sequence)
            self.demo_step_start_time = current_time
            
            # Change to the next state
            next_step = self.demo_sequence[self.demo_current_step]
            self.voice_widget.set_state(next_step["state"])
    
    def update(self):
        """Update the application state"""
        # Update the demo if active
        if self.demo_active:
            self.update_demo()
        
        # Update the voice widget
        self.voice_widget.update()
    
    def draw(self):
        """Draw the application UI"""
        # Clear the screen with a dark background
        self.screen.fill((30, 30, 40))
        
        # Draw the voice widget centered
        widget_x = (self.width - self.widget_size) // 2
        widget_y = (self.height - self.banner_height - self.widget_size) // 2
        self.screen.blit(self.voice_widget.get_surface(), (widget_x, widget_y))
        
        # Draw the banner background
        pygame.draw.rect(self.screen, self.banner_color, 
                         (0, self.height - self.banner_height, self.width, self.banner_height))
        
        # Draw a subtle highlight at the top of the banner
        pygame.draw.line(self.screen, self.banner_highlight, 
                         (0, self.height - self.banner_height), 
                         (self.width, self.height - self.banner_height), 2)
        
        # Draw the buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            # Check if this is the current state or mouse is over
            is_current = self.voice_widget.current_state == button["state"]
            is_hover = button["rect"].collidepoint(mouse_pos)
            
            # Draw button background with highlight if current or hover
            if is_current:
                # Draw a highlight border for the current state
                pygame.draw.rect(self.screen, (255, 255, 255), 
                                button["rect"].inflate(4, 4))
            
            # Draw the button with slightly lighter color if hovered
            button_color = button["color"]
            if is_hover and not is_current:
                # Lighten the color for hover effect
                button_color = tuple(min(255, c + 20) for c in button_color)
            
            pygame.draw.rect(self.screen, button_color, button["rect"])
            
            # Draw the button text
            text = self.info_font.render(button["text"], True, button["text_color"])
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # Draw the demo button
        is_hover = self.demo_button["rect"].collidepoint(mouse_pos)
        button_color = self.demo_button["color"]
        
        # Change text and color if demo is active
        button_text = "Stop Demo" if self.demo_active else "Run Demo"
        
        if self.demo_active:
            # Use a different color for active demo
            button_color = (180, 100, 100)
        elif is_hover:
            # Lighten the color for hover effect
            button_color = tuple(min(255, c + 20) for c in button_color)
        
        pygame.draw.rect(self.screen, button_color, self.demo_button["rect"])
        
        # Draw the button text
        text = self.info_font.render(button_text, True, self.demo_button["text_color"])
        text_rect = text.get_rect(center=self.demo_button["rect"].center)
        self.screen.blit(text, text_rect)
        
        # Draw the title
        title_text = self.title_font.render("AI Voice Visualization", True, (255, 255, 255))
        self.screen.blit(title_text, (20, 20))
        
        # Draw the current state
        state_text = self.info_font.render(f"Current State: {self.voice_widget.current_state.name}", 
                                          True, (220, 220, 220))
        self.screen.blit(state_text, (20, 60))
        
        # Draw demo status if active
        if self.demo_active:
            current_step = self.demo_sequence[self.demo_current_step]
            time_elapsed = time.time() - self.demo_step_start_time
            time_remaining = max(0, current_step["duration"] - time_elapsed)
            
            demo_text = f"Demo: {current_step['state'].name} ({time_remaining:.1f}s remaining)"
            demo_render = self.info_font.render(demo_text, True, (220, 220, 220))
            self.screen.blit(demo_render, (20, 90))
        
        # Draw keyboard shortcuts help
        help_text = self.info_font.render("Press 0-3 for states, D for demo, ESC to quit", 
                                         True, (180, 180, 180))
        help_rect = help_text.get_rect(right=self.width - 20, bottom=self.height - self.banner_height - 20)
        self.screen.blit(help_text, help_rect)
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Run the application main loop"""
        running = True
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update()
            
            # Draw
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(30)
        
        # Clean up
        pygame.quit()

# Run the application if this file is executed directly
if __name__ == "__main__":
    example = VoiceWidgetExample(800, 600)
    example.run()