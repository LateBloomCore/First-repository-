import random
import tkinter as tk


class Config:
    WIDTH = 800
    HEIGHT = 500
    FPS = 60
    PADDLE_WIDTH = 12
    PADDLE_HEIGHT = 90
    PADDLE_SPEED = 6
    BALL_RADIUS = 10
    BALL_SPEED_X = 5
    BALL_SPEED_Y = 4
    BOT_ENABLED = True
    BOT_MAX_SPEED = 4
    BOT_REACTION_FRAMES = 6
    BOT_TARGET_JITTER = 16


class PongGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PONG")
        self.root.geometry(f"{Config.WIDTH}x{Config.HEIGHT}")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(
            self.root,
            width=Config.WIDTH,
            height=Config.HEIGHT,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.left_paddle = self.canvas.create_rectangle(
            30,
            (Config.HEIGHT - Config.PADDLE_HEIGHT) / 2,
            30 + Config.PADDLE_WIDTH,
            (Config.HEIGHT + Config.PADDLE_HEIGHT) / 2,
            fill="white",
            outline="",
        )
        self.right_paddle = self.canvas.create_rectangle(
            Config.WIDTH - 30 - Config.PADDLE_WIDTH,
            (Config.HEIGHT - Config.PADDLE_HEIGHT) / 2,
            Config.WIDTH - 30,
            (Config.HEIGHT + Config.PADDLE_HEIGHT) / 2,
            fill="white",
            outline="",
        )
        self.ball = self.canvas.create_oval(
            Config.WIDTH / 2 - Config.BALL_RADIUS,
            Config.HEIGHT / 2 - Config.BALL_RADIUS,
            Config.WIDTH / 2 + Config.BALL_RADIUS,
            Config.HEIGHT / 2 + Config.BALL_RADIUS,
            fill="white",
            outline="",
        )

        self.ball_velocity = [Config.BALL_SPEED_X, Config.BALL_SPEED_Y]
        self.pressed_keys: set[str] = set()
        self.left_score = 0
        self.right_score = 0
        self.game_over = False
        self.bot_enabled = Config.BOT_ENABLED
        self.bot_reaction_timer = 0
        self.bot_target_y = Config.HEIGHT / 2

        self.left_score_text = self.canvas.create_text(
            Config.WIDTH * 0.25,
            30,
            text=str(self.left_score),
            fill="white",
            font=("Arial", 24, "bold"),
        )
        self.right_score_text = self.canvas.create_text(
            Config.WIDTH * 0.75,
            30,
            text=str(self.right_score),
            fill="white",
            font=("Arial", 24, "bold"),
        )
        self.win_text = self.canvas.create_text(
            Config.WIDTH / 2,
            Config.HEIGHT / 2,
            text="",
            fill="white",
            font=("Arial", 32, "bold"),
        )

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)

        self.running = True
        self.game_loop()

    def on_key_press(self, event: tk.Event) -> None:
        if event.keysym:
            self.pressed_keys.add(event.keysym)
        if event.keysym in ("b", "B"):
            self.bot_enabled = not self.bot_enabled
        if event.keysym == "space" and self.game_over:
            self.reset_game()

    def on_key_release(self, event: tk.Event) -> None:
        if event.keysym in self.pressed_keys:
            self.pressed_keys.remove(event.keysym)

    def move_paddles(self) -> None:
        left_dy = 0
        right_dy = 0
        if "w" in self.pressed_keys or "W" in self.pressed_keys:
            left_dy -= Config.PADDLE_SPEED
        if "s" in self.pressed_keys or "S" in self.pressed_keys:
            left_dy += Config.PADDLE_SPEED
        if self.bot_enabled:
            right_dy = self.get_bot_move()
        else:
            if "Up" in self.pressed_keys:
                right_dy -= Config.PADDLE_SPEED
            if "Down" in self.pressed_keys:
                right_dy += Config.PADDLE_SPEED

        self.move_paddle(self.left_paddle, left_dy)
        self.move_paddle(self.right_paddle, right_dy)

    def move_paddle(self, paddle: int, dy: int) -> None:
        if dy == 0:
            return
        x1, y1, x2, y2 = self.canvas.coords(paddle)
        new_y1 = max(0, y1 + dy)
        new_y2 = min(Config.HEIGHT, y2 + dy)
        self.canvas.coords(paddle, x1, new_y1, x2, new_y2)

    def get_paddle_center(self, paddle: int) -> float:
        _, y1, _, y2 = self.canvas.coords(paddle)
        return (y1 + y2) / 2

    def get_ball_center(self) -> float:
        _, y1, _, y2 = self.canvas.coords(self.ball)
        return (y1 + y2) / 2

    def get_bot_move(self) -> float:
        if self.bot_reaction_timer <= 0:
            target = self.get_ball_center()
            target += random.uniform(-Config.BOT_TARGET_JITTER, Config.BOT_TARGET_JITTER)
            self.bot_target_y = max(0, min(Config.HEIGHT, target))
            self.bot_reaction_timer = Config.BOT_REACTION_FRAMES
        else:
            self.bot_reaction_timer -= 1

        paddle_center = self.get_paddle_center(self.right_paddle)
        distance = self.bot_target_y - paddle_center
        if abs(distance) <= Config.BOT_MAX_SPEED:
            return distance
        return Config.BOT_MAX_SPEED if distance > 0 else -Config.BOT_MAX_SPEED

    def move_ball(self) -> None:
        if self.game_over:
            return
        vx, vy = self.ball_velocity
        self.canvas.move(self.ball, vx, vy)
        x1, y1, x2, y2 = self.canvas.coords(self.ball)

        if y1 <= 0 or y2 >= Config.HEIGHT:
            self.ball_velocity[1] *= -1
            self.canvas.move(self.ball, 0, self.ball_velocity[1])

        if self.check_paddle_collision(self.left_paddle) and vx < 0:
            self.ball_velocity[0] *= -1
            self.canvas.move(self.ball, self.ball_velocity[0], 0)

        if self.check_paddle_collision(self.right_paddle) and vx > 0:
            self.ball_velocity[0] *= -1
            self.canvas.move(self.ball, self.ball_velocity[0], 0)

        if x2 < 0:
            self.add_score("right")
        elif x1 > Config.WIDTH:
            self.add_score("left")

    def check_paddle_collision(self, paddle: int) -> bool:
        bx1, by1, bx2, by2 = self.canvas.coords(self.ball)
        px1, py1, px2, py2 = self.canvas.coords(paddle)
        return bx2 >= px1 and bx1 <= px2 and by2 >= py1 and by1 <= py2

    def add_score(self, side: str) -> None:
        if side == "left":
            self.left_score += 1
            self.canvas.itemconfig(self.left_score_text, text=str(self.left_score))
        else:
            self.right_score += 1
            self.canvas.itemconfig(self.right_score_text, text=str(self.right_score))

        if self.left_score >= 5 or self.right_score >= 5:
            winner = "LEFT" if self.left_score >= 5 else "RIGHT"
            self.canvas.itemconfig(self.win_text, text=f"{winner} WINS")
            self.game_over = True
            self.ball_velocity = [0, 0]
            return

        self.reset_ball()

    def reset_ball(self) -> None:
        self.canvas.coords(
            self.ball,
            Config.WIDTH / 2 - Config.BALL_RADIUS,
            Config.HEIGHT / 2 - Config.BALL_RADIUS,
            Config.WIDTH / 2 + Config.BALL_RADIUS,
            Config.HEIGHT / 2 + Config.BALL_RADIUS,
        )
        self.ball_velocity[0] = random.choice([-1, 1]) * Config.BALL_SPEED_X
        self.ball_velocity[1] = random.choice([-1, 1]) * Config.BALL_SPEED_Y

    def reset_game(self) -> None:
        self.left_score = 0
        self.right_score = 0
        self.canvas.itemconfig(self.left_score_text, text=str(self.left_score))
        self.canvas.itemconfig(self.right_score_text, text=str(self.right_score))
        self.canvas.itemconfig(self.win_text, text="")
        self.game_over = False
        self.bot_reaction_timer = 0
        self.bot_target_y = Config.HEIGHT / 2
        self.reset_ball()

    def game_loop(self) -> None:
        if not self.running:
            return
        self.move_paddles()
        self.move_ball()
        delay = int(1000 / Config.FPS)
        self.root.after(delay, self.game_loop)


def main() -> None:
    root = tk.Tk()
    PongGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
