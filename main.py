import tkinter as tk

from pong.logic import GameLogic


class PongGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PONG")
        self.logic = GameLogic()
        self.config = self.logic.config
        self.root.geometry(f"{self.config.width}x{self.config.height}")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(
            self.root,
            width=self.config.width,
            height=self.config.height,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        state = self.logic.state
        self.left_paddle = self.canvas.create_rectangle(
            state.left_paddle.x,
            state.left_paddle.y,
            state.left_paddle.x + state.left_paddle.width,
            state.left_paddle.y + state.left_paddle.height,
            fill="white",
            outline="",
        )
        self.right_paddle = self.canvas.create_rectangle(
            state.right_paddle.x,
            state.right_paddle.y,
            state.right_paddle.x + state.right_paddle.width,
            state.right_paddle.y + state.right_paddle.height,
            fill="white",
            outline="",
        )
        self.ball = self.canvas.create_oval(
            state.ball.x - state.ball.radius,
            state.ball.y - state.ball.radius,
            state.ball.x + state.ball.radius,
            state.ball.y + state.ball.radius,
            fill="white",
            outline="",
        )

        self.pressed_keys: set[str] = set()

        self.left_score_text = self.canvas.create_text(
            self.config.width * 0.25,
            30,
            text=str(state.score.left),
            fill="white",
            font=("Arial", 24, "bold"),
        )
        self.right_score_text = self.canvas.create_text(
            self.config.width * 0.75,
            30,
            text=str(state.score.right),
            fill="white",
            font=("Arial", 24, "bold"),
        )
        self.win_text = self.canvas.create_text(
            self.config.width / 2,
            self.config.height / 2,
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
            self.logic.toggle_bot()
        if event.keysym == "space" and self.logic.state.game_over:
            self.logic.reset_game()

    def on_key_release(self, event: tk.Event) -> None:
        if event.keysym in self.pressed_keys:
            self.pressed_keys.remove(event.keysym)

    def get_paddle_input(self) -> tuple[float, float]:
        left_dy = 0
        right_dy = 0
        if "w" in self.pressed_keys or "W" in self.pressed_keys:
            left_dy -= self.config.paddle_speed
        if "s" in self.pressed_keys or "S" in self.pressed_keys:
            left_dy += self.config.paddle_speed
        if "Up" in self.pressed_keys:
            right_dy -= self.config.paddle_speed
        if "Down" in self.pressed_keys:
            right_dy += self.config.paddle_speed
        return left_dy, right_dy

    def render(self) -> None:
        state = self.logic.state
        self.canvas.coords(
            self.left_paddle,
            state.left_paddle.x,
            state.left_paddle.y,
            state.left_paddle.x + state.left_paddle.width,
            state.left_paddle.y + state.left_paddle.height,
        )
        self.canvas.coords(
            self.right_paddle,
            state.right_paddle.x,
            state.right_paddle.y,
            state.right_paddle.x + state.right_paddle.width,
            state.right_paddle.y + state.right_paddle.height,
        )
        self.canvas.coords(
            self.ball,
            state.ball.x - state.ball.radius,
            state.ball.y - state.ball.radius,
            state.ball.x + state.ball.radius,
            state.ball.y + state.ball.radius,
        )
        self.canvas.itemconfig(self.left_score_text, text=str(state.score.left))
        self.canvas.itemconfig(self.right_score_text, text=str(state.score.right))
        win_text = f"{state.winner} WINS" if state.game_over and state.winner else ""
        self.canvas.itemconfig(self.win_text, text=win_text)

    def game_loop(self) -> None:
        if not self.running:
            return
        left_dy, right_dy = self.get_paddle_input()
        self.logic.update(left_dy, right_dy)
        self.render()
        delay = int(1000 / self.config.fps)
        self.root.after(delay, self.game_loop)


def main() -> None:
    root = tk.Tk()
    PongGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
