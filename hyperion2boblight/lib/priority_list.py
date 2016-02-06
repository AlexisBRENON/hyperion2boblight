""" The priority list implement a kind of ... priority list !!!
Each item is associated to a priority. The lowest priority item is the first item
to be retrieved.
This module is thread-proof.
"""

import threading
from queue import Empty as QEmpty

class Empty(QEmpty):
    pass

class PriorityList(object):
    """docstring for PriorityList"""
    def __init__(self):
        super(PriorityList, self).__init__()
        self.data = {}
        self.condition = threading.Condition(threading.RLock())

    def get_priorities(self):
        """ Return a list of priorities in the list """
        with self.condition:
            result = list(self.data.keys())
            result.sort()
        return result

    def put(self, priority, data=None):
        """ Add a new item to the list """
        if isinstance(priority, (tuple, list)):
            data = priority[1]
            priority = priority[0]

        with self.condition:
            self.data[priority] = data
            self.condition.notify_all()

    def remove(self, priority):
        """ Remove the item with the priority _priority_ """
        with self.condition:
            if priority in self.data:
                del self.data[priority]
                self.condition.notify_all()

    def clear(self):
        """ Clear the list. Remove every item """
        with self.condition:
            self.data.clear()
            self.condition.notify_all()

    def get_first(self):
        """ Return the first (lowest priority) item.
        If no item are present, return (None, None) """
        with self.condition:
            priorities = self.get_priorities()
            if len(priorities) > 0:
                result = (priorities[0], self.data[priorities[0]])
            else:
                raise Empty()
        return result

    def wait_new_item(self):
        """
        Wait until the current first item change.
        If an item is added with a higher priority (less prioritary), this
        function will not return. It's the same if an item is removed.
        If the first item is removed, or an item with lower priority is added,
        then it will return the new first item.
        """
        with self.condition:
            while True:
                try:
                    current_first = self.get_first()
                except Empty:
                    current_first = None
                self.condition.wait()
                new_first = self.get_first() # If exception raised, it's the calling thread that
                # must handle it
                if new_first != current_first:
                    break
        return new_first

    def size(self):
        """ Return the number of item currently in the list """
        with self.condition:
            result = len(self.data.keys())
        return result
