# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 11:39:16 2019

@author: micha
"""


def zigzag(array):
    #converts a matrix into 1D array in order of energy frequency values
    
    n = len(array)

    if n != len(array[0]):
        print("Matrix is not square")
        return

    # 1D array container
    ordered = []
    for i in range(n):
        # Iterate through upper left triangle
        for j in range(i+1):
            # Each nth diagonal contains n+1 elements
            if j == 0:
                # Initialize block index
                x = i
                y = 0
            if i % 2 == 0:
                # Moving up the diagonal
                ordered.append(array[x][y])
            else:
                # Moving down the diagonal
                ordered.append(array[y][x])
            # Move to next element
            x -= 1
            y += 1
    for i in range(n - 1, 0, -1):
        # Iterate lower right triangle
        for j in range(i):
            # Each nth diagonal contains n elements
            if j == 0:
                # Initialize indexes
                x = n - i
                y = n - 1
            if i % 2 == 0:
                # Move up the diagonal
                ordered.append(array[x][y])
            else:
                # Move down th diagonal
                ordered.append(array[y][x])
            # Move to next element
            x += 1
            y -= 1
    return ordered




def izigzag(ordered, n=8):
    #converts a 1D array into a blocksize x blocksize matrix 

    count = 0
    # 2D array container
    array = [[0 for i in range(n)] for i in range(n)]

    for i in range(n):
        # Iterate through upper left triangle (including centeral diagonal)
        for j in range(i+1):
            # Each nth diagonal contains n+1 elements
            if j == 0:
                # Initialize indexes
                x = i
                y = 0
            if i % 2 == 0:
                # Moving up the diagonal
                array[x][y] = ordered[count]
            else:
                # Moving down the diagonal
                array[y][x] = ordered[count]
            # Move to next element
            x -= 1
            y += 1
            count += 1
    for i in range(n - 1, 0, -1):
        # Iterate lower triangle (excluding central diagonal)
        for j in range(i):
            # Each nth diagonal contains n elements
            if j == 0:
                # Initialize indexes
                x = n - i
                y = n - 1
            if i % 2 == 0:
                # Move up the diagonal, append array values to new block elements
                array[x][y] = ordered[count]
            else:
                # Move down th diagonal
                array[y][x] = ordered[count]
            # Move to next element
            x += 1
            y -= 1
            count += 1
    return array