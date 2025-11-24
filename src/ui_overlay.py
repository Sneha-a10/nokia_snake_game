# src/ui_overlay.py
import cv2

BTN_W, BTN_H = 160, 64
BTN_GAP = 20

class UIButtonEvents:
    NONE = 0
    RESTART = 1
    EXIT = 2

class UIOverlay:
    def __init__(self, ox=20, oy=20, cell_size=20):
        self.ox = ox
        self.oy = oy
        self.cell_size = cell_size
        self.mouse = {"x": None, "y": None, "clicked": False}
        self.restart_rect = None
        self.exit_rect = None

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse["x"], self.mouse["y"], self.mouse["clicked"] = x, y, True
        if event == cv2.EVENT_LBUTTONUP:
            self.mouse["clicked"] = False

    def draw_game_area(self, frame, grid_size):
        ox, oy = self.ox, self.oy
        cell = self.cell_size
        grid_w = grid_size * cell
        grid_h = grid_size * cell

        # darken area
        overlay = frame.copy()
        cv2.rectangle(overlay, (ox, oy), (ox + grid_w, oy + grid_h), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.35, frame, 0.65, 0)

        # border
        cv2.rectangle(frame, (ox, oy), (ox + grid_w, oy + grid_h), (255, 255, 0), 3) # Cyan border

        # grid lines
        for i in range(grid_size + 1):
            x = ox + i * cell
            cv2.line(frame, (x, oy), (x, oy + grid_h), (50, 50, 50), 1)
            y = oy + i * cell
            cv2.line(frame, (ox, y), (ox + grid_w, y), (50, 50, 50), 1)

        return frame

    def draw_header(self, frame, score=0, elapsed_time=0):
        # Draw a header bar
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, 70), (30, 30, 30), -1)
        
        # Title - Centered
        title = "NOKIA SNAKE"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.0
        thick = 2
        (tw, th), _ = cv2.getTextSize(title, font, scale, thick)
        cv2.putText(frame, title, (w//2 - tw//2, 45), font, scale, (0, 255, 255), thick)
        
        # Score - Right aligned
        score_text = f"Score: {score}"
        (sw, sh), _ = cv2.getTextSize(score_text, font, 0.8, 2)
        cv2.putText(frame, score_text, (w - sw - 20, 45), font, 0.8, (255, 255, 255), 2)
        
        # Timer - Left aligned
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_text = f"Time: {minutes:02}:{seconds:02}"
        cv2.putText(frame, timer_text, (20, 45), font, 0.8, (255, 255, 255), 2)
        
        return frame

    def draw_countdown(self, frame, remaining):
        h, w, _ = frame.shape
        text = f"Starting in: {remaining}s"
        # Center text below header or in header if space allows. 
        # Let's put it just below header or overlaying the board slightly but centered.
        # Actually, let's put it in the center of the screen for visibility
        cv2.putText(frame, text, (w//2 - 120, h//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        return frame

    def draw_game_over(self, frame, score=0):
        h, w, _ = frame.shape
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

        # Game Over Text
        text = "GAME OVER"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 2.0
        thick = 5
        (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
        cx, cy = w // 2, h // 2
        
        cv2.putText(frame, text, (cx - tw // 2, cy - 80), font, scale, (0, 0, 255), thick)

        # Final Score
        score_text = f"Final Score: {score}"
        (sw, sh), _ = cv2.getTextSize(score_text, font, 1.0, 2)
        cv2.putText(frame, score_text, (cx - sw // 2, cy - 20), font, 1.0, (255, 255, 0), 2)

        # Buttons centered below text
        btn_w, btn_h = 160, 60
        gap = 40
        total_w = 2 * btn_w + gap
        start_x = cx - total_w // 2
        btn_y = cy + 50

        self.restart_rect = (start_x, btn_y, start_x + btn_w, btn_y + btn_h)
        self.exit_rect = (start_x + btn_w + gap, btn_y, start_x + btn_w + gap + btn_w, btn_y + btn_h)

        # Draw Restart Button
        cv2.rectangle(frame, (self.restart_rect[0], self.restart_rect[1]),
                      (self.restart_rect[2], self.restart_rect[3]), (0, 200, 0), -1)
        cv2.putText(frame, "RESTART", (self.restart_rect[0] + 15, self.restart_rect[1] + 40),
                    font, 0.8, (255, 255, 255), 2)

        # Draw Exit Button
        cv2.rectangle(frame, (self.exit_rect[0], self.exit_rect[1]),
                      (self.exit_rect[2], self.exit_rect[3]), (0, 0, 200), -1)
        cv2.putText(frame, "EXIT", (self.exit_rect[0] + 45, self.exit_rect[1] + 40),
                    font, 0.8, (255, 255, 255), 2)

        return frame

    def check_button_click(self):
        if self.mouse["x"] is None:
            return UIButtonEvents.NONE

        mx, my = self.mouse["x"], self.mouse["y"]

        if self.restart_rect and \
           self.restart_rect[0] <= mx <= self.restart_rect[2] and \
           self.restart_rect[1] <= my <= self.restart_rect[3]:
            self.mouse["x"] = None
            return UIButtonEvents.RESTART

        if self.exit_rect and \
           self.exit_rect[0] <= mx <= self.exit_rect[2] and \
           self.exit_rect[1] <= my <= self.exit_rect[3]:
            self.mouse["x"] = None
            return UIButtonEvents.EXIT

        return UIButtonEvents.NONE

    def draw_status(self, frame, controller, game, paused, fps):
        ox, oy = self.ox, self.oy
        grid_h = game.grid_size * self.cell_size

        status_text = "PAUSED" if paused else ("PLAYING" if not game.game_over else "DEAD")
        status_col = (0, 0, 255) if paused else ((0, 200, 0) if not game.game_over else (0, 0, 200))

        cv2.putText(frame, f"Status: {status_text}", (ox + 10, oy + grid_h + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_col, 2)

        cv2.putText(frame, f"Dir: {controller.last_direction}",
                    (ox + 200, oy + grid_h + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 50, 50), 2)

        cv2.putText(frame, f"FPS: {fps}", (ox + 420, oy + grid_h + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.putText(frame, "Show OPEN PALM to pause", (ox + 10, oy + grid_h + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.putText(frame, "Click RESTART after death", (ox + 10, oy + grid_h + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        return frame
