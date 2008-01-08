#! /usr/bin/python

import os

for foo in range(1, 10):
    print foo
    os.spawnlp(os.P_NOWAIT, "./hammer_add.sh", str(foo))
    
    
os.waitpid(-1, 0)




