# src/snake_game.py
import random

class SnakeGame:
    """
    Classic grid-based snake engine.
    - grid coordinates: (x,y) with (0,0) top-left
    - snake: list of (x,y) with head at index 0
    - walls: hit wall -> game_over True
    """
    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.reset()

    def reset(self):
        mid = self.grid_size // 2
        self.snake = [(mid, mid)]
        self.direction = "RIGHT"
        self.last_moved_direction = "RIGHT"
        self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            f = (random.randint(0, self.grid_size - 1),
                 random.randint(0, self.grid_size - 1))
            if f not in self.snake:
                self.food = f
                break

    def change_direction(self, new_dir):
        # prevent reversing onto itself immediately
        # Check against the direction we LAST MOVED, not the current buffer
        opposite = {"UP":"DOWN","DOWN":"UP","LEFT":"RIGHT","RIGHT":"LEFT"}
        if new_dir != opposite.get(self.last_moved_direction, ""):
            self.direction = new_dir

    def step(self):
        if self.game_over:
            return

        # Update last_moved_direction to what we are about to execute
        self.last_moved_direction = self.direction

        head_x, head_y = self.snake[0]
        if self.direction == "UP":
            head_y -= 1
        elif self.direction == "DOWN":
            head_y += 1
        elif self.direction == "LEFT":
            head_x -= 1
        elif self.direction == "RIGHT":
            head_x += 1

        new_head = (head_x, head_y)

        # wall collision
        if not (0 <= head_x < self.grid_size and 0 <= head_y < self.grid_size):
            self.game_over = True
            return

        # self collision
        if new_head in self.snake:
            # Special case: if we are just chasing our tail (which will move), it's safe
            # But in this simple implementation, we check current snake body.
            # If we don't eat, tail moves. If new_head == tail, it's safe.
            if new_head != self.snake[-1]: 
                self.game_over = True
                return
            # If we ate food, we grow, so tail doesn't move. Then it IS a collision.
            # But we handle growth after this check.
            # Actually, standard logic:
            # If new_head == food: tail stays. Collision check should include tail.
            # If new_head != food: tail moves. Collision check should EXCLUDE tail.
            
            # Let's refine self-collision logic:
            if new_head == self.food:
                 # We will grow, so tail stays. Collision with tail is fatal.
                 self.game_over = True
                 return
            else:
                 # We will pop tail. Collision with tail is safe.
                 if new_head != self.snake[-1]:
                     self.game_over = True
                     return

        # move
        self.snake.insert(0, new_head)

        # food?
        if new_head == self.food:
            self.score += 10
            self.spawn_food()
        else:
            self.snake.pop()
