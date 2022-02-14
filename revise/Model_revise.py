# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 12:35:51 2021

@author: 53055
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 13:46:24 2021

@author: 53055
"""

import numpy as np
import pickle

def Statespace():
    #s (s_heavy, s_light, s_base, s_arm)
    SB = [0, 1, 2, 3]
    SA = [0, 1, 2, 3, 4, 5, 6, 7]
    Loc_H = [-1, 0, 1, 2, 3, 4, 5, 6, 7]
    Loc_L = [-1, 0, 1, 2, 3, 4, 5, 6, 7]
    L = []
    S = []
    for lh in Loc_H:
        for ll in Loc_L:
            L.append((lh, ll))
    L.remove((-1, -1))
    for sb in SB:
        for sa in range(sb*2-1, sb*2+3):
            for l in L:
                if sa >= 0 and sa <= 7:
                    S.append((l[0], l[1], sb, sa))
    print(len(S))
    return S

def FinalState(S):
    F = []
    for i in range(len(S)):
        if (S[i][0] == 6 or S[i][0] == 7) and (S[i][1] == 6 or S[i][1] == 7):
            print(S[i])
            F.append(i)
    return F

def Actionspace():
    #A is the action set for human, B is the action set for robot 
    A = ["A_ML", "A_MR", "B_ML", "B_MR", "Pick_H", "Pick_L", "Place"]
    B = ["lambda", "B_ML", "B_MR"]
    Product_A = {}
    for a in A:
        Product_A[a] = []
        if a == "A_ML" or a == "A_MR":
            Product_A[a].append("lambda")
            Product_A[a].append("B_ML")
            Product_A[a].append("B_MR")
        else:
            Product_A[a].append("lambda")
                                
    return A, B, Product_A

def Cost():
    C_A = {}
    C_B = {}
    C_A["A_ML"] = -10
    C_A["A_MR"] = -10
    C_A["B_ML"] = -20
    C_A["B_MR"] = -20
    C_A["Pick_H"] = -5
    C_A["Pick_L"] = -5
    C_A["Place"] = -5
    C_B["B_ML"] = -20
    C_B["B_MR"] = -20
    C_B["lambda"] = 0
    return C_A, C_B

def Transition(S, A, B, Product_A, p_H, p_L):
    #All using index instead of string or tuple
    P = {}
    for s in S:
        s_index = S.index(s)
        P[s_index] = {}
        for a in A:
            a_index = A.index(a)    
            if a in Available_A(s):
                available_B = Product_A[a]
                for b in B:
                    b_index = B.index(b)
                    if b in available_B:
                        P[s_index][(a_index,b_index)] = Cal_Transit(S, s, a, b, p_H, p_L)
                    else:
                        P[s_index][(a_index,b_index)] = {}
                        P[s_index][(a_index,b_index)][s_index] = 1.0
            else:
                for b in B:
                    b_index = B.index(b)
                    P[s_index][(a_index,b_index)] = {}
                    P[s_index][(a_index,b_index)][s_index] = 1.0
    return P

def Cal_Transit(S, s, a, b, p_H, p_L, bias = 0.1):
    Next_State = {}
    sh_ = s[0]
    sl_ = s[1]
    sb_ = s[2]
    sa_ = s[3]
    if a == "A_ML":
        #Control arm place
        if s[3] == 0:
            Next_State[S.index(s)] = 1.0
            return Next_State
        else:
            sa_ -= 1
        #Control base place
        if b == "B_ML":
            if s[2] == 0:
                Next_State[S.index(s)] = 1.0
                return Next_State
            else:
                sb_ = sb_ - 1
                sa_ = sa_ - 2
                if sa_ < 0:
                    Next_State[S.index(s)] = 1.0
                    return Next_State
        elif b == "lambda":
            sb_ = sb_
        else:
            if s[2] == 3:
                Next_State[S.index(s)] = 1.0
                return Next_State
            else:
                sb_ = s[2] + 1
                sa_ = sa_ + 2
                if sa_ > 7:
                    Next_State[S.index(s)] = 1.0
                    return Next_State
        
        #Picking the heavy one and in left/right pos
        if sh_ == -1 and (sa_ == 2 * sb_ - 1 or sa_ == 2 * sb_ + 2):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_H - bias
            Next_State[S.index((s[3], sl_, sb_, sa_))] = 1 - p_H + bias
            return Next_State
        #Picking the heavy one and in middle pos
        if sh_ == -1 and (sa_ == 2 * sb_ or sa_ == 2 * sb_ + 1):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_H
            Next_State[S.index((s[3], sl_, sb_, sa_))] = 1 - p_H
            return Next_State
        #Picking the light one and in left/right pos
        if sl_ == -1 and (sa_ == 2 * sb_ - 1 or sa_ == 2 * sb_ + 2):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_L - bias
            Next_State[S.index((sh_, s[3], sb_, sa_))] = 1 - p_L + bias
            return Next_State
        #Picking the light one and in middle pos
        if sl_ == -1 and (sa_ == 2 * sb_ or sa_ == 2 * sb_ + 1):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_L
            Next_State[S.index((sh_, s[3], sb_, sa_))] = 1 - p_L
            return Next_State
        Next_State[S.index((sh_, sl_, sb_, sa_))] = 1.0
        return Next_State
        
        
    if a == "A_MR":
        #Control arm place
        if s[3] == 7:
            Next_State[S.index(s)] = 1.0
            return Next_State
        else:
            sa_ += 1
        #Control base place
        if b == "B_ML":
            if s[2] == 0:
                Next_State[S.index(s)] = 1.0
                return Next_State
            else:
                sb_ = sb_ - 1
                sa_ = sa_ - 2
                if sa_ < 0:
                    Next_State[S.index(s)] = 1.0
                    return Next_State
        elif b == "lambda":
            sb_ = sb_
        else:
            if s[2] == 3:
                Next_State[S.index(s)] = 1.0
                return Next_State
            else:
                sb_ = sb_ + 1
                sa_ = sa_ + 2
                if sa_ > 7:
                    Next_State[S.index(s)] = 1.0
                    return Next_State
                
        
        #Picking the heavy one and in left/right pos
        if sh_ == -1 and (sa_ == 2 * sb_ - 1 or sa_ == 2 * sb_ + 2):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_H - bias
            Next_State[S.index((s[3], sl_, sb_, sa_))] = 1 - p_H + bias
            return Next_State
        #Picking the heavy one and in middle pos
        if sh_ == -1 and (sa_ == 2 * sb_ or sa_ == 2 * sb_ + 1):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_H
            Next_State[S.index((s[3], sl_, sb_, sa_))] = 1 - p_H
            return Next_State
        #Picking the light one and in left/right pos
        if sl_ == -1 and (sa_ == 2 * sb_ - 1 or sa_ == 2 * sb_ + 2):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_L - bias
            Next_State[S.index((sh_, s[3], sb_, sa_))] = 1 - p_L + bias
            return Next_State
        #Picking the light one and in middle pos
        if sl_ == -1 and (sa_ == 2 * sb_ or sa_ == 2 * sb_ + 1):
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_L
            Next_State[S.index((sh_, s[3], sb_, sa_))] = 1 - p_L
            return Next_State
        
        Next_State[S.index((sh_, sl_, sb_, sa_))] = 1.0
        return Next_State
    #Human choose move base action
    if a == "B_ML":
        if s[2] == 0:
            sb_ = 0
            Next_State[S.index(s)] = 1.0
            return Next_State
        else:
            sb_ -= 1
            sa_ -= 2
            if sa_ < 0:
                Next_State[S.index(s)] = 1.0
            else:
                Next_State[S.index((sh_, sl_, sb_, sa_))] = 1.0
            return Next_State
    if a == "B_MR":
        if s[2] == 3:
            sb_ = 3
            Next_State[S.index(s)] = 1.0
            return Next_State
        else:
            sb_ += 1
            sa_ += 2
            if sa_ > 7:
                Next_State[S.index(s)] = 1.0
            else:
                Next_State[S.index((sh_, sl_, sb_, sa_))] = 1.0
            return Next_State
        
    #Human choose "Pick" action
    if a == "Pick_H":
        if sa_ == 2 * sb_ - 1 or sa_ == 2 * sb_ + 2:
            #in left or right pos
            sh_ = -1
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_H - bias
            Next_State[S.index((s[0], sl_, sb_, sa_))] = 1 - p_H + bias
            return Next_State
        else:
            #in middle pos
            sh_ = -1
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_H
            Next_State[S.index((s[0], sl_, sb_, sa_))] = 1 - p_H
            return Next_State
                
    if a == "Pick_L":
        if sa_ == 2 * sb_ - 1 or sa_ == 2 * sb_ + 2:
            #in left or right pos
            sl_ = -1
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_L - bias
            Next_State[S.index((sh_, s[1], sb_, sa_))] = 1 - p_L + bias
            return Next_State
        else:
            #in middle pos
            sl_ = -1
            Next_State[S.index((sh_, sl_, sb_, sa_))] = p_L
            Next_State[S.index((sh_, s[1], sb_, sa_))] = 1 - p_L
            return Next_State
            
    #Human choose "Place" action
    if a == "Place":
        if sh_ == -1:
            Next_State[S.index((sa_, sl_, sb_, sa_))] = 1.0
            return Next_State
        else:
            Next_State[S.index((sh_, sa_, sb_, sa_))] = 1.0
            return Next_State

def Reward(S, A, B, Cost_A, Cost_B):
    R1 = {}
    R2 = {}
    for i in range(len(S)):
        R1[i] = {}
        R2[i] = {}
        for a in range(len(A)):
            R1[i][a] = {}
            R2[i][a] = {}
            for b in range(len(B)):
                R1[i][a][b] = Cost_A[A[a]]
                R2[i][a][b] = Cost_B[B[b]]
    return R1, R2

def initial_state(S):
    sh = [0, 1]
    sl = [0, 1]
    sb = 1
    sa = 2
    c = np.zeros(len(S))
    initlist = []
    for sh_ in sh:
        for sl_ in sl:
            initlist.append((sh_, sl_, sb, sa))
    for init_st in initlist:
        init_index = S.index(init_st)
        c[init_index] = 1/len(initlist)
    return c

def testP(P):
    for s in P.keys():
        for pro_a in P[s].keys():
            if sum(P[s][pro_a].values()) != 1:
                print(s, sum(P[s][pro_a].values()))

def valueiteration(S, P, F, A, R1):
    gamma = 0.85
    policy = {s : {} for s in S}
    V1 = {}
    for s in S:
        s_index = S.index(s)
        if s_index not in F:
            V1[s_index] = 0
        elif S.index(s) in F:
            V1[s_index] = 2000
    iter_count = 0
    while True:
        b = 0
        iter_count += 1
        print(iter_count)
        V = V1.copy()
        delta = 0
        for s in S:
            s_index = S.index(s)
            if s_index not in F:
                maxV = -10000
                maxaction = None
                for a in range(len(A)):
                    tempV = 0.0
                    Pro = P[s_index][(a,b)]
#                    print(s_index)
#                    print(Pro)
                    tempV = R1[s_index][a][b] + gamma * sum(Pro[s] * V[s] for s in Pro.keys())
                    if tempV >= maxV:
                        maxV = tempV
                        maxaction = a
                        # print(s, maxV)
                V1[s_index] = maxV
                policy[s] = {}
                policy[s][maxaction] = 1.0
                delta = max(delta, abs(V1[s_index] - V[s_index]))
            elif s_index in F:
                V[s_index] = 2000
                policy[s]["Exit"] = 1.0
        if delta < 0.0001 * (1 - gamma) / gamma:
            return V, policy

def policyevaluation(S, pi_1, F):
    gamma = 0.85
    V1 = {}
    V2 = {}
    for s in S:
        s_index = S.index(s)
        if s_index not in F:
            V1[s_index] = 0
            V2[s_index] = 0
        elif S.index(s) in F:
            V1[s_index] = 2000
            V2[s_index] = 2000

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
                for act in pi_1[s].keys():
                    a = act
                Pro = P[s_index][(a, b)]
                V1[s_index] = R1[s_index][a][b] + gamma * sum(Pro[s] * V1_[s] for s in Pro.keys())
                V2[s_index] = R2[s_index][a][b] + gamma * sum(Pro[s] * V2_[s] for s in Pro.keys())
                delta1 = max(delta1, abs(V1[s_index] - V1_[s_index]))
                delta2 = max(delta2, abs(V2[s_index] - V2_[s_index]))
            elif s_index in F:
                V1[s_index] = 2000
                V2[s_index] = 2000

        if delta1 < 0.0001 * (1 - gamma) / gamma and delta2 < 0.0001 * (1 - gamma) / gamma:
            return V1, V2
    
        
def Available_A(s):
    if s[0] == -1 or s[1] == -1:
        available_A = ["A_ML", "A_MR", "B_ML", "B_MR", "Place"]
    elif s[0] == s[3] and s[1] == s[3]:
        available_A = ["A_ML", "A_MR", "B_ML", "B_MR", "Pick_H", "Pick_L"]
    elif s[0] == s[3]:
        available_A = ["A_ML", "A_MR", "B_ML", "B_MR", "Pick_H"]
    elif s[1] == s[3]:
        available_A = ["A_ML", "A_MR", "B_ML", "B_MR", "Pick_L"]
    else:
        available_A = ["A_ML", "A_MR", "B_ML", "B_MR"]
    if s[3] == 2 * s[2] - 1:
        available_A.remove("A_ML")
    if s[3] == 2 * s[2] + 2:
        available_A.remove("A_MR")

    return available_A
if __name__ == "__main__":
    S = Statespace()
    A, B, Product_A = Actionspace()
    p_H = 0.7
    p_L = 0.9
    P = Transition(S, A, B, Product_A, p_H, p_L)
    testP(P)
    Cost_A, Cost_B = Cost()
    F = FinalState(S)
    R1, R2 = Reward(S, A, B, Cost_A, Cost_B)
    c = initial_state(S)
    
    V, policy = valueiteration(S, P, F, A, R1)
#    V1, V2 = policyevaluation(S, policy, F)
    filename_S = "S_revise.pkl"
    file = open(filename_S, "wb")
    pickle.dump(S, file)
    file.close()
#    
    filename_A = "A_revise.pkl"
    file = open(filename_A, "wb")
    pickle.dump(A, file)
    file.close()
#    
    filename_B = "B_revise.pkl"
    file = open(filename_B, "wb")
    pickle.dump(B, file)
    file.close()
#    
    filename_P = "P_revise.pkl"
    file = open(filename_P, "wb")
    pickle.dump(P, file)
    file.close()
#    
    filename_F = "F_revise.pkl"
    file = open(filename_F, "wb")
    pickle.dump(F, file)
    file.close()
#    
#    
    filename_R1 = "R1_revise.pkl"
    file = open(filename_R1, "wb")
    pickle.dump(R1, file)
    file.close()
#    
    filename_R2 = "R2_revise.pkl"
    file = open(filename_R2, "wb")
    pickle.dump(R2, file)
    file.close()
#    
    filename_c = "c_revise.pkl"
    file = open(filename_c, "wb")
    pickle.dump(c, file)
    file.close()
    
    filename_policy = "policy_revise.pkl"
    file = open(filename_policy, "wb")
    pickle.dump(policy, file)
    file.close()
    
        