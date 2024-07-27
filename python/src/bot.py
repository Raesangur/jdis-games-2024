import math
import numpy as np

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
        self.name = "Bon Matin"
        self.old_position = None
        self.C_ALLOW_BLADE = False
        self.C_AGGRESSIVE = True


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
                                            
                - RotateBladeAction(rad)    Si vous avez la lame comme arme, vous pouver mettre votre arme
                                       à la rotation donnée en radian.
        Arguments:
            game_state (GameState): (fr): L'état de la partie.
                                (en): The state of the game.   
        """
        print(f"Current tick: {game_state.current_tick}")
        player = [p for p in game_state.players if p.name == "bon-matin"][0]
        print(player.health)


        if player.pos == self.old_position:
            print("Stuck!")
            #octets = self.find_wall(player.pos, player.dest)
            pass

        if game_state.current_tick % 100 < 50:
            self.C_AGGRESSIVE = True
            print("Aggressive Mode")
        else:
            self.C_AGGRESSIVE = False
            print("Discovery Mode")

        actions = []

        ennemy, ennemyDist = self.find_closest_player(player, game_state.players) 
        if ennemyDist <= 2 and self.C_ALLOW_BLADE:
            if player.playerWeapon != 2:
                actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponBlade))

            dx = player.pos.x - ennemy.pos.x
            dy = player.pos.y - ennemy.pos.y
            actions.append(RotateBladeAction(math.atan2(dy, dx)))
        elif ennemyDist <= 15:
            if player.playerWeapon != 1:
                actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponCanon))

            actions.append(ShootAction((ennemy.pos.x, ennemy.pos.y)))

        if self.C_AGGRESSIVE == False:
            coin = self.find_closest_coin(player, game_state.coins)
            actions.append(MoveAction((coin.pos.x, coin.pos.y)))
        else:
            actions.append(MoveAction((ennemy.pos.x, ennemy.pos.y)))

        self.old_position = player.pos
        return actions
    

    def find_wall(self, position, destination):
        wall_map = self.decompress_octets()

        if destination.y < position.y:
            # WALL UP
            y = position.y - 1
            x_temp = position.x

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(x_temp/5)

            x1 = cell*5
            x2 = x1+1
            x3 = x2+1
            x4 = x3+1
            x5 = x4+1

            wall_map[x1][y] = 1
            wall_map[x2][y] = 1
            wall_map[x3][y] = 1
            wall_map[x4][y] = 1
            wall_map[x5][y] = 1

            print(wall_map)
            return self.compress_array(wall_map)

        elif destination.y > position.y:
            # WALL DOWN
            y = position.y + 1
            x_temp = position.x

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(x_temp/5)

            x1 = cell*5
            x2 = x1+1
            x3 = x2+1
            x4 = x3+1
            x5 = x4+1

            wall_map[x1][y] = 1
            wall_map[x2][y] = 1
            wall_map[x3][y] = 1
            wall_map[x4][y] = 1
            wall_map[x5][y] = 1

            print(wall_map)
            return self.compress_array(wall_map)
            
        elif destination.x > position.x:
            # WALL RIGHT
            x = position.x + 1
            y_temp = position.y

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(y_temp/5)

            y1 = cell*5
            y2 = y1+1
            y3 = y2+1
            y4 = y3+1
            y5 = y4+1

            wall_map[x][y1] = 1
            wall_map[x][y2] = 1
            wall_map[x][y3] = 1
            wall_map[x][y4] = 1
            wall_map[x][y5] = 1

            print(wall_map)
            return self.compress_array(wall_map)
        else:
            # WALL LEFT
            x = position.x - 1
            y_temp = position.y

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(y_temp/5)

            y1 = cell*5
            y2 = y1+1
            y3 = y2+1
            y4 = y3+1
            y5 = y4+1

            wall_map[x][y1] = 1
            wall_map[x][y2] = 1
            wall_map[x][y3] = 1
            wall_map[x][y4] = 1
            wall_map[x][y5] = 1

            print(wall_map)
            return self.compress_array(wall_map)


    def decompress_octets(self):
        flat_array = np.unpackbits(self.__map_state.save)
        return flat_array.reshape((100, 100))


    def compress_array(self, array):
        flat_array = array.flatten()
        return np.packbits(flat_array)


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
        self.old_position = None
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