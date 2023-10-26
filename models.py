import random

from exceptions import GameNotInstantiatedError
from helpers import send_request


class Player:

    def __init__(self, game: "Game", lives: int, gold: int) -> None:
        self._game = game
        self._lives = lives
        self._gold = gold

    @property
    def lives(self) -> int:
        return self._lives

    @lives.setter
    def lives(self, value: int) -> None:
        self._lives = value

    @property
    def gold(self) -> int:
        return self._gold

    @gold.setter
    def gold(self, value: int) -> None:
        self._gold = value

    def has_x_amount_of_money(self, amount: int) -> bool:
        return self._gold >= amount

    def buy_item(self, item_id: str) -> None:
        item = self._game.shop.get_item(item_id)
        if self._gold >= item.cost:
            self._game.shop.sell_item(item)

    def solve_message(self, message: "Message") -> dict:
        return self._game.message_manager.solve_message(message)


class Dragon:

    def __init__(self, game: "Game", level: int) -> None:
        self._game = game
        self._level = level

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        self._level = value


class Reputation:

    def __init__(self, game: "Game") -> None:
        self._game = game
        self._people: int = 0
        self._state: int = 0
        self._underworld: int = 0

    def investigate(self) -> None:
        url = f'https://dragonsofmugloar.com/api/v2/{self._game.game_id}/investigate/reputation'
        data = send_request(url, 'POST')

        self._people = data['people']
        self._state = data['state']
        self._underworld = data['underworld']

    @property
    def people(self) -> int:
        return self._people

    @property
    def state(self) -> int:
        return self._state

    @property
    def underworld(self) -> int:
        return self._underworld

    def __repr__(self) -> str:
        return f'Reputation(people={self._people}, state={self._state}, underworld={self._underworld})'


class Message:

    def __init__(self, ad_id: str, description: str, reward: int,
                 expires_in: int, probability: str, encrypted: bool) -> None:

        self._ad_id = ad_id
        self._description = description
        self._reward = reward
        self._expires_in = expires_in
        self._probability = probability

        self._encrypted = encrypted

    @property
    def reward(self) -> int:
        return self._reward

    @property
    def ad_id(self) -> str:
        return self._ad_id

    @property
    def description(self) -> str:
        return self._description

    @property
    def expires_in(self) -> int:
        return self._expires_in

    @property
    def probability(self) -> str:
        return self._probability

    @property
    def encrypted(self) -> bool:
        return self._encrypted

    def __repr__(self) -> str:
        return (f'Message(ad_id={self._ad_id}, description={self._description}, reward={self._reward},'
                f' expires_in={self._expires_in}, probability={self._probability}, encrypted={self._encrypted})')


class MessageManager:

    def __init__(self, game: "Game") -> None:
        self._game = game
        self._messages: set[Message] = set()

    @property
    def messages(self) -> set[Message]:
        return set(filter(lambda x: x.encrypted is False, self._messages))

    def messages_by_probability(self, keywords: set[str] = None) -> set[Message]:
        if keywords is None:
            return self.messages
        return set(filter(lambda x: x.probability in keywords, self.messages))

    def filtered_messages(self, keywords: set[str], message_set: set = None) -> set[Message]:
        if message_set is None:
            message_set = self.messages

        def contains(message: Message) -> bool:
            for keyword in keywords:
                if keyword in message.description:
                    return True
            return False

        return set(filter(lambda x: not contains(x), message_set))

    def highest_value_message(self, message_set: set = None) -> Message:
        if message_set is None:
            message_set = self.messages
        return max(message_set, key=lambda x: x.reward)

    def update_messages(self) -> None:
        url = f'https://dragonsofmugloar.com/api/v2/{self._game.game_id}/messages'
        data = send_request(url, 'GET')

        new_messages = set()
        for message in data:
            try:
                is_encrypted = message['encrypted']
            except KeyError:
                is_encrypted = False

            new_message = Message(message['adId'], message['message'], message['reward'],
                                  message['expiresIn'], message['probability'], is_encrypted)

            new_messages.add(new_message)
        self._messages = new_messages

    def solve_message(self, message: Message) -> dict:
        url = f'https://dragonsofmugloar.com/api/v2/{self._game.game_id}/solve/{message.ad_id}'
        data = send_request(url, 'POST')

        self._game.player.lives = data['lives']
        self._game.player.gold = data['gold']
        self._game.turn = data['turn']
        self._game.score = data['score']

        return {
            'success': data['success'],
            'description': data['message']
        }


class ShopItem:

    def __init__(self, item_id: str, name: str, cost: int) -> None:
        self._item_id = item_id
        self._name = name
        self._cost = cost

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def cost(self) -> int:
        return self._cost

    def __repr__(self) -> str:
        return f'ShopItem(item_id={self._item_id}, name={self._name}, cost={self._cost})'


class Shop:

    def __init__(self, game: "Game") -> None:
        self._game = game
        self._items: dict[str:ShopItem] = {}

    @property
    def upgrades(self) -> dict:
        return {item_id: item for item_id, item in self._items.items() if item_id != 'hpot'}

    def get_item(self, item_id: str) -> ShopItem:
        return self._items[item_id]

    def upgrades_by_cost(self, cost: int) -> dict:
        return {item_id: item for item_id, item in self._items.items() if item.cost == cost}

    def get_random_upgrade(self, cost: int | None = None) -> str:
        if cost is None:
            return random.choice(list(self.upgrades.keys()))
        return random.choice(list(self.upgrades_by_cost(cost).keys()))

    def update_items(self) -> None:
        url = f'https://dragonsofmugloar.com/api/v2/{self._game.game_id}/shop'
        data = send_request(url, 'GET')

        new_items = {}
        for item in data:
            new_item = ShopItem(item['id'], item['name'], item['cost'])
            new_items[new_item.item_id] = new_item

        self._items = new_items

    def sell_item(self, item: ShopItem) -> None:
        url = f'https://dragonsofmugloar.com/api/v2/{self._game.game_id}/shop/buy/{item.item_id}'
        data = send_request(url, 'POST')

        self._game.player.gold = data['gold']
        self._game.player.lives = data['lives']
        self._game.dragon.level = data['level']
        self._game.turn = data['turn']


class Game:

    def __init__(self) -> None:
        self._data: dict | None = None

        self._player: Player | None = None
        self._dragon: Dragon | None = None
        self._reputation: Reputation | None = None
        self._message_manager: MessageManager | None = None
        self._shop: Shop | None = None

        self._turn: int = 0
        self._score: int = 0

    def start_game(self) -> None:
        url = 'https://dragonsofmugloar.com/api/v2/game/start'
        self._data: dict = send_request(url, 'POST')

    @property
    def game_id(self) -> str | None:
        if self._data is not None:
            return self._data['gameId']
        raise GameNotInstantiatedError('PLease create a game object before running this function.')

    @property
    def player(self) -> Player | None:
        if self._player is not None:
            return self._player
        raise GameNotInstantiatedError('PLease create a game object before running this function.')

    @property
    def reputation(self) -> Reputation | None:
        if self._reputation is not None:
            return self._reputation
        raise GameNotInstantiatedError('PLease create a game object before running this function.')

    @property
    def dragon(self) -> Dragon | None:
        if self._dragon is not None:
            return self._dragon
        raise GameNotInstantiatedError('PLease create a game object before running this function.')

    @property
    def message_manager(self) -> MessageManager | None:
        if self._message_manager is not None:
            return self._message_manager
        raise GameNotInstantiatedError('PLease create a game object before running this function.')

    @property
    def shop(self) -> Shop | None:
        if self._shop is not None:
            return self._shop
        raise GameNotInstantiatedError('PLease create a game object before running this function.')

    @property
    def turn(self) -> int:
        return self._turn

    @turn.setter
    def turn(self, value: int) -> None:
        self._turn = value

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        self._score = value

    def initialize_player(self) -> None:
        if self._data is not None:
            self._player = Player(self, self._data['lives'], self._data['gold'])
        else:
            raise GameNotInstantiatedError('PLease create a game object before running this function.')

    def initialize_reputation(self) -> None:
        if self._data is not None:
            self._reputation = Reputation(self)
        else:
            raise GameNotInstantiatedError('PLease create a game object before running this function.')

    def initialize_dragon(self) -> None:
        if self._data is not None:
            self._dragon = Dragon(self, self._data['level'])
        else:
            raise GameNotInstantiatedError('PLease create a game object before running this function.')

    def initialize_message_manager(self) -> None:
        if self._data is not None:
            self._message_manager = MessageManager(self)
            self._message_manager.update_messages()
        else:
            raise GameNotInstantiatedError('PLease create a game object before running this function.')

    def initialize_shop(self) -> None:
        if self._data is not None:
            self._shop = Shop(self)
            self._shop.update_items()
        else:
            raise GameNotInstantiatedError('PLease create a game object before running this function.')
