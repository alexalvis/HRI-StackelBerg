# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 14:45:32 2021

@author: 53055
"""

import pickle
import numpy as np

def test(p1, p2):
    for s in p1.keys():
        if s != "Fail":
            for act in p1[s].keys():
                if act not in p2[s].keys():
                    print(s)
    print("p1 and p2 are same")
    
def check_LP(S, A, B, P, F, R1, R2, V1, V2, policy):
    w = np.zeros((len(S), len(A), len(B)))
    z = np.zeros((len(S), len(A), len(B)))
    b = 0
    B_len = len(B)
    A_len = len(A)
    S_len = len(S)
    Z = 100000
    gamma = 0.95
    for i in range(S_len):
        if i not in F:
            for act in policy[S[i]].keys():
                a = act
            w[i][a][b] = sum(V2[s_] * pro for s_, pro in P[i][(a, b)].items())
            z[i][a][b] = sum(V1[s_] * pro for s_, pro in P[i][(a, b)].items())

    pi_1 = {}
    for i in range(S_len):
        if i not in F:
            pi_1[i] = {}
            for a in range(A_len):
                if a in policy[S[i]].keys():
                    pi_1[i][a] = 1
                else:
                    pi_1[i][a] = 0
                    
    d = {}
    for i in range(S_len):
        if i not in F:
            d[i] = {}
            for b in range(B_len):
                if b == 0:
                    d[i][b] = 1
                else:
                    d[i][b] = 0
        
    for i in range(S_len):
        if i not in F:
            for a in range(A_len):
                error1 = V1[i] - sum((R1[i][a][b] * d[i][b] + gamma * z[i][a][b]) for b in range(B_len))
                print(error1)
                if  error1 < 0:
                    print("violate 3d_1, state index: ", i, "error is: ", error1)
 
                if V1[i] - sum((R1[i][a][b] * d[i][b] + gamma * z[i][a][b]) for b in range(B_len)) > (1 - pi_1[i][a]) * Z:  
                    print("violate 3d_2, state index: ", i)
                    
                if V2[i] - sum((R2[i][a][b] * d[i][b] + gamma * w[i][a][b]) for b in range(B_len)) > (1 - pi_1[i][a]) * Z:
                    print("violate 3e, state index: ", i)
            
            


                
if __name__ == "__main__":
#    with open("policy.pkl", "rb") as f:
#        p1 = pickle.load(f)
#    with open("policy_revise.pkl", "rb") as f:
#        p2 = pickle.load(f)
#    test(p1, p2)
    with open("S_small.pkl", "rb") as f:
        S = pickle.load(f)
    with open("A_small.pkl", "rb") as f:
        A = pickle.load(f)
    with open("B_small.pkl", "rb") as f:
        B = pickle.load(f)
    with open("P_small.pkl", "rb") as f:
        P = pickle.load(f)
    with open("F_small.pkl", "rb") as f:
        F = pickle.load(f)
    with open("R1_small.pkl", "rb") as f:
        R1 = pickle.load(f)
    with open("R2_small.pkl", "rb") as f:
        R2 = pickle.load(f)
    with open("c_small.pkl", "rb") as f:
        c = pickle.load(f)
    with open("V1_small.pkl", "rb") as f:
        V1 = pickle.load(f)
    with open("V2_small.pkl", "rb") as f:
        V2 = pickle.load(f)
    with open("policy_small.pkl", "rb") as f:
        p2 = pickle.load(f)
        
    check_LP(S, A, B, P, F, R1, R2, V1, V2, policy)