""" in a group of 27 random people, what is the probability that there exists a month without anyones birthday """

import numpy as np

num_people = 27
num_simulations = 100000
count = 0

for _ in range(num_simulations):
    birthdays = np.random.randint(low=1, high=13, size=num_people)
    if len(np.unique(birthdays)) < 12:
        count += 1

probability = count / num_simulations

print('Probability:', probability)
