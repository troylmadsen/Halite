#!/usr/bin/env python

import os
import time

ship_requirement = 10
damage_requirement = 1000

iterations = 1


def get_ships(data):
    return int(data.split("producing ")[1].split(" ships")[0])

def get_damage(data):
    return int(data.split("dealing ")[1].split(" damage")[0])

def get_rank(data):
    return int(data.split("rank #")[1].split(" and")[0])

player_1_wins = 0
player_2_wins = 0

for num in range(iterations):
    try:
        print("Currently on: {}".format(num))
        if player_1_wins > 0 or player_2_wins > 0:
            p1_pct = round(player_1_wins/(player_1_wins+player_2_wins)*100.0, 2)
            p2_pct = round(player_2_wins/(player_1_wins+player_2_wins)*100.0, 2)
            print("Player 1 win: {}%; Player 2 win: {}%.".format(p1_pct, p2_pct))

        os.system('halite.exe -d "360 240" "python MyBot-1.py" "python MyBot-2.py" >> data.gameout')

        with open('data.gameout', 'r') as f:
            contents = f.readlines()
            Bot1 = contents[-4]
            Bot2 = contents[-3]
            print(Bot1)
            print(Bot2)

            Bot1_ships = get_ships(Bot1)
            Bot1_dmg = get_damage(Bot1)
            Bot1_rank = get_rank(Bot1)

            Bot2_ships = get_ships(Bot2)
            Bot2_dmg = get_damage(Bot2)
            Bot2_rank = get_rank(Bot2)

            print("Bot1 rank: {} ships: {} dmg: {}".format(Bot1_rank,Bot1_ships,Bot1_dmg))
            print("Bot2 rank: {} ships: {} dmg: {}".format(Bot2_rank,Bot2_ships,Bot2_dmg))

        if Bot1_rank == 1:
            print("c1 won")
            player_1_wins += 1
            if Bot1_ships >= ship_requirement and Bot1_dmg >= damage_requirement:
                with open("c1_input.vec","r") as f:
                    input_lines = f.readlines()
                with open("train.in","a") as f:
                    for l in input_lines:
                        f.write(l)

                with open("c1_out.vec","r") as f:
                    output_lines = f.readlines()
                with open("train.out","a") as f:
                    for l in output_lines:
                        f.write(l)

        elif Bot2_rank == 1:
            print("c2 won")
            player_2_wins += 1
            if Bot2_ships >= ship_requirement and Bot2_dmg >= damage_requirement:
                with open("c2_input.vec","r") as f:
                    input_lines = f.readlines()
                with open("train.in","a") as f:
                    for l in input_lines:
                        f.write(l)

                with open("c2_out.vec","r") as f:
                    output_lines = f.readlines()
                with open("train.out","a") as f:
                    for l in output_lines:
                        f.write(l)

        time.sleep(2)
    except Exception as e:
        print(str(e))
        time.sleep(2)
