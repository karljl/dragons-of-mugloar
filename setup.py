from models import Game


def new_game() -> Game:
    game = Game()

    game.start_game()

    game.initialize_player()
    game.initialize_reputation()
    game.initialize_dragon()
    game.initialize_shop()
    game.initialize_message_manager()

    return game
