"""
a program that tests the menu function

requires:
   pip install pytest

run it with
   pytest
"""
from game import start_game, move_player

def test_open_door_with_key():

    game = start_game()

    # 给钥匙
    game.items.append("key")

    # 人工放一个门
    game.current_level.level[4][8] = "D"

    # 玩家站在门左边
    game.x = 7
    game.y = 4

    # 尝试进入门
    move_player(game, "right")

    # 门已打开
    assert game.current_level.level[4][8] == "d"

    # 玩家已经进入门格
    assert game.x == 8
    assert game.y == 4

    # 钥匙消耗
    assert "key" not in game.items