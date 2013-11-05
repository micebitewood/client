import os
import random
dir = './'
teams = [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]
teams = teams[1:]
random.shuffle(teams)
random.shuffle(teams)
random.shuffle(teams)

for i in range(len(teams)):
    if i % 2 == 0:
        print teams[i], 'vs',
    else:
        print teams[i]
