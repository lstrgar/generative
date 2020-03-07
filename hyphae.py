import cairo, math, numpy, scipy, random, glob, imageio
from numpy import cos, sin, pi
from operator import itemgetter
from PIL import Image

#CANVAS SCALE
SCALE = 15000
ONE = 1./SCALE

#MAXIMUM NUMBER OF NODES
NODE_MAX = 2*1e7

#BOUNDING SHAPE PARAMS
CIRCLE_RAIDUS = 0.45

#NUMBER SOURCE NODES
NUM_SOURCES = 5

#RADIUS PARAMS
DEF_RAD = ONE*40.
MIN_RAD_FACT = 0.91
MAX_RAD_FACT = 0.96

#ANGLE SEARCH PARAMS (relative to parent)
MIN_SEARCH_ANG = 0
MAX_SEARCH_ANG = pi/4.

#CHILDREN AND COLLISIONS
C_MAX = 2. # Maximum number of children a node can have
COLL_DIST = 2 # Scalar increasing required distance between nodes
ZONE_WIDTH = 80
NUM_ZONES = int(SCALE/ZONE_WIDTH)


class Render(object):

	def __init__(self, scale):
		
		self.sur = cairo.ImageSurface(cairo.FORMAT_ARGB32, scale, scale)
		self.ctx = cairo.Context(self.sur)
		self.ctx.scale(scale, scale)
		self.ctx.set_source_rgb(1, 1, 1)
		self.ctx.rectangle(0, 0, 1, 1)
		self.ctx.fill()

	def circles(self, x1, y1, x2, y2, r):
		self.ctx.set_source_rgb(0, 0, 0)
		dist = math.hypot(x2 - x1, y2 - y1)
		ang = numpy.arctan2(y2 - y1, x2 - x1)
		i = 0
		while True:
			x = x1 + (i * ONE * cos(ang))
			y = y1 + (i * ONE * sin(ang))
			self.ctx.arc(x, y, r, 0, 2.*pi)
			self.ctx.fill()
			if (i*ONE >= dist):
				return (x, y)
			i += 1

	def circle(self, x, y, r):
		self.ctx.set_source_rgb(0, 0, 0)
		self.ctx.arc(x, y, r, 0, 2.*pi)
		self.ctx.fill()


def random_seed():
	return (random.random(), random.random())

## SEARCH ANGLE OPTIONS
def get_source_angle(uni = True, p1 = 0, p2 = 2.*pi):
	if (uni):
		return random.uniform(p1, p1)
	else:
		return random.normal(p1, p2)

def update_angle(old, p1 = MIN_SEARCH_ANG, p2 = MAX_SEARCH_ANG):
	return old + random.uniform(p1, p2)


## RADIUS OPTIONS
def get_source_radius(default = DEF_RAD, rand = True, uni = True, minm = 38*ONE, maxm = 62*ONE, sd = 7):
	if (rand):
		if (uni):
			return random.uniform(minm, maxm)
		else:
			return random.normal(default, sd)
	else:
		return default

def update_radius(old, uni = True, p1 = MIN_RAD_FACT, p2 = MAX_RAD_FACT):
	if (uni):
		return old * random.uniform(p1, p2)
	else:
		return old * random.normal(p1, p2)


## BOUNDS CHECKING
def inCircle(x, y, r = CIRCLE_RAIDUS):
	return math.sqrt(numpy.square(x-0.5)+numpy.square(y-0.5)) < r

def getZone(x, y):
	x_z = math.floor(x*SCALE/ZONE_WIDTH)
	y_z = math.floor(y*SCALE/ZONE_WIDTH)
	return (NUM_ZONES*y_z) + x_z

def indicesNear(x, y, Zp):
	x_z = math.floor(x*SCALE/ZONE_WIDTH)
	y_z = math.floor(y*SCALE/ZONE_WIDTH)
	zones = numpy.array([x_z-1,x_z,x_z+1,x_z-1,x_z,x_z+1,x_z-1,x_z,x_z+1])+\
		numpy.array([y_z+1,y_z+1,y_z+1,y_z,y_z,y_z,y_z-1,y_z-1,y_z-1])*NUM_ZONES

	zones = [z for z in zones if not z < 1]
	getter = itemgetter(*zones)
	indices = getter(Zp)
	return [j for i in indices for j in i]


## CREATING ANIMATIONS
def to_gif():
	filenames = glob.glob('./temp_images/*.png')
	list.sort(filenames, key=lambda x: x.split('.png')[0])
	images = []
	for filename in filenames:
		images.append(imageio.imread(filename))
	imageio.mimsave('./animations/hyphae.gif', images)


def main():

	render = Render(SCALE) # Get paintbrush and canvas

 	# Track node data x, y, r, parent, children, growth dir
	data = numpy.zeros(shape=(int(NODE_MAX),7), dtype='f')

	# Collision detection -- indices of all points in each zone
	Zp = [[] for i in range((NUM_ZONES+1)**2)]

	for i in range(0, int(NUM_SOURCES)): # Initialize seeds

		x,y = random_seed()
		while not inCircle(x, y, CIRCLE_RAIDUS):
			x, y = random_seed()

		data[i] = (x, y, get_source_radius(rand = True), -1, 0, get_source_angle(), 2.*pi)
		z = getZone(x, y)
		Zp[z].append(i)



	index = NUM_SOURCES

	while True:

		try:

			i = random.randint(0, index)
			if data[i][4] > C_MAX:
				#print("Maximum number of children")
				continue

			(x,y,r,p,c,d,ms) = data[i]

			new_r = update_radius(r)
			if (new_r < ONE):
				#print("Radius too small")
				data[i][4] = C_MAX + 1
				continue

			new_d = update_angle(d, p2 = ms)

			new_x = x + (sin(new_d) * r * random.uniform(4, 5))
			new_y = y + (cos(new_d) * r * random.uniform(4, 5))
			if not inCircle(new_x, new_y):
				#print("Outside of bounds")
				continue

			new_ms = random.uniform(0, pi/5.) if random.uniform(0,1) > 0.97 else ms

			indices = indicesNear(new_x, new_y, Zp)
			indices = [ind for ind in indices if ind != i]


			if len(indices) > 0:

				xs = numpy.array([d[0] for d in data[indices]])
				ys = numpy.array([d[1] for d in data[indices]])
				rs = numpy.array([d[2] for d in data[indices]])
				dists = numpy.sqrt(numpy.square(xs - new_x) + numpy.square(ys - new_y))
				collisions = dists > COLL_DIST + (rs + r)


			if len(indices) == 0 or all(collisions):
				print(index)
				new_x, new_y = render.circles(x, y, new_x, new_y, new_r)
				data[index] = (new_x, new_y, new_r, i, 0, new_d, new_ms)
				data[i][4] += 1
				z = getZone(new_x, new_y)
				Zp[z].append(index)


				# Not drawing for animation
				# if ((index - 1) % DRAW_FREQ == 0):
				# 	render.sur.write_to_png('temp_images/hyphae.{:d}.png'.format(index))


				index += 1


		except KeyboardInterrupt:
			render.sur.write_to_png('temp_images/hyphae.png')
			# Image.MAX_IMAGE_PIXELS = None
			# to_gif()
			break

	return


if __name__ == '__main__':
	main()

