from setup import new_game
from models import Player, Shop, Message

from constants import *
# normally it's a bad practice to use * for imports as it can be difficult to track where something is coming from,
# but since constants are the only things written in uppercase, I think it is a good exception.


def buy_items(player: Player, shop: Shop) -> None:
    while player.has_x_amount_of_money(HEALTH_POTION_VAL) and player.lives < PLAYER_LIVES_UPPER_LIMIT:
        print('Buying a health potion.')
        player.buy_item('hpot')

    while player.has_x_amount_of_money(HEALTH_POTION_VAL + EXPENSIVE_ITEM_VAL):
        print('Buying a random $300 item.')
        item = shop.get_random_upgrade(EXPENSIVE_ITEM_VAL)
        player.buy_item(item)

    while player.has_x_amount_of_money(HEALTH_POTION_VAL + CHEAP_ITEM_VAL):
        print('Buying a random $100 item.')
        item = shop.get_random_upgrade(CHEAP_ITEM_VAL)
        player.buy_item(item)


def get_highest_value_message(message_manager) -> Message:
    easy_messages = message_manager.messages_by_probability(EASY_MESSAGES)
    difficult_messages = message_manager.messages_by_probability(DIFFICULT_MESSAGES)

    easy_messages_filtered = message_manager.filtered_messages(TO_AVOID, easy_messages)
    difficult_messages_filtered = message_manager.filtered_messages(TO_AVOID, difficult_messages)

    if len(easy_messages_filtered) > 0:
        highest_value_message = message_manager.highest_value_message(easy_messages_filtered)
    elif len(difficult_messages_filtered) > 0:
        highest_value_message = message_manager.highest_value_message(difficult_messages_filtered)
    else:
        highest_value_message = message_manager.highest_value_message(message_manager.messages)

    return highest_value_message


def main():
    game = new_game()

    while game.player.lives > 0:

        buy_items(game.player, game.shop)

        game.message_manager.update_messages()
        highest_value_message = get_highest_value_message(game.message_manager)

        print('Highest value message is: ', highest_value_message)

        message_solved = game.player.solve_message(highest_value_message)

        print(message_solved['description'])
        print('Lives: ', game.player.lives)
        print('Current score: ', game.score)
        print()

    print('Game over!')
    print('Score: ', game.score)
    print('Level: ', game.dragon.level)


if __name__ == '__main__':
    main()
