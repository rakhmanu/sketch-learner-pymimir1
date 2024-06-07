#!/usr/bin/env python3

import sys
import numpy as np
import random as rn
import os

grid_N = 3

roslaunch_command = ""

class grid:
    def __init__(self,rows=0,cols=0):
        self.grid_map = np.array(False)
        self.grid_map.resize(rows,cols)
        self.neighbor_name = ["up", "down", "left", "right"]
        self.start = -1
        self.goal = -1
        self.obstacles = []

    def clear(self):
        for i in range(len(self.grid_map)):
            for j in range(len(self.grid_map[0])):
                self.grid_map[i][j] = False

    def index2ij(self,ind):
        return ind//len(self.grid_map[0]), ind%len(self.grid_map[0])

    def ij2index(self,i,j):
        return i*len(self.grid_map[0]) + j

    def neighbor(self, that, ind):
        i, j = self.index2ij(ind)
        out_ind = -1
        if that == self.neighbor_name[0]:  # up
            if i - 1 >= 0:
                out_ind = self.ij2index(i - 1, j)
        elif that == self.neighbor_name[1]:  # down
            if i + 1 < len(self.grid_map):
                out_ind = self.ij2index(i + 1, j)
        elif that == self.neighbor_name[2]:  # left
            if j - 1 >= 0:
                out_ind = self.ij2index(i, j - 1)
        elif that == self.neighbor_name[3]:  # right
            if j + 1 < len(self.grid_map[0]):
                out_ind = self.ij2index(i, j + 1)
        return out_ind


    def make_str_objects_param(self):
        total_num_of_cells = len(self.grid_map) * len(self.grid_map[0])
        print(total_num_of_cells)
        out_str="  robot - thing \n"
        num_blocks = 1
        for num in range(num_blocks):
            out_str+="      block0" + str(num+1) + " "
        out_str += "- thing \n"
        for n in range(total_num_of_cells):
            out_str+="      pos" + str(n) + " " + "- location" + "\n"
        out_str += ")"
        return out_str


    def make_str_param_grid(self):
        total_num_of_cells = len(self.grid_map) * len(self.grid_map[0])
        out_str=""
        for cell in range(total_num_of_cells):
            out_str+="(grid wp" + str(cell) + ")"
        return out_str

    def make_str_obstacle_param(self):
        out_str = ""
        num_blocks = 1
        for num in range(num_blocks):
            for n in range(len(self.obstacles)):
                out_str += "(at block0" + str(num+1) + " " + "pos" + str(self.obstacles[n]) + ")"
        return out_str

    def make_str_clear_param(self):
        out_str = ""
        for row in range(len(self.grid_map)):
            for col in range(len(self.grid_map[row])):
                cell_ind = self.ij2index(row, col)
                if not self.is_occupied(cell_ind) or cell_ind == self.goal:
                    out_str += "   (clear pos" + str(cell_ind) + ")\n"
        return out_str

    def make_str_nongoal_param(self):
        out_str = ""
        for row in range(len(self.grid_map)):
            for col in range(len(self.grid_map[row])):
                cell_ind = self.ij2index(row, col)
                if cell_ind != self.goal:
                    out_str += "   (is-nongoal pos" + str(cell_ind) + ")\n"
        return out_str


    
    def make_str_connect_param(self):
        out_str = ""
        for row in range(len(self.grid_map)):
            for col in range(len(self.grid_map[row])):
                cell_ind = self.ij2index(row, col)
                for nei_name in self.neighbor_name:
                    nei_candidate = self.neighbor(nei_name, cell_ind)
                    if nei_candidate != -1:
                        # Get direction from neighbor name
                        direction = nei_name
                        out_str += f"   (move-dir pos{cell_ind} pos{nei_candidate} {direction})\n"
        return out_str



    
    def make_str_log(self):
        out_str=""
        delim = ","
        out_str += str(self.start)
        out_str += delim
        out_str += str(self.goal)
        out_str += delim
        for n in range(len(self.obstacles)):
            out_str+=str(self.obstacles[n])
            if(n < (len(self.obstacles)-1)):
                out_str+=delim

        return out_str

    def mark_occupancy(self,ind,b):
        i,j = self.index2ij(ind)
        self.grid_map[i][j] = b

    def is_occupied(self,ind):
        i,j = self.index2ij(ind)
        return self.grid_map[i][j]

    def set_start_ind(self):
        num_of_cells = len(self.grid_map) * len(self.grid_map[0])
        start_ind = -1
        while(start_ind == -1):
            start_candidate = rn.randint(0,num_of_cells-1)
            if(self.is_occupied(start_candidate) != True):
                start_ind = start_candidate
                #set
                self.start = start_ind
                #mark as occupied
                self.mark_occupancy(start_ind,True)

    def set_goal_ind(self):
        num_of_cells = len(self.grid_map) * len(self.grid_map[0])
        goal_ind = -1
        while(goal_ind == -1):
            goal_candidate = rn.randint(0,num_of_cells-1)
            if(self.is_occupied(goal_candidate) != True):
                goal_ind = goal_candidate
                #set
                self.goal = goal_ind
                #mark as occupied
                self.mark_occupancy(goal_ind,True)

    def set_obstacles(self, n_of_obs):
        num_of_cells = len(self.grid_map) * len(self.grid_map[0])
        obstacles_ind = []
        while(len(obstacles_ind) != n_of_obs):
            obs_candidate = rn.randint(0,num_of_cells-1)
            if(self.is_occupied(obs_candidate) != True):
                #add to obstables list
                obstacles_ind.append(obs_candidate)
                #mark as occupied
                self.mark_occupancy(obs_candidate,True)

        self.obstacles = sorted(obstacles_ind)

    def make_str_complete(self):
        out_str = "(define (problem p01)\n  (:domain ulzhal)\n"
        out_str +="(:objects \n"
        out_str += "      " + "down - direction \n"
        out_str += "      " + "left - direction \n"
        out_str += "      " + "right - direction \n"
        out_str += "      " + "up - direction \n"
        out_str += "    " + self.make_str_objects_param() + "\n"
        out_str += " (:init\n"
        out_str += "   (at robot pos" + str(self.start) + ")\n"
        out_str += "   " + self.make_str_obstacle_param() + "\n"
        out_str += self.make_str_clear_param() + "\n"
        out_str += "   (is-goal pos" + str(self.goal) + ")\n"
        out_str += self.make_str_nongoal_param() + "\n"
        out_str += "   (is-agent robot" + ")\n"
        num_blocks = 1
        for num in range(num_blocks):
            out_str+="   (is-block block0" + str(num+1) + ")"+ "\n"
        out_str += self.make_str_connect_param() #includes indent and line
        out_str += " " + ")\n"
        num_blocks = 1
        for num in range(num_blocks):
            out_str += " " + "(:goal (and (at-goal block0" + str(num+1) + ") ))\n"
        out_str += ")"
        return out_str

      

def modify_pddl_random(map,n_obj,pddl_file):
    map.clear()
    #generate grid parameters string
    print(map.make_str_objects_param())
    print(map.make_str_param_grid())

    #pick start
    map.set_start_ind()
    #pick goal
    map.set_goal_ind()
    #pick obstacles
    map.set_obstacles(n_obj)

    #print("robot: " + str(map.start))
    #print("goal: " + str(map.goal))
    #print("obstacles : ", map.obstacles)
    #print(map.grid_map)

    pddl_content = map.make_str_complete()
    print(pddl_content)

    f = open(pddl_file, "w")
    f.write(pddl_content)
    f.close()

    return map


def run_terminal(cmd):
    return os.system(cmd)

class parameter_set:
    def __init__(self,file=""):
        self.min_obs_n = -1
        self.max_obs_n = -1
        self.repeat_n = -1
        self.gird_row = -1
        self.grid_col = -1
        self.pddl_file = ""
        self.change_gazebo = ""
        self.run_cmd = ""
        if(file!=""):
            with open(file) as f:
                lines = f.read().splitlines()
            for line in lines:
                temp = line.split(":")
                if(temp[0] == "min_obs_n"):
                    self.min_obs_n = int(temp[1])
                elif(temp[0] == "max_obs_n"):
                    self.max_obs_n = int(temp[1])
                elif(temp[0] == "repeat_n"):
                    self.repeat_n = int(temp[1])
                elif(temp[0] == "grid_row"):
                    self.gird_row = int(temp[1])
                elif(temp[0] == "grid_col"):
                    self.grid_col = int(temp[1])
                elif(temp[0] == "pddl_file"):
                    self.pddl_file = temp[1]
                elif(temp[0] == "change_gazebo"):
                    self.change_gazebo = temp[1]
                elif(temp[0] == "run_cmd"):
                    self.run_cmd = temp[1]
                else:
                    #unknown parameter
                    print("unknown parameter name")


#read parameters from file
param_file_name = "parameters.csv"
print("Read Parameters from File: " + param_file_name)
param_set = parameter_set(param_file_name)

#grid_N = int(sys.argv[1])
grid_N = param_set.gird_row
grid_S = param_set.grid_col
# Before using grid_N and grid_S
print("Grid parameters:")
print("grid_N:", grid_N)
print("grid_S:", grid_S)
print("Generating Grid with "+ str(grid_N) +" Rows and "+ str(grid_S)+" Cols")
map = grid(grid_N, grid_S)


log_list = []
min_obstacle = param_set.min_obs_n
max_obstacle = param_set.max_obs_n
n_repeat = param_set.repeat_n

# Function to modify PDDL and write problem files
def generate_problem_instances(map, param_set):
    log_list = []
    min_obstacle = param_set.min_obs_n
    max_obstacle = param_set.max_obs_n
    n_repeat = param_set.repeat_n

    for obs in range(min_obstacle, max_obstacle + 1):  # Adjusted range to include max_obstacle
        for repeat in range(n_repeat):
            modified_map = modify_pddl_random(map, obs, param_set.pddl_file)
	
            # Construct problem filename
            pddl_filename = f"problem_{obs}_{repeat + 1}_{param_set.grid_col}_{param_set.gird_row}.pddl"

            # Write modified PDDL to file
            with open(pddl_filename, 'w') as f:
                f.write(modified_map.make_str_complete())

            # Append log
            log_list.append(modified_map.make_str_log())

    # Write logs to a file
    with open('log.csv', 'w') as f:
        for string_log in log_list:
            f.write("%s\n" % string_log)

    print("Problem generation is completed")

# Modify PDDL and write problem files
map = grid(param_set.gird_row, param_set.grid_col)
generate_problem_instances(map, param_set)


