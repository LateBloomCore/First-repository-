import random

from pong.logic import GameConfig, GameLogic


def test_ball_bounces_off_wall() -> None:
    config = GameConfig(width=200, height=100, ball_speed_y=4)
    logic = GameLogic(config=config, rng=random.Random(0))
    logic.state.bot_enabled = False
    logic.state.ball.y = logic.state.ball.radius - 1
    logic.state.ball_velocity = [0, -4]

    logic.update(0, 0)

    assert logic.state.ball_velocity[1] > 0
    assert logic.state.ball.y == logic.state.ball.radius


def test_ball_bounces_off_paddle() -> None:
    config = GameConfig(width=200, height=100, ball_speed_x=5)
    logic = GameLogic(config=config, rng=random.Random(0))
    logic.state.bot_enabled = False
    paddle = logic.state.left_paddle
    logic.state.ball.x = paddle.x + paddle.width + logic.state.ball.radius - 1
    logic.state.ball.y = paddle.center_y
    logic.state.ball_velocity = [-5, 0]

    logic.update(0, 0)

    assert logic.state.ball_velocity[0] > 0


def test_scoring_increments_and_resets_ball() -> None:
    config = GameConfig(width=200, height=100)
    logic = GameLogic(config=config, rng=random.Random(0))
    logic.state.bot_enabled = False
    logic.state.ball.x = config.width + logic.state.ball.radius + 1
    logic.state.ball_velocity = [0, 0]

    logic.update(0, 0)

    assert logic.state.score.left == 1
    assert logic.state.ball.x == config.width / 2
    assert logic.state.ball.y == config.height / 2


def test_reset_ball_sets_center_and_speed() -> None:
    config = GameConfig(width=200, height=100, ball_speed_x=5, ball_speed_y=4)
    logic = GameLogic(config=config, rng=random.Random(1))
    logic.state.ball.x = 10
    logic.state.ball.y = 20

    logic.reset_ball()

    assert logic.state.ball.x == config.width / 2
    assert logic.state.ball.y == config.height / 2
    assert abs(logic.state.ball_velocity[0]) == config.ball_speed_x
    assert abs(logic.state.ball_velocity[1]) == config.ball_speed_y
