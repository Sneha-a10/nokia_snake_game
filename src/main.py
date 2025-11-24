import cv2
import time
import mediapipe as mp

from finger_tracking import FingerTracker
from controller import FingerMotionController
from snake_game import SnakeGame
from ui_overlay import UIOverlay, UIButtonEvents

def run_countdown(cap, ui, window_name="Finger Snake"):
    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            return False
        frame = cv2.flip(frame, 1)
        remaining = 5 - int(time.time() - start_time)
        remaining = max(0, remaining)
        frame = ui.draw_header(frame)
        frame = ui.draw_countdown(frame, remaining)
        cv2.imshow(window_name, frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False
        if remaining == 0:
            return True

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not accessible.")
        return

    tracker = FingerTracker(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    controller = FingerMotionController()
    game = SnakeGame(grid_size=20)

    cell_size = 20
    oy = 80  # Increased offset to make room for header

    ui = UIOverlay(ox=20, oy=oy, cell_size=cell_size)
    cv2.namedWindow("Finger Snake", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Finger Snake", 800, 600)
    cv2.setMouseCallback("Finger Snake", ui.mouse_callback)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.55)

    # countdown
    if not run_countdown(cap, ui):
        cap.release()
        cv2.destroyAllWindows()
        return

    game_start_time = time.time()
    elapsed_time = 0

    last_step = time.time()
    step_interval = 0.14
    paused = False
    fps_t0 = time.time()
    frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # compute centered ox
        grid_w = game.grid_size * cell_size
        ox = max(10, (w - grid_w) // 2)
        ui.ox = ox

        # detect palm for pause
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        paused_local = False
        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            tips = [8, 12, 16, 20]
            pips = [6, 10, 14, 18]
            paused_local = True
            for tip, pip in zip(tips, pips):
                if hand.landmark[tip].y > hand.landmark[pip].y:
                    paused_local = False
                    break
            paused = paused_local

        # fingertip detection (on clean frame)
        frame, fingertip, hand_landmarks = tracker.get_index_finger(frame, draw=False)

        # Update timer
        if not game.game_over:
            elapsed_time = time.time() - game_start_time

        # draw UI background and board
        frame = ui.draw_header(frame, game.score, elapsed_time)
        frame = ui.draw_game_area(frame, game.grid_size)

        # update direction & game
        if not paused and not game.game_over:
            direction = controller.get_direction(fingertip)
            game.change_direction(direction)

        # step
        now = time.time()
        if not paused and not game.game_over and (now - last_step) > step_interval:
            game.step()
            last_step = now

        # redraw game area border for correct layering
        # frame = ui.draw_game_area(frame, game.grid_size) # We can skip full redraw, just border if needed, but let's keep it simple
        # Actually, we want the snake to be ON the board, and hands ON TOP of snake.
        # Current order: Board -> Snake -> Hands
        # But previously I did: Board -> Hands -> Snake (which covers hands) -> Board (covers snake?)
        # Let's do: Board -> Snake -> Hands
        
        # draw snake and food (using circles for prettier look)
        ox_local, oy_local = ui.ox, ui.oy
        for (x, y) in game.snake:
            # Draw circle for snake segment
            center = (ox_local + x * cell_size + cell_size // 2, oy_local + y * cell_size + cell_size // 2)
            cv2.circle(frame, center, cell_size // 2 - 1, (0, 255, 100), -1)

        fx, fy = game.food
        # Draw circle for food
        center = (ox_local + fx * cell_size + cell_size // 2, oy_local + fy * cell_size + cell_size // 2)
        cv2.circle(frame, center, cell_size // 2 - 2, (0, 100, 255), -1)

        # draw hands on top of everything
        frame = tracker.draw_hands(frame, hand_landmarks)

        # game-over UI
        if game.game_over:
            frame = ui.draw_game_over(frame, game.score)

            evt = ui.check_button_click()
            if evt == UIButtonEvents.RESTART:
                game.reset()
                controller = FingerMotionController()
                paused = False
                
                # Restart countdown
                if not run_countdown(cap, ui):
                    cap.release()
                    cv2.destroyAllWindows()
                    return

                game_start_time = time.time()
                elapsed_time = 0

                cv2.imshow("Finger Snake", frame)
                cv2.waitKey(1)
            elif evt == UIButtonEvents.EXIT:
                cap.release()
                cv2.destroyAllWindows()
                return

        # status + fps
        frames += 1
        if time.time() - fps_t0 >= 1.0:
            fps = int(frames / (time.time() - fps_t0))
            fps_t0 = time.time()
            frames = 0
        else:
            fps = "--"

        frame = ui.draw_status(frame, controller, game, paused, fps)

        cv2.imshow("Finger Snake", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
