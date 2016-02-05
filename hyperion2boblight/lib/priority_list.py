""" The priority list implement a kind of ... priority list !!!
Each item is associated to a priority. The lowest priority item is the first item
to be retrieved.
This module is thread-proof.
"""
import threading

class PriorityList(object):
    """docstring for PriorityList"""
    def __init__(self):
        super(PriorityList, self).__init__()
        self.lock = threading.RLock()
        self.datas = {}
        self.event = threading.Event()
        self.current_obtained_item = (None, None)

    def get_priorities(self):
        """ Return a list of priorities in the list """
        with self.lock:
            result = list(self.datas.keys())
            result.sort()
        return result

    def put(self, priority, data):
        """ Add a new item to the list """
        with self.lock:
            self.datas[priority] = data
            self.event.set()

    def remove(self, priority):
        """ Remove the item with the priority _priority_ """
        with self.lock:
            if priority in self.datas:
                del self.datas[priority]
                self.event.set()

    def clear(self):
        """ Clear the list. Remove every item """
        with self.lock:
            self.datas.clear()
            self.event.set()

    def get_first(self):
        """ Return the first (lowest priority) item.
        If no item are present, return (None, None) """
        with self.lock:
            priorities = self.get_priorities()
            if len(priorities) > 0:
                result = (priorities[0], self.datas[priorities[0]])
            else:
                result = (None, None)
        return result

    def wait_new_item(self):
        """ Wait until the current first item change.
        If an item is added with a higher priority (less prioritary), this
        function will not return. It's the same if an item is removed.
        If the first item is removed, or an item with lower priority is added,
        then it will return the new first item.
        Note : The first call will always return immediately; with (None, None)
               if no items are currently in the list. """
        wait = True
        while wait:
            self.event.wait()
            self.event.clear()
            if self.get_first() != self.current_obtained_item:
                self.current_obtained_item = self.get_first()
                wait = False
        return self.current_obtained_item

    def size(self):
        """ Return the number of item currently in the list """
        with self.lock:
            result = len(self.datas.keys())
        return result
