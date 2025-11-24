# Finger Snake Game 🐍👆

A modern, computer-vision-powered twist on the classic Nokia Snake game! Control the snake using your index finger movements captured by your webcam.

## 🎮 Features

*   **Hand Gesture Control**: Navigate the snake simply by moving your index finger.
*   **Real-time Tracking**: Uses MediaPipe and OpenCV for smooth and responsive hand tracking.
*   **Classic Gameplay**: Eat food to grow longer and increase your score.
*   **Modern UI**:
    *   Clean, dark-themed interface with a cyan game board.
    *   Live Score and Timer display.
    *   Visual countdown on start and restart.
    *   Interactive "Game Over" screen with Restart and Exit buttons.
*   **Pause Functionality**: Show an **OPEN PALM** to pause the game instantly.

## 🛠️ Tech Stack

*   **Python 3.x**
*   **OpenCV** (`cv2`): For image processing and UI rendering.
*   **MediaPipe**: For robust hand and finger tracking.

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Sneha-a10/nokia_snake_game.git
    cd nokia_snake_game
    ```

2.  **Install dependencies**:
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```
    *If `requirements.txt` is missing, install manually:*
    ```bash
    pip install opencv-python mediapipe
    ```

## 🚀 How to Run

1.  Ensure your webcam is connected.
2.  Run the main script:
    ```bash
    python src/main.py
    ```

## 🕹️ Controls

*   **Move**: Move your **Index Finger** relative to the camera frame.
    *   Move Up/Down/Left/Right to change the snake's direction.
*   **Pause**: Show an **Open Palm** (all fingers extended) to pause the game. Close your hand or show just the index finger to resume.
*   **Quit**: Press `q` on your keyboard or click "EXIT" on the Game Over screen.

## 📂 Project Structure

*   `src/main.py`: The entry point of the game. Handles the main loop and integration.
*   `src/snake_game.py`: Contains the core game logic (snake movement, collision, scoring).
*   `src/finger_tracking.py`: Handles MediaPipe initialization and hand landmark detection.
*   `src/controller.py`: Interprets finger movements into directional commands.
*   `src/ui_overlay.py`: Manages all UI elements (drawing the board, score, timer, buttons).

## 📝 License

This project is open-source and available for educational purposes.
