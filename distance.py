from math import sin, cos, sqrt, atan2, radians
class Distance():
	def __init__(self):
		self.R = 6373.0


	def calculate_dist_in_kms(self, *args):
		R = self.R
		lat1, lon1, lat2, lon2 = float(args[0]), float(args[1]), float(args[2]), float(args[3])
		d_lon = radians(lon2) - radians(lon1)
		d_lat = radians(lat2) - radians(lat1)

		a = sin(d_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(d_lon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		distance = R * c
		return distance


	def calculate_dist_in_miles(self, *args):
		return self.calculate_dist_in_kms(*args)/0.6214

