import math
import numpy as np
from queue import Queue

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
        self.old_player = None
        self.C_ALLOW_BLADE = False
        self.C_AGGRESSIVE = True
        self.C_STUCK_ADJUST = True
        self.C_STUCK_HYSTERESIS = 5
        self.C_PATHFINDING = True
        self.stuck = 0
        self.stuckCorner = (0, 0)


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
        print("Health: " + str(player.health) + "\t Position: " + str(player.pos))
        
        # Check if respawning
        if self.old_player and player.health > self.old_player.health:
            print("---- NEW LIFE ----")
            self.stuck = 0

        actions = []

        if player.pos == self.old_position:
            self.stuck = game_state.current_tick
            print("Stuck!")
            self.find_wall(player.pos, player.dest)
            print(f"Nombre de murs trouvés: {np.sum(self.wall_map)/5}")
            self.instructions = None
            self.choose_stuck_corner()
        else:
            if (game_state.current_tick > self.stuck + self.C_STUCK_HYSTERESIS):
                self.stuck = 0

        self.adjust_aggressiveness(game_state)

        ennemy, ennemyDist = self.find_closest_player(player, game_state.players)

        # Attack with Blade
        if ennemyDist <= 2 and self.C_ALLOW_BLADE:
            if player.playerWeapon != 2:
                actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponBlade))
            actions.append(self.attack_blade(player, ennemy))

        # Attack with gun
        elif ennemyDist <= 20:
            if player.playerWeapon != 1:
                actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponCanon))
            actions.append(self.attack_gun(player, ennemy))

        # Move
        if self.instructions == None or len(self.instructions) == 0:
            if self.stuck and self.C_STUCK_ADJUST:
                print('ALLER VERS STUCK CORNER')
                if self.C_PATHFINDING:
                    #goal = self.stuckCorner
                    goal = (player.pos.x + 15, player.pos.y - 15)
                else:
                    actions.append(MoveAction(self.stuckCorner))
            else:
                coin, coinDistance = self.find_closest_coin(player, game_state.coins)
                if self.C_AGGRESSIVE == False or coinDistance < 5:
                    print('ALLER VERS COIN')
                    if self.C_PATHFINDING:
                        goal = (coin.pos.x, coin.pos.y)
                    else:
                        actions.append(MoveAction((coin.pos.x, coin.pos.y)))
                else:
                    print('ALLER VERS ENNEMY')
                    if self.C_PATHFINDING:
                        goal = (ennemy.pos.x, ennemy.pos.y)
                    else:
                        actions.append(MoveAction((ennemy.pos.x, ennemy.pos.y)))

            if self.C_PATHFINDING:
                self.instructions = self.find_path(player.pos, goal)

        # Save old players
        self.old_position = player.pos
        self.old_player = player

        if self.C_PATHFINDING:
            position = self.instructions.pop(0)
            actions.append(MoveAction((position[0], position[1])))

        return actions


    def find_path(self, position, goal):
        # BFS algorithm to find the shortest path
        maze = self.wall_map
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        start = (int(position.x), int(position.y))
        end = (int(goal[0]), int(goal[1]))

        print(f"Start : {start}")
        print(f"Goal : {end}")

        visited = np.zeros_like(maze, dtype=bool)
        visited[start] = True
        queue = Queue()
        queue.put((start, []))

        while not queue.empty():
            (node, path) = queue.get()
            # print(f'Dans la while, node = {node}, path = {path}')

            for dx, dy in directions:
                next_node = (node[0]+dx, node[1]+dy)
                if (next_node == end):
                    print('CHEMIN DE PATHFINDING TROUVÉ')
                    return path + [next_node]
                if (next_node[0] >= 0 and next_node[1] >= 0 and
                    next_node[0] < maze.shape[0] and next_node[1] < maze.shape[1] and
                    maze[next_node] == 0 and not visited[next_node]):
                    visited[next_node] = True
                    queue.put((next_node, path + [next_node]))


    def find_wall(self, position, destination):
        if destination.y < position.y:
            # WALL UP
            print('Wall up')
            y = int(position.y - 1)
            x_temp = position.x

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(x_temp/5)

            x1 = cell*5
            x2 = x1+1
            x3 = x2+1
            x4 = x3+1
            x5 = x4+1

            self.wall_map[int(x1)][y] = 1
            self.wall_map[int(x2)][y] = 1
            self.wall_map[int(x3)][y] = 1
            self.wall_map[int(x4)][y] = 1
            self.wall_map[int(x5)][y] = 1

        elif destination.y > position.y:
            # WALL DOWN
            print('Wall down')
            y = int(position.y + 1)
            x_temp = position.x

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(x_temp/5)

            x1 = cell*5
            x2 = x1+1
            x3 = x2+1
            x4 = x3+1
            x5 = x4+1

            self.wall_map[int(x1)][y] = 1
            self.wall_map[int(x2)][y] = 1
            self.wall_map[int(x3)][y] = 1
            self.wall_map[int(x4)][y] = 1
            self.wall_map[int(x5)][y] = 1
            
        elif destination.x > position.x:
            print('Wall right')
            # WALL RIGHT
            x = int(position.x + 1)
            y_temp = position.y

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(y_temp/5)

            y1 = cell*5
            y2 = y1+1
            y3 = y2+1
            y4 = y3+1
            y5 = y4+1

            self.wall_map[x][int(y1)] = 1
            self.wall_map[x][int(y2)] = 1
            self.wall_map[x][int(y3)] = 1
            self.wall_map[x][int(y4)] = 1
            self.wall_map[x][int(y5)] = 1

        else:
            # WALL LEFT
            print('Wall left')
            x = int(position.x - 1)
            y_temp = position.y

            # valeur entre 0 et 19 car il y a 20 cell de 5 unité
            cell = math.floor(y_temp/5)

            y1 = cell*5
            y2 = y1+1
            y3 = y2+1
            y4 = y3+1
            y5 = y4+1

            self.wall_map[x][int(y1)] = 1
            self.wall_map[x][int(y2)] = 1
            self.wall_map[x][int(y3)] = 1
            self.wall_map[x][int(y4)] = 1
            self.wall_map[x][int(y5)] = 1


    # def decompress_octets(self):
    #     flat_array = np.unpackbits(self.__map_state.save)
        # small_wall_flat_array = flat_array[:400]
        # small_wall_array = flat_array.reshape((20, 20))

        # big_wall_array = np.zeros((100, 100), dtype=int)

        # for i in range(20):
        #     for j in range(20):
        #         if small_wall_array[i][j] == 1:


    # def compress_array(self, array):
    #     flat_array = array.flatten()
    #     return np.packbits(flat_array)


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
        self.__map_state = map_state
        self.old_position = None
        self.wall_map = np.zeros((100, 100), dtype=int)
        self.instructions = None


    def on_end(self):
        pass

    def find_closest_coin(self, player, coins):
        minDistance = 10000
        bestCoin = None

        for coin in coins:
            distance = math.dist([player.pos.x, player.pos.y], [coin.pos.x, coin.pos.y])

            if distance < minDistance:
                bestCoin = coin
                minDistance = distance

        return bestCoin, minDistance

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
    
    def adjust_aggressiveness(self, game_state):
        if game_state.current_round == 1:
            self.C_AGGRESSIVE = False
            print("Treasure Mode")

        elif game_state.current_tick % 50 < 25:
            self.C_AGGRESSIVE = True
            print("Aggressive Mode")

        else:
            self.C_AGGRESSIVE = False
            print("Discovery Mode")

    def attack_blade(self, player, ennemy):
        dx = player.pos.x - ennemy.pos.x
        dy = player.pos.y - ennemy.pos.y
        return RotateBladeAction(math.atan2(dy, dx))
    
    def attack_gun(self, player, ennemy):
        distance = [player.pos.x - ennemy.pos.x, player.pos.y - ennemy.pos.y]
        norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
        direction = [distance[1] / norm, distance[0] / norm]
        direction = [c * 15 for c in direction]

        #return ShootAction(direction)
        return ShootAction((ennemy.pos.x, ennemy.pos.y))


    def choose_stuck_corner(self, player):
        if self.stuckCorner == (0, 0):
            print("Going lower left")
            self.stuckCorner = (0, 10000)
        elif self.stuckCorner == (0, 10000):
            print("Going lower right")
            self.stuckCorner = (10000, 10000)
        elif self.stuckCorner == (10000, 10000):
            print("Going upper right")
            self.stuckCorner = (10000, 0)
        else:
            print("Going upper left")
            self.stuckCorner = (0, 0)

        return self.stuckCorner