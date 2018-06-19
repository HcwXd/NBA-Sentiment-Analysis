def cool():
    point_table = []
    for x in range(4):
        point_table.append(0)
    point_table[2] = 3
    return point_table


banana = cool()
print(banana)
