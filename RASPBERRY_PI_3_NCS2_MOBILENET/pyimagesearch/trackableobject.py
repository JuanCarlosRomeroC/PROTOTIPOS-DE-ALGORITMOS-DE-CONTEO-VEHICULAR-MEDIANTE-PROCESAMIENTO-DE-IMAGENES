class TrackableObject:
	def __init__(self, objectID, centroid):
		# almacenar el ID del objeto, luego inicializar una lista de centroides
		# usando el centroide actual
		self.objectID = objectID
		self.centroids = [centroid]

		# inicializar un booleano usado para indicar si el objeto tiene
		# ya se han contado o no
		self.counted = False