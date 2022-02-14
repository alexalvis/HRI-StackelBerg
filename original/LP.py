# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 22:23:14 2021

@author: 53055
"""

from mip import *
import numpy as np
import pickle

def LinearProgramming(S, A, B, P, F, Sink, R1, R2, c, gamma = 0.85):
    model = Model()
    
    x_len = len(S)
    A_len = len(A)
    B_len = len(B)
    v1 = [model.add_var() for i in range(x_len)]
    v2 = [model.add_var() for i in range(x_len)]
    pi_1 = [[model.add_var(var_type=BINARY) for j in range(A_len)] for i in range(x_len)]
    #w for robot, z for human
    w = [[[model.add_var() for b in range(B_len)] for a in range(A_len)]for i in range(x_len)]
    z = [[[model.add_var() for b in range(B_len)] for a in range(A_len)]for i in range(x_len)]
    d = [[model.add_var(var_type=BINARY) for j in range(B_len)] for i in range(x_len)]
    Z = 100000
    #Objective
    model.objective = maximize(xsum(c[i] * v2[i] for i in range(x_len)))
    
    #Restriction 1b already specified when we define pi_1
    #Restriction 1c
    for i in range(x_len - 1):
        model += xsum(pi_1[i][j] for j in range(A_len)) == 1
    #Restriction 2a, 2b, 2c for w(robot)
    for i in range(x_len - 1):
        if i not in F:
            for a in range(A_len):
                for b in range(B_len):
                    model += w[i][a][b] >= xsum(v2[s_] * pro for s_, pro in P[i][(a, b)].items()) - Z * (1-d[i][b])
                    model += w[i][a][b] <= xsum(v2[s_] * pro for s_, pro in P[i][(a, b)].items()) + Z * (1-d[i][b])
                    model += w[i][a][b] <= Z * d[i][b]
                    model += w[i][a][b] >= -Z * d[i][b]
                    
    #Similar Restriction 2a, 2b, 2c but for z(human)           
    for i in range(x_len - 1):
        if i not in F:
            for a in range(A_len):
                for b in range(B_len):
                    model += z[i][a][b] >= xsum(v1[s_] * pro for s_, pro in P[i][(a, b)].items()) - Z * (1-d[i][b])
                    model += z[i][a][b] <= xsum(v1[s_] * pro for s_, pro in P[i][(a, b)].items()) + Z * (1-d[i][b])
                    model += z[i][a][b] <= Z * d[i][b]
                    model += z[i][a][b] >= -Z * d[i][b]
                
    #Restriction 3b already specified when we define variable
    #Restriction 3c
    for i in range(x_len - 1):
        model += xsum(d[i][j] for j in range(B_len)) == 1
    
    #Restriction the value of final state and sink state
    for i in F:
        model += v1[i] == 2000
        model += v2[i] == 2000
        
    for i in F:
        for a in range(A_len):
            for b in range(B_len):
                model += w[i][a][b] == 2000 * d[i][b]
                model += z[i][a][b] == 2000 * d[i][b]

                
    
    for i in Sink:
        model += v1[i] == -2000
        model += v2[i] == -2000
        
    for i in Sink:
        for a in range(A_len):
            for b in range(B_len):
                model += w[i][a][b] == -2000 * d[i][b]
                model += z[i][a][b] == -2000 * d[i][b]
        
    #Restriction 3d, 3e
    for i in range(x_len - 1):
        if i not in F:
            for a in range(A_len):
                model += (v2[i] - xsum((R2[i][a][b] * d[i][b] + gamma * w[i][a][b]) for b in range(B_len))) <= (1 - pi_1[i][a]) * Z
                model += (v1[i] - xsum((R1[i][a][b] * d[i][b] + gamma * z[i][a][b]) for b in range(B_len))) <= (1 - pi_1[i][a]) * Z
                model += (v1[i] - xsum((R1[i][a][b] * d[i][b] + gamma * z[i][a][b]) for b in range(B_len))) >= 0
                
    for i in range(x_len):
        model += d[i][0] == 1
    
    print("Start optimization")
#    model.max_gap = 0.05
    status = model.optimize()   # Set the maximal calculation time
    print("Finish optimization")
    print(status)

if __name__ == "__main__":
    with open("S.pkl", "rb") as f:
        S = pickle.load(f)
    with open("A.pkl", "rb") as f:
        A = pickle.load(f)
    with open("B.pkl", "rb") as f:
        B = pickle.load(f)
    with open("P.pkl", "rb") as f:
        P = pickle.load(f)
    with open("F.pkl", "rb") as f:
        F = pickle.load(f)
    with open("Sink.pkl", "rb") as f:
        Sink = pickle.load(f)
    with open("R1.pkl", "rb") as f:
        R1 = pickle.load(f)
    with open("R2.pkl", "rb") as f:
        R2 = pickle.load(f)
    with open("c.pkl", "rb") as f:
        c = pickle.load(f)
    
    LinearProgramming(S, A, B, P, F, Sink, R1, R2, c)
    