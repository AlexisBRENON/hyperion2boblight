import threading

class PriorityList(object):
  """docstring for PriorityList"""
  def __init__(self):
    super(PriorityList, self).__init__()
    self.lock = threading.RLock()
    self.datas = {}
    self.event = threading.Event()

  def get_priorities(self):
    with self.lock:
      result = list(self.datas.keys())
      result.sort()
    return result

  def put(self, priority, data):
    with self.lock:
      self.datas[priority] = data
      self.event.set()

  def remove(self, priority):
    with self.lock:
      if priority in self.datas:
        del self.datas[priority]
        self.event.set()

  def clear(self):
    with self.lock:
      self.datas.clear()
      self.event.set()

  def get_first(self):
    with self.lock:
      priorities = self.get_priorities()
      if len(priorities) > 0:
        result = (priorities[0], self.datas[priorities[0]])
      else:
        result = (None, None)
    return result

  def wait_new_item(self):
    self.event.wait()
    result = self.get_first()
    self.event.clear()
    return result

  def size(self):
    with self.lock:
      result = len(self.datas.keys())
    return result
