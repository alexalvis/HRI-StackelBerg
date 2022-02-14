# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 11:23:35 2021

@author: 53055
"""

from mip import *
import numpy as np
import pickle

def LinearProgramming(S, A, B, P, F, R1, R2, c, v1_0, k, gamma = 0.85):
    model = Model(solver_name = CBC)
    x_len = len(S)
    v1 = [model.add_var() for i in range(x_len)]
    v2 = [model.add_var() for i in range(x_len)]
    pi_1 = [[model.add_var(var_type=BINARY) for j in range(len(A[i]))] for i in range(x_len)]
    d = [[model.add_var(var_type=BINARY) for j in range(len(B[i]))] for i in range(x_len)]
    w = [[[model.add_var() for b in range(len(B[i]))] for a in range(len(A[i]))]for i in range(x_len)]
    z = [[[model.add_var() for b in range(len(B[i]))] for a in range(len(A[i]))]for i in range(x_len)]
    
    Z = 10000
    model.objective = minimize(xsum(c[i] * v2[i] for i in range(x_len)))
    
    for i in range(x_len):
        model += xsum(pi_1[i][j] for j in range(len(A[i]))) == 1
        
    for i in range(x_len):
        model += xsum(d[i][j] for j in range(len(B[i]))) == 1
        
    for i in range(x_len):
        if i not in F:
            for a in range(len(A[i])):
                for b in range(len(B[i])):
                    model += w[i][a][b] >= xsum(v2[s_] * pro for s_, pro in P[i][(a, b)].items()) - Z * (1-d[i][b])
                    model += w[i][a][b] <= xsum(v2[s_] * pro for s_, pro in P[i][(a, b)].items()) + Z * (1-d[i][b])
                    model += w[i][a][b] <= Z * d[i][b]
                    model += w[i][a][b] >= -Z * d[i][b]
    
    for i in range(x_len):
        if i not in F:
            for a in range(len(A[i])):
                for b in range(len(B[i])):
                    model += z[i][a][b] >= xsum(v1[s_] * pro for s_, pro in P[i][(a, b)].items()) - Z * (1-d[i][b])
                    model += z[i][a][b] <= xsum(v1[s_] * pro for s_, pro in P[i][(a, b)].items()) + Z * (1-d[i][b])
                    model += z[i][a][b] <= Z * d[i][b]
                    model += z[i][a][b] >= -Z * d[i][b]
                    
    for i in F:
        model += v1[i] == 0
        model += v2[i] == 0

        
    for i in F:
        model += d[i][0] == 1
        model += pi_1[i][0] == 1
        for a in range(len(A[i])):
            for b in range(len(B[i])):
                model += w[i][a][b] == 0 * d[i][b]
                model += z[i][a][b] == 0 * d[i][b]
                
    for i in range(x_len):
        if i not in F:
            for a in range(len(A[i])):
                model += (xsum((R2[i][b] * d[i][b] + gamma * w[i][a][b]) for b in range(len(B[i]))) - v2[i]) <= (1 - pi_1[i][a]) * Z
                model += (xsum((R1[i][a] * d[i][b] + gamma * z[i][a][b]) for b in range(len(B[i]))) - v1[i]) <= (1 - pi_1[i][a]) * Z
                model += (xsum((R1[i][a] * d[i][b] + gamma * z[i][a][b]) for b in range(len(B[i]))) - v1[i]) >= 0
    
#    v1_limit = 0
#    for i in range(x_len):
#        v1_limit += c[i] * v1_0[i]
    
#    model += xsum(c[i] * v1[i] for i in range(x_len)) <= v1_limit
    
    model += xsum(d[i][0] for i in range(x_len)) >= k
    print("Start optimization")
#    model.max_gap = 0.05
#    model.infeas_tol = 0.000001
    status = model.optimize(max_seconds= 3600)   # Set the maximal calculation time
    print("Finish optimization")
    print(status)
    robot_res = {}
    human_res = {}
    for i in range(x_len):
        for index_b in range(len(B[i])):
            if d[i][index_b].x == 1:
                robot_res[i] = index_b    
        
    for i in range(x_len):
        for index_a in range(len(A[i])):
            if pi_1[i][index_a].x == 1:
                human_res[i] = index_a
                
    v1_0 = []
    for i in range(x_len):
        v1_0.append(v1[i].x)
    
    print("The model objective is:", model.objective_value)
    print("Robot policy: ", robot_res)
    print("Human policy: ", human_res)
    print("The human's cost is: ", v1[3].x)
    return robot_res, human_res, v1_0

if __name__ == "__main__":
    with open("S_small_ns_novice.pkl", "rb") as f:
        S = pickle.load(f)
    with open("A_small_ns_novice.pkl", "rb") as f:
        A = pickle.load(f)
    with open("B_small_ns_novice.pkl", "rb") as f:
        B = pickle.load(f)
    with open("P_small_ns_novice.pkl", "rb") as f:
        P = pickle.load(f)
    with open("F_small_ns_novice.pkl", "rb") as f:
        F = pickle.load(f)
    with open("R1_small_ns_novice.pkl", "rb") as f:
        R1 = pickle.load(f)
    with open("R2_small_ns_novice.pkl", "rb") as f:
        R2 = pickle.load(f)
    with open("c_small_ns_novice.pkl", "rb") as f:
        c = pickle.load(f)
    with open("v1_0.pkl", "rb") as f:
        v1_0 = pickle.load(f)
        
    k = 14
    
    robot_res, human_res, v1_0 = LinearProgramming(S, A, B, P, F, R1, R2, c, k, v1_0)
    
    filename_d = "d_robot_ns.pkl"
    file = open(filename_d, "wb")
    pickle.dump(robot_res, file)
    file.close()
    
    filename_pi_1 = "pi_1_small_ns.pkl"
    file = open(filename_pi_1, "wb")
    pickle.dump(human_res, file)
    file.close()
    
#    filename_v1_0 = "v1_0.pkl"
#    file = open(filename_v1_0, "wb")
#    pickle.dump(v1_0, file)
#    file.close()