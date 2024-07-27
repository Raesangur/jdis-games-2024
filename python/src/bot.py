import math
import numpy

from typing import List, Union

from core.action import MoveAction, ShootAction, RotateBladeAction, SwitchWeaponAction, SaveAction
from core.consts import Consts
from core.game_state import GameState, PlayerWeapon, Point
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
        players = [p for p in game_state.players]
        print(players)
        player = [p for p in players if p.name == "bon-matin"][0]
        print(player.health)

        if player.position == self.old_position:
            octets = find_wall(player.position, player.destination)

        actions = [
            MoveAction((10.0, 11.34)),
            ShootAction((11.2222, 13.547)),
            SwitchWeaponAction(PlayerWeapon.PlayerWeaponBlade),
            SaveAction(b"Bon Matin"),
        ]

        return actions
    

    def find_wall(position, destination):
        wall_map = decompress_octets()

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
            return compress_array(wall_map)

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
            return compress_array(wall_map)
            
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
            return compress_array(wall_map)
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
            return compress_array(wall_map)


    def decompress_octets():
        flat_array = np.unpackbits(self.__map_state.save)
        return flat_array.reshape((100, 100))


    def compress_array(array):
        flat_array = array.flatten()
        return np.packbits(flat_array)


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
