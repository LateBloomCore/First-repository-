from random import uniform

from ursina import Entity, Text, Ursina, color, destroy
from ursina.prefabs.first_person_controller import FirstPersonController


COIN_COUNT = 8
COIN_AREA = 12
COIN_HEIGHT = 0.6
COLLECT_DISTANCE = 1.2


def create_coin(position):
    return Entity(
        model="sphere",
        color=color.yellow,
        scale=0.6,
        position=position,
        collider="sphere",
    )


def random_coin_position():
    return (uniform(-COIN_AREA, COIN_AREA), COIN_HEIGHT, uniform(-COIN_AREA, COIN_AREA))


def setup_scene():
    Entity(
        model="plane",
        texture="white_cube",
        texture_scale=(40, 40),
        scale=40,
        color=color.lime,
        collider="box",
        position=(0, 0, 0),
    )


def main():
    app = Ursina()

    setup_scene()

    player = FirstPersonController()
    player.gravity = 0.6

    score_text = Text(text="Score: 0", position=(-0.85, 0.45), origin=(0, 0), scale=1.5)
    win_text = Text(
        text="YOU WIN",
        origin=(0, 0),
        scale=3,
        color=color.azure,
        enabled=False,
        background=True,
    )

    coins = []
    score = 0

    def spawn_coins():
        nonlocal coins
        for coin in coins:
            destroy(coin)
        coins = [create_coin(random_coin_position()) for _ in range(COIN_COUNT)]

    def reset_game():
        nonlocal score
        score = 0
        score_text.text = "Score: 0"
        win_text.enabled = False
        spawn_coins()

    spawn_coins()

    def update():
        nonlocal score
        if win_text.enabled:
            return

        for coin in coins[:]:
            if (player.position - coin.position).length() <= COLLECT_DISTANCE:
                destroy(coin)
                coins.remove(coin)
                score += 1
                score_text.text = f"Score: {score}"

        if not coins:
            win_text.enabled = True

    def input(key):
        if key == "space" and win_text.enabled:
            reset_game()

    app.update = update
    app.input = input

    app.run()


if __name__ == "__main__":
    main()
