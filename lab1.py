import math

def calc_entropy_col(col, threshold, data, classes):
	above = []
	below = []
	below = [x for x in data if x[col] <= threshold]
	above = [x for x in data if x[col] > threshold]

   
	below_prob = float(len(below))/len(data) if len(data) > 0 else 1
	above_prob = float(len(above))/len(data) if len(data) > 0 else 1

	return below, above, (below_prob*calc_entropy(below, classes) + above_prob*calc_entropy(above, classes))
	#below.append(calc_entropy(below[0], classes))
	#above.append(calc_entropy(above[0], classes))


def calc_entropy(data, classes):
	entropy = 0
	total = len(data)
	if total == 0:
		return 1

	c_j = []
	for c in classes:
		c_j.append(len([x for x in data if x[2] == c]))
	
	for c in c_j:
		prob = (float(c)/total)
		entropy += prob*math.log(prob, 2) if prob > 0 else 0

	return -entropy

def calc_entropy_range(col, data, classes):
	min_entropy = 1
	min_threshold = 0
	min_below = []
	min_above = []
	for l in [x*0.1 for x in range(0, 70, 1)]:
		below, above, ent = calc_entropy_col(col, l, data, classes)
		if ent != 0 and ent < min_entropy:
			min_entropy = ent
			min_threshold = l
			min_below = below
			min_above = above
		#print("threshold: " + str(l))
		#print("below len: " + str(len(b[0])) + " entropy: " + str(b[1]))
		#print("above len: " + str(len(a[0])) + " entropy: " + str(a[1]))
	return min_below, min_above, min_entropy, min_threshold

if __name__ == '__main__':
	with open('lab1-training-data.txt') as file:
		lines = [x.split('\t') for x in file.read().split('\r\n')]
	training_data = []
	for x in lines[1:-1]:
		training_data.append([float(x[0]), float(x[1]), x[2].replace('\xa0', ' ')])

	classes = set(x[2] for x in training_data)
	#b, a = calc_entropy_col(0, 2.5, training_data, classes)
	#print(b[1], a[1])

	col0_below, col0_above, col0_min_entropy, col0_min_threshold = calc_entropy_range(0, training_data, classes)
	col1_below, col1_above, col1_min_entropy, col1_min_threshold = calc_entropy_range(1, training_data, classes)

	if col0_min_entropy < col1_min_entropy:
		col1b_below, col1b_above, col1b_min_entropy, col1b_min_threshold = calc_entropy_range(1, col0_below, classes)
		col1a_below, col1a_above, col1a_min_entropy, col1a_min_threshold = calc_entropy_range(1, col0_above, classes)
		print("Column 0: threshold(" + str(col0_min_threshold) + ") entropy(" + str(col0_min_entropy) + ")")
		print("Column 1 Below: threshold(" + str(col1b_min_threshold) + ") entropy(" + str(col1b_min_entropy) + ")")
		print("Column 1 Above: threshold(" + str(col1a_min_threshold) + ") entropy(" + str(col1a_min_entropy) + ")")
	else:
		col0b_below, col0b_above, col0b_min_entropy, col0b_min_threshold = calc_entropy_range(0, col1_below, classes)
		col0a_below, col0a_above, col0a_min_entropy, col0a_min_threshold = calc_entropy_range(0, col1_above, classes)
		print("Column 1: threshold(" + str(col1_min_threshold) + ") entropy(" + str(col1_min_entropy) + ")")
		print("Column 0 Below: threshold(" + str(col0b_min_threshold) + ") entropy(" + str(col0b_min_entropy) + ")")
		print("Column 0 Above: threshold(" + str(col0a_min_threshold) + ") entropy(" + str(col0a_min_entropy) + ")")

	#print('0 ' + str(calc_entropy_range(0, training_data, classes)))
	#print('1 ' + str(calc_entropy_range(1, training_data, classes)))