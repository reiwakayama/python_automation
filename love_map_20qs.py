# Randomly pick 20 numbers between 1-60, 3x

import random
r1 = 1
r2 = 60 
li = list(range(r1,r2))

batch1 ={2, 14, 59, 36, 7, 9, 60, 31, 30, 22, 28, 10, 8, 47, 11, 44, 3, 1, 20, 29}
print(f"Batch 1: {batch1}")

li = list(filter(lambda x: x not in batch1, li))

batch2 = random.sample(li, 20)
print(f"Batch 2: {batch2}")

li = list(filter(lambda x: x not in batch2, li))
print(f"Batch 3: {li}")
