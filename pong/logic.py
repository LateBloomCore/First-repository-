from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class GameConfig:
    width: int = 800
    height: int = 500
    fps: int = 60
    paddle_width: int = 12
    paddle_height: int = 90
    paddle_speed: int = 6
    ball_radius: int = 10
    ball_speed_x: int = 5
    ball_speed_y: int = 4
    winning_score: int = 5
    bot_enabled: bool = True
    bot_max_speed: int = 4
    bot_reaction_frames: int = 6
    bot_target_jitter: int = 16


@dataclass
class Paddle:
    x: float
    y: float
    width: int
    height: int

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    def move(self, dy: float, bounds_height: float) -> None:
        if dy == 0:
            return
        new_y = max(0, min(bounds_height - self.height, self.y + dy))
        self.y = new_y


@dataclass
class Ball:
    x: float
    y: float
    radius: int

    @property
    def left(self) -> float:
        return self.x - self.radius

    @property
    def right(self) -> float:
        return self.x + self.radius

    @property
    def top(self) -> float:
        return self.y - self.radius

    @property
    def bottom(self) -> float:
        return self.y + self.radius

    def move(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy


@dataclass
class Score:
    left: int = 0
    right: int = 0


@dataclass
class GameState:
    left_paddle: Paddle
    right_paddle: Paddle
    ball: Ball
    ball_velocity: list[float]
    score: Score
    game_over: bool
    bot_enabled: bool
    bot_reaction_timer: int
    bot_target_y: float
    winner: str | None = None


class GameLogic:
    def __init__(self, config: GameConfig | None = None, rng: random.Random | None = None) -> None:
        self.config = config or GameConfig()
        self.rng = rng or random.Random()
        self.state = GameState(
            left_paddle=Paddle(
                x=30,
                y=(self.config.height - self.config.paddle_height) / 2,
                width=self.config.paddle_width,
                height=self.config.paddle_height,
            ),
            right_paddle=Paddle(
                x=self.config.width - 30 - self.config.paddle_width,
                y=(self.config.height - self.config.paddle_height) / 2,
                width=self.config.paddle_width,
                height=self.config.paddle_height,
            ),
            ball=Ball(
                x=self.config.width / 2,
                y=self.config.height / 2,
                radius=self.config.ball_radius,
            ),
            ball_velocity=[self.config.ball_speed_x, self.config.ball_speed_y],
            score=Score(),
            game_over=False,
            bot_enabled=self.config.bot_enabled,
            bot_reaction_timer=0,
            bot_target_y=self.config.height / 2,
        )

    def toggle_bot(self) -> None:
        self.state.bot_enabled = not self.state.bot_enabled

    def update(self, left_move: float, right_move: float) -> None:
        self._move_paddles(left_move, right_move)
        self._move_ball()

    def _move_paddles(self, left_move: float, right_move: float) -> None:
        self.state.left_paddle.move(left_move, self.config.height)
        if self.state.bot_enabled:
            right_move = self._get_bot_move()
        self.state.right_paddle.move(right_move, self.config.height)

    def _get_bot_move(self) -> float:
        if self.state.bot_reaction_timer <= 0:
            target = self.state.ball.y
            target += self.rng.uniform(-self.config.bot_target_jitter, self.config.bot_target_jitter)
            self.state.bot_target_y = max(0, min(self.config.height, target))
            self.state.bot_reaction_timer = self.config.bot_reaction_frames
        else:
            self.state.bot_reaction_timer -= 1

        distance = self.state.bot_target_y - self.state.right_paddle.center_y
        if abs(distance) <= self.config.bot_max_speed:
            return distance
        return self.config.bot_max_speed if distance > 0 else -self.config.bot_max_speed

    def _move_ball(self) -> None:
        if self.state.game_over:
            return

        vx, vy = self.state.ball_velocity
        self.state.ball.move(vx, vy)

        if self.state.ball.top <= 0:
            self.state.ball.y = self.state.ball.radius
            self.state.ball_velocity[1] = abs(vy)
        elif self.state.ball.bottom >= self.config.height:
            self.state.ball.y = self.config.height - self.state.ball.radius
            self.state.ball_velocity[1] = -abs(vy)

        if self._check_paddle_collision(self.state.left_paddle) and vx < 0:
            self.state.ball.x = self.state.left_paddle.x + self.state.left_paddle.width + self.state.ball.radius
            self.state.ball_velocity[0] = abs(vx)

        if self._check_paddle_collision(self.state.right_paddle) and vx > 0:
            self.state.ball.x = self.state.right_paddle.x - self.state.ball.radius
            self.state.ball_velocity[0] = -abs(vx)

        if self.state.ball.right < 0:
            self._add_score("right")
        elif self.state.ball.left > self.config.width:
            self._add_score("left")

    def _check_paddle_collision(self, paddle: Paddle) -> bool:
        ball = self.state.ball
        return (
            ball.right >= paddle.x
            and ball.left <= paddle.x + paddle.width
            and ball.bottom >= paddle.y
            and ball.top <= paddle.y + paddle.height
        )

    def _add_score(self, side: str) -> None:
        if side == "left":
            self.state.score.left += 1
        else:
            self.state.score.right += 1

        if self.state.score.left >= self.config.winning_score or self.state.score.right >= self.config.winning_score:
            self.state.winner = "LEFT" if self.state.score.left >= self.config.winning_score else "RIGHT"
            self.state.game_over = True
            self.state.ball_velocity = [0, 0]
            return

        self.reset_ball()

    def reset_ball(self) -> None:
        self.state.ball.x = self.config.width / 2
        self.state.ball.y = self.config.height / 2
        self.state.ball_velocity[0] = self.rng.choice([-1, 1]) * self.config.ball_speed_x
        self.state.ball_velocity[1] = self.rng.choice([-1, 1]) * self.config.ball_speed_y

    def reset_game(self) -> None:
        self.state.score = Score()
        self.state.winner = None
        self.state.game_over = False
        self.state.bot_reaction_timer = 0
        self.state.bot_target_y = self.config.height / 2
        self.reset_ball()
