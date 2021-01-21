# importar los paquetes necesarios
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker:
	def __init__(self, maxDisappeared=50, maxDistance=50, mask=None):
	
		# inicializar el siguiente ID de objeto único junto con dos ordenados
		# diccionarios utilizados para realizar un seguimiento del mapeo de un objeto determinado
		# ID a su centroide y número de fotogramas consecutivos que tiene
		# han sido marcados como "desaparecidos", respectivamente

		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()

		# almacenar el número máximo de fotogramas consecutivos en un determinado
		# Se permite marcar el objeto como "desaparecido" hasta que
		# es necesario anular el registro del objeto del seguimiento
		

		self.maxDisappeared = maxDisappeared

		# almacenar la distancia máxima entre centroides para asociar
		# un objeto - si la distancia es mayor que este máximo
		# distancia comenzaremos a marcar el objeto como "desaparecido"
		self.maxDistance = maxDistance

		self.mask=mask

	def register(self, centroid):
		# al registrar un objeto usamos el siguiente objeto disponible
		# ID para almacenar el centroide
		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		self.nextObjectID += 1

	def deregister(self, objectID):
		# para anular el registro de un ID de objeto, eliminamos el ID de objeto de
		# ambos de nuestros respectivos diccionarios
		del self.objects[objectID]
		del self.disappeared[objectID]


	def update(self, rects):
		# compruebe si la lista de rectángulos del cuadro delimitador de entrada
		# esta vacio
		if len(rects) == 0:
			# recorrer los objetos rastreados existentes y marcarlos
			# como desaparecido
			for objectID in list(self.disappeared.keys()):
				self.disappeared[objectID] += 1

				# si hemos alcanzado un número máximo de consecutivos
				# fotogramas donde un objeto dado ha sido marcado como
				# faltante, anular el registro
				if self.disappeared[objectID] > self.maxDisappeared:
					self.deregister(objectID)


			# regrese temprano ya que no hay centroides ni información de seguimiento
			# actualizar
			return self.objects

		# inicializar una matriz de centroides de entrada para el marco actual
		inputCentroids = np.zeros((len(rects), 2), dtype="int")

		# recorrer los rectángulos del cuadro delimitador
		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			# use las coordenadas del cuadro delimitador para derivar el centroide
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			inputCentroids[i] = (cX, cY)

		# si actualmente no estamos rastreando ningún objeto, tome la entrada
		# centroides y registrar cada uno de ellos
		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i])

		# de lo contrario, actualmente están rastreando objetos, por lo que debemos
		# intente hacer coincidir los centroides de entrada con el objeto existente
		# centroides
		else:
			# toma el conjunto de ID de objeto y los centroides correspondientes
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

			# filtrar los centroides que están fuera de la máscara
			objectCentroids = [item if self.centroid_inside_mask(item) else [0, 0] for item in objectCentroids]

			# calcula la distancia entre cada par de objetos
			# centroides y centroides de entrada, respectivamente - nuestro
			# el objetivo será hacer coincidir un centroide de entrada con un
			# objeto centroide
			D = dist.cdist(np.array(objectCentroids), inputCentroids)

			# para realizar este emparejamiento debemos (1) encontrar el
			# valor más pequeño en cada fila y luego (2) ordenar la fila
			# índices basados en sus valores mínimos para que la fila
			# con el valor más pequeño como en el * frente * del índice
			# lista
			rows = D.min(axis=1).argsort()

			# a continuación, realizamos un proceso similar en las columnas mediante
			# encontrar el valor más pequeño en cada columna y luego
			# ordenar usando la lista de índice de fila calculada previamente
			cols = D.argmin(axis=1)[rows]

			# para determinar si necesitamos actualizar, registrar,
			# o anular el registro de un objeto que necesitamos para realizar un seguimiento
			# de los índices de filas y columnas que ya hemos examinado
			usedRows = set()
			usedCols = set()

			# recorrer la combinación del índice (fila, columna)
			# tuplas
			for (row, col) in zip(rows, cols):
				# si ya hemos examinado la fila o
				# valor de columna antes, ignóralo
				if row in usedRows or col in usedCols:
					continue

				# si la distancia entre centroides es mayor que
				# la distancia máxima, no asocie los dos
				# centroides al mismo objeto
				if D[row, col] > self.maxDistance:
					continue


				# de lo contrario, tome el ID del objeto para la fila actual,
				# establece su nuevo centroide y restablece el desaparecido
				# mostrador
				objectID = objectIDs[row]

				self.disappeared[objectID] = 0

				self.objects[objectID] = inputCentroids[col]


				# indicar que hemos examinado cada una de las filas y
				# índices de columna, respectivamente
				usedRows.add(row)
				usedCols.add(col)

			# calcular el índice de fila y columna que NO tenemos todavía
			# examinado
			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)

			# en el caso de que el número de centroides del objeto sea
			# igual o mayor que el número de centroides de entrada
			# tenemos que comprobar y ver si algunos de estos objetos tienen
			# potencialmente desaparecido
			if D.shape[0] >= D.shape[1]:
				# recorrer los índices de fila no utilizados
				for row in unusedRows:
					# toma el ID del objeto para la fila correspondiente
					# indexar e incrementar el contador desaparecido
					objectID = objectIDs[row]
					self.disappeared[objectID] += 1

					# compruebe si el número de consecutivos
					# marcos el objeto ha sido marcado como "desaparecido"
					# para garantías de anular el registro del objeto
					if self.disappeared[objectID] > self.maxDisappeared:
						self.deregister(objectID)

			# de lo contrario, si el número de centroides de entrada es mayor
			# que el número de centroides de objetos existentes que necesitamos
			# registrar cada nuevo centroide de entrada como un objeto rastreable
			else:
				for col in unusedCols:
					self.register(inputCentroids[col])

		# devolver el conjunto de objetos rastreables
		return self.objects

	def centroid_inside_mask(self, centroid):
		if self.mask is None:
			return True
		x, y = centroid
		if x < self.mask[0][0] or x > self.mask[1][0]:
			return False
		if y < self.mask[0][1] or y > self.mask[1][1]:
			return False
		return True