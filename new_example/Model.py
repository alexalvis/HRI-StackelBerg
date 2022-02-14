# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 13:36:42 2021

@author: 53055
"""

import numpy as np
import pickle

def StateSpace():
    pos_arm = [0, 1, 2]
    pos_light = [-1, 0, 1, 2]
    pos_heavy = [-1, 0, 1, 2]
    S = []
    for pos_a in pos_arm:
        for pos_l in pos_light:
            for pos_h in pos_heavy:
                if pos_l == -1 and pos_h == -1:
                    pass
                else:
                    S.append((pos_a, pos_l, pos_h))
    return S

def FinalState(S):
    F = []
    F.append(S.index((0, 2, 2)))
    F.append(S.index((1, 2, 2)))
    F.append(S.index((2, 2, 2)))
    return F

def ActionSpace(S):
    A_H = []
    A_R = []
    for i in range(len(S)):
        if S[i][1] == -1 or S[i][2] == -1:
            A_H.append(["M_R_S", "M_R_L", "Place"])
            A_R.append(["lambda", "help"])
        elif S[i][1] == S[i][2] and S[i][0] == S[i][1]:
            A_H.append(["Pick_L", "Pick_H"])
            A_R.append(["lambda", "help"])
        elif S[i][1] == S[i][0] and S[i][0] != S[i][2]:
            A_H.append(["M_L", "M_R", "Pick_L"])
            A_R.append(["lambda", "help"])
        elif S[i][2] == S[i][0] and S[i][0] != S[i][1]:
            A_H.append(["M_L", "M_R", "Pick_H"])
            A_R.append(["lambda", "help"])
        elif S[i][0] != S[i][1] and S[i][0] != S[i][2]:
            A_H.append(["M_L", "M_R"])
            A_R.append(["lambda"])
    return A_H, A_R

def Cost():
    Cost_H = {}
    Cost_R = {}
    Cost_H["M_L"] = -5
    Cost_H["M_R"] = -5
    Cost_H["Pick_L"] = -10
    Cost_H["Pick_H"] = -15
    Cost_H["M_R_S"] = -10
    Cost_H["M_R_L"] = -15
    Cost_H["Place"] = -5
    Cost_R["lambda"] = 0
    Cost_R["help"] = -10
    
    return Cost_H, Cost_R

def Transition(S, F, A_H, A_R):
    P = {}
    for i in range(len(S)):
        s = S[i]
        P[i] = {}
        if s not in F:
            for a in range(len(A_H[i])):
                for b in range(len(A_R[i])):
                    P[i][(a, b)] = CalTransit(S, s, A_H[i][a], A_R[i][b])
        else:
            for a in range(len(A_H[i])):
                for b in range(len(A_R[i])):
                    P[i][(a, b)] = {}
                    P[i][(a, b)][i] = 1.0
    return P

def CalTransit(S, s, a_h, a_r, l_p = 0.8, h_p = 0.6, bias_h = 0.1, bias_r = 0.1):
    Trans = {}
    pos_a = s[0]
    pos_l = s[1]
    pos_h = s[2]
    if a_h == "M_R_S":
        pos_a += 1
        if pos_a > 2:
            Trans[S.index(s)] = 1.0
            return Trans
        else:     
            if pos_l == -1:
                if a_r == "lambda":
                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p
                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - l_p
                    return Trans
                elif a_r == "help":
                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p + bias_r
                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - (l_p + bias_r)
                    return Trans
            else:
                if a_r == "lambda":
                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p
                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - h_p
                    return Trans
                elif a_r == "help":
                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p + bias_r
                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - (h_p + bias_r)
                    return Trans
                    
    if a_h == "M_R_L":
        pos_a += 1
        if pos_a > 2:
            Trans[S.index(s)] = 1.0
            return Trans
        else:
            if pos_l == -1:
                if a_r == "lambda":
                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p + bias_h
                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - (l_p + bias_h)
                    return Trans
                elif a_r == "help":
                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p + bias_r + bias_h
                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - (l_p + bias_r + bias_h)
                    return Trans
            else:
                if a_r == "lambda":
                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p + bias_h
                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - (h_p + bias_h)
                    return Trans
                elif a_r == "help":
                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p + bias_r + bias_h
                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - (h_p + bias_r + bias_h)
                    return Trans
                
    if a_h == "M_L":
        pos_a -= 1
        if pos_a < 0:
            Trans[S.index(s)] = 1.0
            return Trans
        else:
            Trans[S.index((pos_a, pos_l, pos_h))] = 1.0
            return Trans
        
    if a_h == "M_R":
        pos_a += 1
        if pos_a > 2:
            Trans[S.index(s)] = 1.0
            return Trans
        else:
            Trans[S.index((pos_a, pos_l, pos_h))] = 1.0
            return Trans
    
    if a_h == "Place":
        if pos_l == -1:
            Trans[S.index((pos_a, pos_a, pos_h))] = 1.0
        elif pos_h == -1:
            Trans[S.index((pos_a, pos_l, pos_a))] = 1.0
        return Trans
    
    if a_h == "Pick_L":
        if a_r == "lambda":
            Trans[S.index((pos_a, -1, pos_h))] = l_p
            Trans[S.index(s)] = 1 - l_p
        elif a_r == "help":
            Trans[S.index((pos_a, -1, pos_h))] = l_p + bias_r
            Trans[S.index(s)] = 1 - (l_p + bias_r)
        return Trans
            
    if a_h == "Pick_H":
        if a_r == "lambda":
            Trans[S.index((pos_a, pos_l, -1))] = h_p
            Trans[S.index(s)] = 1 - h_p
        elif a_r == "help":
            Trans[S.index((pos_a, pos_l, -1))] = h_p + bias_r
            Trans[S.index(s)] = 1 - (h_p + bias_r)
        return Trans
    
def InitState(S):
    s = (0, 0, 0)
    InitList = []
    InitList.append(S.index(s))
    return InitList

def Reward(A_H, A_R, Cost_H, Cost_R):
    R_H = {}
    R_R = {}
    for i in range(len(A_H)):
        R_H[i] = {}
        R_R[i] = {}
        for a_h_i in range(len(A_H[i])):
            R_H[i][a_h_i] = Cost_H[A_H[i][a_h_i]]
        for a_r_i in range(len(A_R[i])):
            R_R[i][a_r_i] = Cost_R[A_R[i][a_r_i]]
    return R_H, R_R
                

def testP(P):
    for s in P.keys():
        for pro_a in P[s].keys():
            if sum(P[s][pro_a].values()) != 1:
                print(s, pro_a, P[s][pro_a])
                
def initState(S):
    c = np.zeros(len(S))
    c[S.index((0, 0, 0))] = 1.0
    return c
                
if __name__ == "__main__":
    S = StateSpace()
    F = FinalState(S)
    c = initState(S)
    A_H, A_R = ActionSpace(S)
    Cost_H, Cost_R = Cost()
    R_H, R_R = Reward(A_H, A_R, Cost_H, Cost_R)
    P = Transition(S, F, A_H, A_R)
    testP(P)
    
    filename_S = "S_small.pkl"
    file = open(filename_S, "wb")
    pickle.dump(S, file)
    file.close()
#    
    filename_A = "A_small.pkl"
    file = open(filename_A, "wb")
    pickle.dump(A_H, file)
    file.close()
#    
    filename_B = "B_small.pkl"
    file = open(filename_B, "wb")
    pickle.dump(A_R, file)
    file.close()
#    
    filename_P = "P_small.pkl"
    file = open(filename_P, "wb")
    pickle.dump(P, file)
    file.close()
#    
    filename_F = "F_small.pkl"
    file = open(filename_F, "wb")
    pickle.dump(F, file)
    file.close()
#    
#    
    filename_R1 = "R1_small.pkl"
    file = open(filename_R1, "wb")
    pickle.dump(R_H, file)
    file.close()
#    
    filename_R2 = "R2_small.pkl"
    file = open(filename_R2, "wb")
    pickle.dump(R_R, file)
    file.close()
#    
    filename_c = "c_small.pkl"
    file = open(filename_c, "wb")
    pickle.dump(c, file)
    file.close()
    
                
            
            
                    