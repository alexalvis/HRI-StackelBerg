# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 14:53:47 2021

@author: 53055
"""
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 13:36:42 2021

@author: 53055
"""

import numpy as np
import pickle

def StateSpace():
    pos_arm = [0, 1]
    pos_light = [-1, 0, 1]
    pos_heavy = [-1, 0, 1]
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
    F.append(S.index((0, 1, 1)))
    F.append(S.index((1, 1, 1)))
    return F

#def ActionSpace(S):
#    A_H = []
#    A_R = []
#    for i in range(len(S)):
#        if S[i][1] == -1 or S[i][2] == -1:
#            A_H.append(["M_R_S", "M_R_L", "Place"])
#            A_R.append(["lambda", "help"])
#        elif S[i][1] == S[i][2] and S[i][0] == S[i][1]:
#            A_H.append(["Pick_L", "Pick_H"])
#            A_R.append(["lambda", "help"])
#        elif S[i][1] == S[i][0] and S[i][0] != S[i][2]:
#            A_H.append(["M_L", "M_R", "Pick_L"])
#            A_R.append(["lambda", "help"])
#        elif S[i][2] == S[i][0] and S[i][0] != S[i][1]:
#            A_H.append(["M_L", "M_R", "Pick_H"])
#            A_R.append(["lambda", "help"])
#        elif S[i][0] != S[i][1] and S[i][0] != S[i][2]:
#            A_H.append(["M_L", "M_R"])
#            A_R.append(["lambda"])
#    return A_H, A_R
    
def ActionSpace(S):
    A_H = []
    A_R = []
    for i in range(len(S)):
#        A_H.append(["Stay"])
        A_H.append([])
        A_R.append(["lambda"])
    for i in range(len(S)):
        s = S[i]
        if s[0] == 0 and (s[1] == -1 or s[2] == -1):
            #Human action
            A_H[i].append("Move_to_1_S")
            A_H[i].append("Move_to_1_L")
            A_H[i].append("Place")
            #Robot action
            A_R[i].append("help")
        if s[0] == 0 and (s[1] == 0 and s[2] == 0):
            #Human action
#            A_H[i].append("Move_to_1")
            A_H[i].append("Pick_up_L")
            A_H[i].append("Pick_up_H")
            #Robot action
            A_R[i].append("help")
            
        if s[0] == 0 and (s[1] == 0 and s[2] == 1):
            #Human action
#            A_H[i].append("Move_to_1")
            A_H[i].append("Pick_up_L")
            #Robot action
            A_R[i].append("help")
            
        if s[0] == 0 and (s[1] == 1 and s[2] == 0):
            #Human action
#            A_H[i].append("Move_to_1")
            A_H[i].append("Pick_up_H")
            #Robot action
            A_R[i].append("help")
        
        if s[0] == 0 and (s[1] == 1 and s[2] == 1):
            A_H[i].append("Exit")
            
        if s[0] == 1 and (s[1] == -1 or s[2] == -1):
            #Human action
            A_H[i].append("Move_to_0_S")
            A_H[i].append("Move_to_0_L")
            A_H[i].append("Place")
            #Robot action
            A_R[i].append("help")
            
        if s[0] == 1 and (s[1] == 0 and s[2] == 0):
            #Human action
            A_H[i].append("Move_to_0")
            #Robot action
            A_R[i].append("help")
        
        if s[0] == 1 and (s[1] == 0 and s[2] == 1):
            #Human action
            A_H[i].append("Move_to_0")
            A_H[i].append("Pick_up_H")
            #Robot action
            A_R[i].append("help")
            
        if s[0] == 1 and (s[1] == 1 and s[2] == 0):
            #Human action
            A_H[i].append("Move_to_0")
            A_H[i].append("Pick_up_L")
            #Robot action
            A_R[i].append("help")
        
        if s[0] == 1 and (s[1] == 1 and s[2] == 1):
            #Game end
            A_H[i].append("Exit")
        
    return A_H, A_R
            
        
def Cost(h = 25):
    Cost_H = {}
    Cost_R = {}
    Cost_H["Move_to_0"] = 30
    Cost_H["Move_to_1"] = 30
    Cost_H["Pick_up_L"] = 40
    Cost_H["Pick_up_H"] = 45
    Cost_H["Move_to_1_S"] = 40
    Cost_H["Move_to_1_L"] = 45
    Cost_H["Move_to_0_S"] = 40
    Cost_H["Move_to_0_L"] = 45
    Cost_H["Place"] = 30
#    Cost_H["Stay"] = 25
    Cost_R["lambda"] = 20
    Cost_R["help"] = h
    Cost_H["Exit"] = 0
    
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

def CalTransit(S, s, a_h, a_r, l_p = 0.5, h_p = 0.4, bias_h = 0.1, bias_r = 0.2):
    Trans = {}
    pos_a = s[0]
    pos_l = s[1]
    pos_h = s[2]
    if a_h == "Stay":
        Trans[S.index(s)] = 1.0
        return Trans
    
    if a_h == "Place":
        if pos_l == -1:
            tempst = (pos_a, pos_a, pos_h)
            Trans[S.index(tempst)] = 1.0
        else:
            tempst = (pos_a, pos_l, pos_a)
            Trans[S.index(tempst)] = 1.0
        return Trans
    
    if a_h == "Move_to_0":
        tempst = (0, pos_l, pos_h)
        Trans[S.index(tempst)] = 1.0
        return Trans
    
    if a_h == "Move_to_1":
        tempst = (1, pos_l, pos_h)
        Trans[S.index(tempst)] = 1.0
        return Trans
    
    if a_h == "Pick_up_L":
        if a_r == "lambda":
            tempst = (pos_a, -1, pos_h)
            Trans[S.index(tempst)] = l_p
            Trans[S.index(s)] = 1 - l_p
        elif a_r == "help":
            tempst = (pos_a, -1, pos_h)
            Trans[S.index(tempst)] = l_p + bias_r
            Trans[S.index(s)] = 1 - (l_p + bias_r)
        return Trans
    
    if a_h == "Pick_up_H":
        if a_r == "lambda":
            tempst = (pos_a, pos_l, -1)
            Trans[S.index(tempst)] = h_p
            Trans[S.index(s)] = 1 - h_p
        elif a_r == "help":
            tempst = (pos_a, pos_l, -1)
            Trans[S.index(tempst)] = h_p + bias_r
            Trans[S.index(s)] = 1 - (h_p + bias_r)
        return Trans
    
    if a_h == "Move_to_1_S":
        if pos_l == -1:
            if a_r == "lambda":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p
                Trans[S.index((1, s[0], pos_h))] = 1 - l_p
            elif a_r == "help":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p + bias_r
                Trans[S.index((1, s[0], pos_h))] = 1 - (l_p + bias_r)
        elif pos_h == -1:
            if a_r == "lambda":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p
                Trans[S.index((1, pos_l, s[0]))] = 1 - h_p
            elif a_r == "help":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p + bias_r
                Trans[S.index((1, pos_l, s[0]))] = 1 - (h_p + bias_r)
        return Trans
                
    if a_h == "Move_to_1_L":
        if pos_l == -1:
            if a_r == "lambda":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p + bias_h
                Trans[S.index((1, s[0], pos_h))] = 1 - (l_p + bias_h)
            elif a_r == "help":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p + bias_r + bias_h
                Trans[S.index((1, s[0], pos_h))] = 1 - (l_p + bias_r + bias_h)
        elif pos_h == -1:
            if a_r == "lambda":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p + bias_h
                Trans[S.index((1, pos_l, s[0]))] = 1 - (h_p + bias_h)
            elif a_r == "help":
                tempst = (1, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p + bias_r + bias_h
                Trans[S.index((1, pos_l, s[0]))] = 1 - (h_p + bias_r + bias_h)
        return Trans
                
    if a_h == "Move_to_0_S":
        if pos_l == -1:
            if a_r == "lambda":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p
                Trans[S.index((0, s[0], pos_h))] = 1 - l_p
            elif a_r == "help":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p + bias_r
                Trans[S.index((0, s[0], pos_h))] = 1 - (l_p + bias_r)
        elif pos_h == -1:
            if a_r == "lambda":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p
                Trans[S.index((0, pos_l, s[0]))] = 1 - h_p
            elif a_r == "help":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p + bias_r
                Trans[S.index((0, pos_l, s[0]))] = 1 - (h_p + bias_r)
        return Trans
                
    if a_h == "Move_to_0_L":
        if pos_l == -1:
            if a_r == "lambda":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p + bias_h
                Trans[S.index((0, s[0], pos_h))] = 1 - (l_p + bias_h)
            elif a_r == "help":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = l_p + bias_r + bias_h
                Trans[S.index((0, s[0], pos_h))] = 1 - (l_p + bias_r + bias_h)
        elif pos_h == -1:
            if a_r == "lambda":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p + bias_h
                Trans[S.index((0, pos_l, s[0]))] = 1 - (h_p + bias_h)
            elif a_r == "help":
                tempst = (0, pos_l, pos_h)
                Trans[S.index(tempst)] = h_p + bias_r + bias_h
                Trans[S.index((0, pos_l, s[0]))] = 1 - (h_p + bias_r + bias_h)
        return Trans
                
    if a_h == "Exit":
        Trans[S.index(s)] = 1.0
        return Trans
        
        
        
            
#def CalTransit(S, s, a_h, a_r, l_p = 0.8, h_p = 0.6, bias_h = 0.1, bias_r = 0.1):
#    Trans = {}
#    pos_a = s[0]
#    pos_l = s[1]
#    pos_h = s[2]
#    if a_h == "M_R_S":
#        pos_a += 1
#        if pos_a > 1:
#            Trans[S.index(s)] = 1.0
#            return Trans
#        else:     
#            if pos_l == -1:
#                if a_r == "lambda":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p
#                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - l_p
#                    return Trans
#                elif a_r == "help":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p + bias_r
#                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - (l_p + bias_r)
#                    return Trans
#            else:
#                if a_r == "lambda":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p
#                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - h_p
#                    return Trans
#                elif a_r == "help":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p + bias_r
#                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - (h_p + bias_r)
#                    return Trans
#                    
#    if a_h == "M_R_L":
#        pos_a += 1
#        if pos_a > 1:
#            Trans[S.index(s)] = 1.0
#            return Trans
#        else:
#            if pos_l == -1:
#                if a_r == "lambda":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p + bias_h
#                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - (l_p + bias_h)
#                    return Trans
#                elif a_r == "help":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = l_p + bias_r + bias_h
#                    Trans[S.index((pos_a, s[0], pos_h))] = 1 - (l_p + bias_r + bias_h)
#                    return Trans
#            else:
#                if a_r == "lambda":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p + bias_h
#                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - (h_p + bias_h)
#                    return Trans
#                elif a_r == "help":
#                    Trans[S.index((pos_a, pos_l, pos_h))] = h_p + bias_r + bias_h
#                    Trans[S.index((pos_a, pos_l, s[0]))] = 1 - (h_p + bias_r + bias_h)
#                    return Trans
#                
#    if a_h == "M_L":
#        pos_a -= 1
#        if pos_a < 0:
#            Trans[S.index(s)] = 1.0
#            return Trans
#        else:
#            Trans[S.index((pos_a, pos_l, pos_h))] = 1.0
#            return Trans
#        
#    if a_h == "M_R":
#        pos_a += 1
#        if pos_a > 1:
#            Trans[S.index(s)] = 1.0
#            return Trans
#        else:
#            Trans[S.index((pos_a, pos_l, pos_h))] = 1.0
#            return Trans
#    
#    if a_h == "Place":
#        if pos_l == -1:
#            Trans[S.index((pos_a, pos_a, pos_h))] = 1.0
#        elif pos_h == -1:
#            Trans[S.index((pos_a, pos_l, pos_a))] = 1.0
#        return Trans
#    
#    if a_h == "Pick_L":
#        if a_r == "lambda":
#            Trans[S.index((pos_a, -1, pos_h))] = l_p
#            Trans[S.index(s)] = 1 - l_p
#        elif a_r == "help":
#            Trans[S.index((pos_a, -1, pos_h))] = l_p + bias_r
#            Trans[S.index(s)] = 1 - (l_p + bias_r)
#        return Trans
#            
#    if a_h == "Pick_H":
#        if a_r == "lambda":
#            Trans[S.index((pos_a, pos_l, -1))] = h_p
#            Trans[S.index(s)] = 1 - h_p
#        elif a_r == "help":
#            Trans[S.index((pos_a, pos_l, -1))] = h_p + bias_r
#            Trans[S.index(s)] = 1 - (h_p + bias_r)
#        return Trans
    
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
                
def policy_evaluation(S, pi_1, d, F):
    gamma = 0.85
    V1 = {}
    V2 = {}
    for s in S:
        s_index = S.index(s)
        if s_index not in F:
            V1[s_index] = 0
            V2[s_index] = 0
        elif S.index(s) in F:
            V1[s_index] = 0
            V2[s_index] = 0
    itercount = 0
    while True:
        b = 0
        itercount += 1
        V1_ = V1.copy()
        V2_ = V2.copy()
        delta1 = 0
        delta2 = 0
        print(itercount)
        for s in S:
            s_index = S.index(s)
            if s_index not in F:
                a = pi_1[s_index]
                b = d[s_index]
                Pro = P[s_index][(a, b)]
                V1[s_index] = R_H[s_index][a] + gamma * sum(Pro[next_s] * V1_[next_s] for next_s in Pro.keys())
                V2[s_index] = R_R[s_index][b] + gamma * sum(Pro[next_s] * V2_[next_s] for next_s in Pro.keys())
                delta1 = max(delta1, abs(V1[s_index] - V1_[s_index]))
                delta2 = max(delta2, abs(V2[s_index] - V2_[s_index]))
            elif s_index in F:
                V1[s_index] = 0
                V2[s_index] = 0

        if delta1 < 0.0001 * (1 - gamma) / gamma and delta2 < 0.0001 * (1 - gamma) / gamma:
            return V1, V2
if __name__ == "__main__":
    S = StateSpace()
    F = FinalState(S)
    c = initState(S)
    A_H, A_R = ActionSpace(S)
    Cost_H, Cost_R = Cost()
    R_H, R_R = Reward(A_H, A_R, Cost_H, Cost_R)
    P = Transition(S, F, A_H, A_R)
    testP(P)
#    with open("d_robot_ns.pkl", "rb") as f:
#        d = pickle.load(f)
#    with open("pi_1_small_ns.pkl", "rb") as f:
#        pi_1 = pickle.load(f)
#    V1, V2 = policy_evaluation(S, pi_1, d, F)
#    print(V1[3], V2[3])
    
    filename_S = "S_small_ns_novice.pkl"
    file = open(filename_S, "wb")
    pickle.dump(S, file)
    file.close()
#    
    filename_A = "A_small_ns_novice.pkl"
    file = open(filename_A, "wb")
    pickle.dump(A_H, file)
    file.close()
#    
    filename_B = "B_small_ns_novice.pkl"
    file = open(filename_B, "wb")
    pickle.dump(A_R, file)
    file.close()
#    
    filename_P = "P_small_ns_novice.pkl"
    file = open(filename_P, "wb")
    pickle.dump(P, file)
    file.close()
#    
    filename_F = "F_small_ns_novice.pkl"
    file = open(filename_F, "wb")
    pickle.dump(F, file)
    file.close()
#    
#    
    filename_R1 = "R1_small_ns_novice.pkl"
    file = open(filename_R1, "wb")
    pickle.dump(R_H, file)
    file.close()
#    
    filename_R2 = "R2_small_ns_novice.pkl"
    file = open(filename_R2, "wb")
    pickle.dump(R_R, file)
    file.close()
#    
    filename_c = "c_small_ns_novice.pkl"
    file = open(filename_c, "wb")
    pickle.dump(c, file)
    file.close()
#    
                
            
            
                    
