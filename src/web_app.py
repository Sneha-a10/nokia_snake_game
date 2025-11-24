import cv2
import av
import time
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode

# Import game modules
from snake_game import SnakeGame
from finger_tracking import FingerTracker
from controller import FingerMotionController
from ui_overlay import UIOverlay, UIButtonEvents

# --- Video Processor ---
class SnakeGameProcessor(VideoTransformerBase):
    def __init__(self):
        self.tracker = FingerTracker(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.controller = FingerMotionController(motion_threshold=20)
        self.game = SnakeGame(grid_size=20)
        self.ui = UIOverlay(ox=20, oy=80, cell_size=20)
        
        self.game_start_time = time.time()
        self.last_step = time.time()
        self.step_interval = 0.15
        
        # Hover state for buttons
        self.hover_start_time = None
        self.hover_button = None # 'RESTART' or 'EXIT'
        self.HOVER_DURATION = 1.5 # seconds to trigger click

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Flip for mirror effect (natural interaction)
        img = cv2.flip(img, 1)
        h, w, _ = img.shape
        
        # 1. Update UI offset based on screen size
        grid_w = self.game.grid_size * self.ui.cell_size
        ox = max(10, (w - grid_w) // 2)
        self.ui.ox = ox

        # 2. Finger Tracking (on clean frame)
        img, fingertip, hand_landmarks = self.tracker.get_index_finger(img, draw=False)

        # 3. Game Logic
        elapsed_time = 0
        if not self.game.game_over:
            elapsed_time = time.time() - self.game_start_time
            
            # Update direction
            direction = self.controller.get_direction(fingertip)
            self.game.change_direction(direction)
            
            # Step game
            now = time.time()
            if (now - self.last_step) > self.step_interval:
                self.game.step()
                self.last_step = now
        else:
            # Game Over Logic - Hover to Click
            if fingertip:
                fx, fy = fingertip
                # Check Restart
                if self.ui.restart_rect and \
                   self.ui.restart_rect[0] <= fx <= self.ui.restart_rect[2] and \
                   self.ui.restart_rect[1] <= fy <= self.ui.restart_rect[3]:
                    
                    if self.hover_button == 'RESTART':
                        if (time.time() - self.hover_start_time) > self.HOVER_DURATION:
                            # Trigger Restart
                            self.game.reset()
                            self.controller = FingerMotionController(motion_threshold=20)
                            self.game_start_time = time.time()
                            self.hover_button = None
                    else:
                        self.hover_button = 'RESTART'
                        self.hover_start_time = time.time()
                
                # Check Exit (Reset hover if not on button)
                elif self.ui.exit_rect and \
                     self.ui.exit_rect[0] <= fx <= self.ui.exit_rect[2] and \
                     self.ui.exit_rect[1] <= fy <= self.ui.exit_rect[3]:
                     pass # Exit not implemented for web (can't close browser tab easily)
                else:
                    self.hover_button = None
            else:
                self.hover_button = None

        # 4. Drawing
        # Header
        img = self.ui.draw_header(img, self.game.score, elapsed_time)
        
        # Board
        img = self.ui.draw_game_area(img, self.game.grid_size)
        
        # Snake & Food
        ox_local, oy_local = self.ui.ox, self.ui.oy
        cell_size = self.ui.cell_size
        
        for (x, y) in self.game.snake:
            center = (ox_local + x * cell_size + cell_size // 2, oy_local + y * cell_size + cell_size // 2)
            cv2.circle(img, center, cell_size // 2 - 1, (0, 255, 100), -1)

        fx, fy = self.game.food
        center = (ox_local + fx * cell_size + cell_size // 2, oy_local + fy * cell_size + cell_size // 2)
        cv2.circle(img, center, cell_size // 2 - 2, (0, 100, 255), -1)

        # Hands
        img = self.tracker.draw_hands(img, hand_landmarks)

        # Game Over UI
        if self.game.game_over:
            img = self.ui.draw_game_over(img, self.game.score)
            
            # Draw Hover Progress
            if self.hover_button == 'RESTART' and self.ui.restart_rect:
                # Draw a progress bar or indicator
                progress = min(1.0, (time.time() - self.hover_start_time) / self.HOVER_DURATION)
                rx, ry, rw, rh = self.ui.restart_rect
                # Draw filling rectangle
                fill_w = int((rw - rx) * progress)
                cv2.rectangle(img, (rx, ry + rh - 5), (rx + fill_w, ry + rh), (255, 255, 0), -1)
                
                cv2.putText(img, "HOVER TO RESTART", (rx, ry - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# --- Main App ---
st.set_page_config(page_title="Nokia Snake - Hand Control", layout="wide")

st.title("🐍 Nokia Snake - Hand Control")
st.markdown("""
**Instructions:**
1. Allow camera access.
2. Use your **Index Finger** to control the snake.
3. **Game Over?** Hover your finger over the **RESTART** button for 1.5 seconds.
""")

col1, col2 = st.columns([2, 1])

with col1:
    webrtc_streamer(
        key="snake-game",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=SnakeGameProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.subheader("📱 Play on Phone")
    st.write("To play on your phone:")
    st.write("1. Open this app's URL on your mobile browser.")
    st.write("2. Ensure you grant camera permissions.")
    st.write("3. Rotate your phone to landscape for the best experience.")
    
    st.info("Note: Hand tracking performance depends on your device's processing power.")
