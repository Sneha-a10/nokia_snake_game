# src/finger_tracking.py
import cv2
import mediapipe as mp

class FingerTracker:
    """
    Lightweight wrapper around Mediapipe Hands.
    get_index_finger(frame) -> (frame_with_drawings, (x,y) or None, hand_landmarks or None)
    Coordinates returned are pixel coordinates in the frame (BGR).
    """
    def __init__(self, max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_index_finger(self, frame, draw=True):
        """
        Process the frame, return (frame, fingertip_xy, hand_landmarks)
        fingertip_xy is (x, y) in pixel coords or None if not found.
        hand_landmarks is the mediapipe landmark object (or None).
        """
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        fingertip = None
        hand_landmarks = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            lm = hand_landmarks.landmark[8]  # index fingertip
            cx, cy = int(lm.x * w), int(lm.y * h)
            fingertip = (cx, cy)

            if draw:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

        return frame, fingertip, hand_landmarks

    def draw_hands(self, frame, hand_landmarks):
        """
        Draw hand landmarks on the frame.
        """
        if hand_landmarks:
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            # Draw the index finger tip specifically as well if needed, or just rely on landmarks
            h, w, _ = frame.shape
            lm = hand_landmarks.landmark[8]
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
        return frame
