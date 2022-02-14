# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 19:30:48 2021

@author: 53055
"""

import Model_2
import LP
import pickle


if __name__ == "__main__":
    S = Model_2.StateSpace()
    F = Model_2.FinalState(S)
    c = Model_2.initState(S)
    A_H, A_R = Model_2.ActionSpace(S)
    Cost_H, Cost_R = Model_2.Cost(h = 25)
    R_H, R_R = Model_2.Reward(A_H, A_R, Cost_H, Cost_R)
    P = Model_2.Transition(S, F, A_H, A_R)
    Model_2.testP(P)
    
    with open("v1_0.pkl", "rb") as f:
        v1_0 = pickle.load(f)
    
    k = 15
    robot_res, human_res, v1_0 = LP.LinearProgramming(S, A_H, A_R, P, F, R_H, R_R, c, v1_0, k)