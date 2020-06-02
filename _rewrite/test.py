array = list(range(20))
print(array)

for idx, x in enumerate(array):
	array[idx] = "{0:0=2d}".format(idx)

print(array)