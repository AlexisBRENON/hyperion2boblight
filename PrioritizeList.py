import threading

class PrioritizeList(object):
	"""docstring for PrioritizeList"""
	def __init__(self):
		super(PrioritizeList, self).__init__()
		self.lock = threading.Lock()
		self.priorities = {}
		self.event = threading.Event()
