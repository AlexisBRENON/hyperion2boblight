import threading

class PriorityList(object):
  """docstring for PriorityList"""
  def __init__(self):
    super(PriorityList, self).__init__()
    self.lock = threading.RLock()
    self.datas = {}
    self.event = threading.Event()

  def getPriorities(self):
    with self.lock:
      result = self.datas.keys()
      result.sort()
    return result

  def get_priorities(self):
    return self.getPriorities()

  def set(self, priority, data):
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

  def getFirst(self):
    with self.lock:
      priorities = self.getPriorities()
      if len(priorities) > 0:
        result = (priorities[0], self.datas[priorities[0]])
      else:
        result = (None, None)
    return result

  def get_first(self):
    return self.getFirst()

  def waitNewItem(self):
    self.event.wait()
    result = self.getFirst()
    self.event.clear()
    return result

  def wait_new_item(self):
    return self.waitNewItem()
