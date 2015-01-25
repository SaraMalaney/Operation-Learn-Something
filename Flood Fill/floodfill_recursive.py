
#Recursive flood fill algorithm

def flood_fill(p, canvas, new_value, original_value):
	canvas[p.x][p.y] = new_value
	for n in p.get_neighbours():
		if n.value == original_value:
			flood_fill(n, canvas, new_value, original_value)

class Point:
	def __init__(self, x, y, canvas):
		self.x = x
		self.y = y
		self.canvas = canvas
		self.value = canvas[x][y]
		self.neighbours = []

	def get_neighbours(self):
		if self.x != 0:
			self.neighbours.append(Point(self.x-1,self.y,self.canvas))
		if self.x != len(self.canvas[0]) - 1:
			self.neighbours.append(Point(self.x+1,self.y,self.canvas))
		if self.y != 0:
			self.neighbours.append(Point(self.x,self.y-1,self.canvas))
		if self.y != len(self.canvas) - 1:
			self.neighbours.append(Point(self.x,self.y+1,self.canvas))
		return self.neighbours

this_canvas = [[0, 1, 1, 0],[0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
this_p = Point(0, 0, this_canvas)
origin = this_p.value
flood_fill(this_p, this_canvas, 5, origin)
print this_canvas
