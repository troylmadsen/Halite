import hlt
import logging
import numpy as np
from collections import OrderedDict
import os
import random

# The running version of the bot
VERSION = 2

# Number of feature per entity to track
HM_ENT_FEATURES = 5

# Chance of a random behavior modification
PCT_CHANGE_CHANCE = 30

# Number of ships to maintain
# Too many results in a timeout
DESIRED_SHIP_COUNT = 50

# Number of actions available to the bot to issue to ship_plans
NUM_ACTIONS = 4

# Creating game and beginning logging
game = hlt.Game("TMasden{}".format(VERSION))
logging.info("TMasdenBot-{} Start".format(VERSION))

# Current ship movement plans
ship_plans = {}

# Storing the moves of the winning bot
if os.path.exists("c{}_input.vec".format(VERSION)):
    os.remove("c{}_input.vec".format(VERSION))

if os.path.exists("c{}_out.vec".format(VERSION)):
    os.remove("c{}_out.vec".format(VERSION))


# Allow for reverse looking in a dictionary
def key_by_value(dictionary, value):
    for k,v in dictionary.items():
        if v[0] == value:
            return k
    return -99


# Ensure that our entity has  HM_ENT_FEATURES
def fix_data(data):
    new_list = []
    last_known_idx = 0
    for i in range(HM_ENT_FEATURES):
        try:
            if i < len(data):
                last_known_idx=i
            new_list.append(data[last_known_idx])
        except:
            new_list.append(0)

    return new_list


# Begin game loop
while True:
    # Begin turn loop
    # Get the map state
    game_map = game.update_map()

    # Commands to control ships this turn to be sent to server
    command_queue = []

    # Gather info for friendly, all, an enemy ships
    team_ships = game_map.get_me().all_ships()
    all_ships = game_map._all_ships()
    enemy_ships = [ship for ship in game_map._all_ships() if ship not in team_ships]

    # Count number of friendly, all, and enemy ships
    my_ship_count = len(team_ships)
    enemy_ship_count = len(enemy_ships)
    all_ship_count = len(all_ships)

    # Get player ID
    my_id = game_map.get_me().id

    # Number of players in the game for the bot to know
    remaining_players = len(game_map.all_players())

    # Gather all empty, friendly, and enemy planets
    empty_planet_sizes = {}
    our_planet_sizes = {}
    enemy_planet_sizes = {}

    for p in game_map.all_planets():
        radius = p.radius
        if not p.is_owned():
            empty_planet_sizes[radius] = p
        elif p.owner.id == game_map.get_me().id:
            our_planet_sizes[radius] = p
        elif p.owner.id != game_map.get_me().id:
            enemy_planet_sizes[radius] = p

    # Count number of empty, friendly, and enemy planets
    hm_our_planets = len(our_planet_sizes)
    hm_empty_planets = len(empty_planet_sizes)
    hm_enemy_planets = len(enemy_planet_sizes)

    # Sort all planets by sizes, largest to smallest
    empty_planet_keys = sorted([k for k in empty_planet_sizes])[::-1]
    our_planet_keys = sorted([k for k in our_planet_sizes])[::-1]
    enemy_planet_keys= sorted([k for k in enemy_planet_sizes])[::-1]

    for ship in game_map.get_me().all_ships():
        try:
            #TODO Allow the bot to decide to dock/undock
            # Ship cannot do anything, skip it
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                # Skip this ship
                continue

            #FIXME unused
            # Get the ship ID
            shipid = ship.id

            # Determine if the ship should changed its action
            change = False
            if random.randint(1,100) <= PCT_CHANGE_CHANCE:
                change = True

            # All entities by distance, closest to furthest from current ship
            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))

            # Closes empty planets and their distancs
            closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
            closest_empty_planet_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]

            # Closest friendly planets and their distances
            closest_my_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].is_owned() and (entities_by_distance[distance][0].owner.id == game_map.get_me().id)]
            closest_my_planets_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].is_owned() and (entities_by_distance[distance][0].owner.id == game_map.get_me().id)]

            # Closest enemy planets and their distances
            closest_enemy_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0] not in closest_my_planets and entities_by_distance[distance][0] not in closest_empty_planets]
            closest_enemy_planets_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0] not in closest_my_planets and entities_by_distance[distance][0] not in closest_empty_planets]

            # Closest friendly ships and their distances
            closest_team_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] in team_ships]
            closest_team_ships_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] in team_ships]

            # Closest enemy ships and their distances
            closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]
            closest_enemy_ships_distances = [distance for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]

            # Distances to largest empty, friendly, and enemy planets
            largest_empty_planet_distances = []
            largest_our_planet_distances = []
            largest_enemy_planet_distances = []

            for i in range(HM_ENT_FEATURES):
                try: largest_empty_planet_distances.append(key_by_value(entities_by_distance, empty_planet_sizes[empty_planet_keys[i]]))
                except:largest_empty_planet_distances.append(-99)

                try: largest_our_planet_distances.append(key_by_value(entities_by_distance, our_planet_sizes[our_planet_keys[i]]))
                except:largest_our_planet_distances.append(-99)

                try: largest_enemy_planet_distances.append(key_by_value(entities_by_distance, enemy_planet_sizes[enemy_planet_keys[i]]))
                except:largest_enemy_planet_distances.append(-99)


            # Entity data for the neural network
            entity_lists = [fix_data(closest_empty_planet_distances),
                            fix_data(closest_my_planets_distances),
                            fix_data(closest_enemy_planets_distances),
                            fix_data(closest_team_ships_distances),
                            fix_data(closest_enemy_ships_distances),
                            fix_data(empty_planet_keys),
                            fix_data(our_planet_keys),
                            fix_data(enemy_planet_keys),
                            fix_data(largest_empty_planet_distances),
                            fix_data(largest_our_planet_distances),
                            fix_data(largest_enemy_planet_distances)]


            # Input vector for the neural network
            input_vector = []

            # Provide only HM_ENT_FEATURES per feature to neural network
            for i in entity_lists:
                for ii in i[:HM_ENT_FEATURES]:
                    input_vector.append(ii)

            # Add last few attribtes to neural network
            input_vector += [my_ship_count,
                             enemy_ship_count,
                             hm_our_planets,
                             hm_empty_planets,
                             hm_enemy_planets,
                             remaining_players]

            #TODO Maybe don't have this
            # If we have too many ships to process in a timely manner, dispose
            # of excess ships
            if my_ship_count > DESIRED_SHIP_COUNT:
                '''ATTACK: [1,0,0,0]'''

                output_vector = NUM_ACTIONS*[0] #[0,0,0,0]
                output_vector[0] = 1 #[1,0,0,0]
                ship_plans[ship.id] = output_vector

            # Random chance to change plans or assign a plan
            elif change or ship.id not in ship_plans:
                '''
                pick new "plan"
                '''
                output_vector = NUM_ACTIONS*[0]
                output_vector[random.randint(0,NUM_ACTIONS-1)] = 1
                ship_plans[ship.id] = output_vector

            else:
                '''continue to execute existing plan'''
                output_vector = ship_plans[ship.id]


            try:

                # ATTACK ENEMY SHIP #
                if np.argmax(output_vector) == 0: #[1,0,0,0]
                    '''
                    type: 0
                    Find closest enemy ship, and attack!
                    '''
                    if not isinstance(closest_enemy_ships[0], int):
                        navigate_command = ship.navigate(
                                    ship.closest_point_to(closest_enemy_ships[0]),
                                    game_map,
                                    speed=int(hlt.constants.MAX_SPEED),
                                    ignore_ships=False)

                        if navigate_command:
                            command_queue.append(navigate_command)



                # MINE ONE OF OUR PLANETS #
                elif np.argmax(output_vector) == 1: #[0,1,0,0]
                    '''
                    type: 1
                    Mine closest already-owned planet
                    '''
                    if not isinstance(closest_my_planets[0], int):
                        target =  closest_my_planets[0]

                        if len(target._docked_ship_ids) < target.num_docking_spots:
                            if ship.can_dock(target):
                                command_queue.append(ship.dock(target))
                            else:
                                navigate_command = ship.navigate(
                                            ship.closest_point_to(target),
                                            game_map,
                                            speed=int(hlt.constants.MAX_SPEED),
                                            ignore_ships=False)

                                if navigate_command:
                                    command_queue.append(navigate_command)

                        # else:
                        #     #attack!
                        #     if not isinstance(closest_enemy_ships[0], int):
                        #         navigate_command = ship.navigate(
                        #                     ship.closest_point_to(closest_enemy_ships[0]),
                        #                     game_map,
                        #                     speed=int(hlt.constants.MAX_SPEED),
                        #                     ignore_ships=False)
                        #
                        #         if navigate_command:
                        #             command_queue.append(navigate_command)



                    # elif not isinstance(closest_empty_planets[0], int):
                    #     target =  closest_empty_planets[0]
                    #     if ship.can_dock(target):
                    #         command_queue.append(ship.dock(target))
                    #     else:
                    #         navigate_command = ship.navigate(
                    #                     ship.closest_point_to(target),
                    #                     game_map,
                    #                     speed=int(hlt.constants.MAX_SPEED),
                    #                     ignore_ships=False)
                    #
                    #         if navigate_command:
                    #             command_queue.append(navigate_command)

                    # #attack!
                    # elif not isinstance(closest_enemy_ships[0], int):
                    #     navigate_command = ship.navigate(
                    #                 ship.closest_point_to(closest_enemy_ships[0]),
                    #                 game_map,
                    #                 speed=int(hlt.constants.MAX_SPEED),
                    #                 ignore_ships=False)
                    #
                    #     if navigate_command:
                    #         command_queue.append(navigate_command)




                # FIND AND MINE AN EMPTY PLANET #
                elif np.argmax(output_vector) == 2: #[0,0,1,0]
                    '''
                    type: 2
                    Mine an empty planet.
                    '''
                    if not isinstance(closest_empty_planets[0], int):
                        target =  closest_empty_planets[0]

                        if ship.can_dock(target):
                            command_queue.append(ship.dock(target))
                        else:
                            navigate_command = ship.navigate(
                                        ship.closest_point_to(target),
                                        game_map,
                                        speed=int(hlt.constants.MAX_SPEED),
                                        ignore_ships=False)

                            if navigate_command:
                                command_queue.append(navigate_command)


                    # else:
                    #     #attack!
                    #     if not isinstance(closest_enemy_ships[0], int):
                    #         navigate_command = ship.navigate(
                    #                     ship.closest_point_to(closest_enemy_ships[0]),
                    #                     game_map,
                    #                     speed=int(hlt.constants.MAX_SPEED),
                    #                     ignore_ships=False)
                    #
                    #         if navigate_command:
                    #             command_queue.append(navigate_command)




                # IDLE FOR A TURN #
                elif np.argmax(output_vector) == 3: #[0,0,0,1]
                    # Do nothing
                    # Remove plans so that a new action may be chosen next turn
                    try:
                        del ship_plans[ship.id]
                    except:
                        pass

            except Exception as e:
                logging.info(str(e))

            with open("c{}_input.vec".format(VERSION),"a") as f:
                f.write(str( [round(item,3) for item in input_vector] ))
                f.write('\n')

            with open("c{}_out.vec".format(VERSION),"a") as f:
                f.write(str(output_vector))
                f.write('\n')

        except Exception as e:
            logging.info(str(e))

    # Send moves to the server
    game.send_command_queue(command_queue)
    # TURN END
# GAME END
