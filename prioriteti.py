koji_puni = 0

def prioritetizuj(k1uv, k2uv, k3uv, count1, count2, count3):
	global koji_puni
	kuv = [k1uv, k2uv, k3uv]

	c1 = count1
	c2 = count2
	c3 = count3	
	print [c1, c2, c3]
	if(kuv == [1,1,1]):

		if(c1 == c2 and c2 == c3):
			koji_puni = 1
		else:
			if c1 == min(c1, c2, c3):
				koji_puni = 1
			elif c2 == min(c1, c2, c3):
				koji_puni = 2
			else:
				koji_puni = 3
	elif(kuv == [1, 1, 0]):

		if c1 > c2:
			koji_puni = 2
		else:
			koji_puni = 1

	elif(kuv == [1,0,1]):

		if c1 > c3:
			koji_puni = 3
		else:
			koji_puni = 1

	elif(kuv == [0, 1, 1]):

		if c2 > c3:
			koji_puni = 3
		else:
			koji_puni = 2

	elif kuv == [1, 0, 0]:
		koji_puni = 1
	
	elif kuv == [0, 1, 0]:
		koji_puni = 2

	elif kuv == [0, 0, 1]:
		koji_puni = 3

	elif kuv == [0,0,0]:
		koji_puni = 0
	print "puni: " + str(koji_puni)
