# src/controller.py
import collections
import math
import time

class FingerMotionController:
    """
    Motion-based controller:
    - keeps a short history of fingertip positions to compute dx/dy
    - returns one of ["UP","DOWN","LEFT","RIGHT"] based on dominant movement
    - includes a motion_threshold and simple smoothing
    """
    def __init__(self, motion_threshold=20, history_len=4):
        self.prev_x = None
        self.prev_y = None
        self.last_direction = "RIGHT"
        self.motion_threshold = motion_threshold
        self.history = collections.deque(maxlen=history_len)  # store (x,y,t)
        self.last_update = time.time()

    def get_direction(self, fingertip):
        """
        fingertip: (x,y) pixel coords or None
        returns direction string (and updates internal state)
        """
        if fingertip is None:
            return self.last_direction

        x, y = fingertip
        now = time.time()

        # initialize
        if not self.history:
            self.history.append((x, y, now))
            return self.last_direction

        # append and compute velocity over last and current
        self.history.append((x, y, now))

        # compute average dx, dy over history (end - start) / dt
        if len(self.history) >= 2:
            x0, y0, t0 = self.history[0]
            x1, y1, t1 = self.history[-1]
            dt = t1 - t0 if (t1 - t0) != 0 else 1e-6
            dx = (x1 - x0) / dt
            dy = (y1 - y0) / dt
        else:
            dx = dy = 0.0

        # choose dominant axis
        if abs(dx) < self.motion_threshold and abs(dy) < self.motion_threshold:
            # not enough movement -> keep last
            return self.last_direction

        if abs(dx) > abs(dy):
            direction = "RIGHT" if dx > 0 else "LEFT"
        else:
            direction = "DOWN" if dy > 0 else "UP"

        # prevent reversal to opposite direction directly — logic kept in game via change_direction
        self.last_direction = direction
        return direction
