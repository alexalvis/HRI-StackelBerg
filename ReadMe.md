You will see five different folders, while you can ignore two folders: new_example, new_example_2. There are readme files in every folder, which tells you the number of state that the robot arm has and the number of state that the robot base has.

You can ignore all the ".pkl" files because those are used to store file data. Just check the model.py and LP.py file.

Model.py mainly specifies the states the whole system has and the transition, rewards, etc. that makes up the MDP.

LP.py specifies the linear programming part. It includes all the restrictions of the linear programming.

