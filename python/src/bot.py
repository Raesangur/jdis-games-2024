import math

from typing import List, Union

from core.action import MoveAction, ShootAction, RotateBladeAction, SwitchWeaponAction, SaveAction
from core.consts import Consts
from core.game_state import GameState, PlayerWeapon, Point, Coin
from core.map_state import MapState


class MyBot:
    """
    (fr) Cette classe représente votre bot. Vous pouvez y définir des attributs et des méthodes qui 
        seront conservées entre chaque appel de la méthode `on_tick`.
    """
    __map_state: MapState
    name : str
    
    def __init__(self):
        self.name = "Magellan"


    def on_tick(self, game_state: GameState) -> List[Union[MoveAction, SwitchWeaponAction, RotateBladeAction, ShootAction, SaveAction]]:
        """
        (fr)    Cette méthode est appelée à chaque tick de jeu. Vous pouvez y définir 
                le comportement de votre bot. Elle doit retourner une liste d'actions 
                qui sera exécutée par le serveur.

                Liste des actions possibles:
                - MoveAction((x, y))       permet de diriger son bot, il ira a vitesse
                                       constante jusqu'à ce point.

                - ShootAction((x, y))      Si vous avez le fusil comme arme, cela va tirer
                                       à la coordonnée donnée.

                - SaveAction([...])        Permet de storer 100 octets dans le serveur. Lors
                                       de votre reconnection, ces données vous seront
                                       redonnées par le serveur.

                - SwitchWeaponAction(id)    Permet de changer d'arme. Par défaut, votre bot
                                       n'est pas armé, voici vos choix:
                                            PlayerWeapon.PlayerWeaponNone
                                            PlayerWeapon.PlayerWeaponCanon
                                            PlayerWeapon.PlayerWeaponBlade
                                            
                - BladeRotateAction(rad)    Si vous avez la lame comme arme, vous pouver mettre votre arme
                                       à la rotation donnée en radian.
        Arguments:
            game_state (GameState): (fr): L'état de la partie.
                                (en): The state of the game.   
        """
        print(f"Current tick: {game_state.current_tick}")
        player = [p for p in game_state.players if p.name == "bon-matin"][0]
        print(player.health)

        coin = self.find_closest_coin(player, game_state.coins)

        actions = [
            #SwitchWeaponAction(PlayerWeapon.PlayerWeaponBlade),
            #RotateBladeAction((game_state.current_tick % 8) * math.pi / 4),
            MoveAction((coin.pos.x, coin.pos.y)),
        ]

        ennemy, ennemyDist = self.find_closest_player(player, game_state.players) 

        if (ennemyDist < 15):
            if player.playerWeapon != 1:
                actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponCanon))

            actions.append(ShootAction((ennemy.pos.x, ennemy.pos.y)))
        
        return actions
    

    def find_wall(position, destination, wall_map):
        # 1- find direction
        if destination.y < position.y:
            direction = 'UP'
        elif destination.y > position.y:
            direction = 'DOWN'
        elif destination.x > position.x:
            direction = 'RIGHT'
        else:
            direction = 'LEFT'
        
        # 2- store wall
        array = [[0] * 100 for _ in range(100)]
        

    def rotate_blade(angle):
        if angle == "UP":
            return RotateBladeAction(math.pi / 2)
        if angle == "RIGHT":
            return RotateBladeAction(0)
        if angle == "LEFT":
            return RotateBladeAction(math.pi)
        else:
            return RotateBladeAction(math.pi / -2)

    def shoot_cannon(currentPos, angle, distance = 15):
        dx = 0
        dy = 0
        if angle == "UP":
            dx = 0
            dy = distance
        if angle == "DOWN":
            dx = 0
            dy = -distance
        if angle == "RIGHT":
            dx = distance
            dy = 0
        if angle == "LEFT":
            dx = -distance
            dy = 0

        return ShootAction(currentPos.x + dx, currentPos.y + dy)



    def on_start(self, map_state: MapState):
        """
        (fr) Cette méthode est appelée une seule fois au début de la partie. Vous pouvez y définir des
            actions à effectuer au début de la partie.

        Arguments:
            map_state (MapState): (fr) L'état de la carte.
        """
        self.__map_state = map_state
        self.old_position = 0
        pass


    def on_end(self):
        """
        (fr) Cette méthode est appelée une seule fois à la fin de la partie. Vous pouvez y définir des
            actions à effectuer à la fin de la partie.
        """
        pass

    def find_closest_coin(self, player, coins):
        minDistance = 10000
        bestCoin = None

        for coin in coins:
            distance = math.dist([player.pos.x, player.pos.y], [coin.pos.x, coin.pos.y])

            if distance < minDistance:
                bestCoin = coin
                minDistance = distance

        return bestCoin

    def find_closest_player(self, player, players):
        minDistance = 10000
        bestPlayer = None

        for p in players:
            distance = math.dist([player.pos.x, player.pos.y], [p.pos.x, p.pos.y])
            if distance == 0:
                continue

            if distance < minDistance:
                bestPlayer = p
                minDistance = distance

        return bestPlayer, minDistance