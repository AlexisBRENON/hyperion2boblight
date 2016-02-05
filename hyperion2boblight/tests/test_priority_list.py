"""
Priority list unit test module
"""
import time
import threading

import pytest

from hyperion2boblight import PriorityList

class TestPriorityList:
    """ Define the PriorityList class features/behaviour """

    @pytest.fixture
    def empty_priority_list(self):
        """ Create an empty priority list """
        return PriorityList()

    @pytest.fixture
    def non_empty_priority_list(self, empty_priority_list):
        """ Create a non empty priority list """
        empty_priority_list.put(1, 1)
        empty_priority_list.put(128, 128)
        empty_priority_list.put(255, 255)
        return empty_priority_list

    def test_empty_priority_list_get_first(self, empty_priority_list):
        """ Fetching an item in an empty list must return the tuple (None, None) """
        assert empty_priority_list.get_first() == (None, None)

    def test_empty_priority_list_size(self, empty_priority_list):
        """ A size of an empty priority list is 0 """
        assert empty_priority_list.size() == 0

    def test_empty_priority_list_put_one_value(self, empty_priority_list):
        """ Putting only one value in the priority, the get_first() function must
        return this value """
        empty_priority_list.put(1, 1)
        assert empty_priority_list.get_first() == (1, 1)

    def test_priority_list_size(self, non_empty_priority_list):
        """ The size of a priority list is the number of items in it """
        assert non_empty_priority_list.size() == 3

    def test_priority_list_get_first(self, non_empty_priority_list):
        """ Fetching an item in a priority list must return the tuple with lowest priority value """
        assert non_empty_priority_list.get_first() == (1, 1)

    def test_priority_list_remove_first(self, non_empty_priority_list):
        """ When first (lowest priority) item is removed, next call to get_first() must
        return the second element """
        first_item = non_empty_priority_list.get_first()
        initial_size = non_empty_priority_list.size()
        non_empty_priority_list.remove(first_item[0])
        assert non_empty_priority_list.get_first() != first_item
        assert non_empty_priority_list.size() == initial_size - 1

    def test_priority_list_put_first(self, non_empty_priority_list):
        """ A new value with lowest priority must become the first """
        non_empty_priority_list.put(0, 0)
        assert non_empty_priority_list.get_first() == (0, 0)

    def test_priority_list_clear(self, non_empty_priority_list):
        """ A call to clear must remove all the items in the priority list """
        non_empty_priority_list.clear()
        assert non_empty_priority_list.size() == 0

    def test_empty_priority_list_wait_item_add(self, empty_priority_list):
        """ In an empty priority list, a call to wait_new_item() should return
        as soon as new item is added """
        expected_tuple = (128, 128)
        def add_item_worker():
            """ Function to add an item to the list after a short pause """
            time.sleep(1.0)
            empty_priority_list.put(expected_tuple[0], expected_tuple[1])

        worker_thread = threading.Thread(target=add_item_worker)
        start = time.time()
        worker_thread.start()
        returned_tuple = empty_priority_list.wait_new_item()
        end = time.time()
        assert returned_tuple == expected_tuple
        assert end - start < 2

    def test_priority_list_wait_item_add_before(self, empty_priority_list):
        """ In a priority list, a call to wait_new_item() should return if an
        item with lower priority is added """
        empty_priority_list.put(128, 128)
        expected_tuple = (1, 1)
        returned_tuple = empty_priority_list.wait_new_item() # Fetch the current first item
        def add_item_worker():
            """ Function to add an item to the list after a short pause """
            time.sleep(1.0)
            empty_priority_list.put(expected_tuple[0], expected_tuple[1])
        worker_thread = threading.Thread(target=add_item_worker)
        worker_thread.start()

        returned_tuple = empty_priority_list.wait_new_item() # Wait for a new item
        assert returned_tuple == expected_tuple

    def test_priority_list_wait_item_add_after(self, empty_priority_list):
        """ In a priority list, a call to wait_new_item() should not return if
        an item with higher priority is added """
        empty_priority_list.put(128, 128)
        returned_tuple = empty_priority_list.wait_new_item() # Fetch the current first item
        def add_item_worker():
            """ Function to add an item to the list after a short pause """
            time.sleep(0.5)
            empty_priority_list.put(255, 255)
            time.sleep(2)
            empty_priority_list.put(1, 1)
        worker_thread = threading.Thread(target=add_item_worker)
        worker_thread.start()

        start = time.time()
        returned_tuple = empty_priority_list.wait_new_item()
        end = time.time()
        assert end - start > 2 # Checj that the wait item doesn't return before the second insert
        assert returned_tuple == (1, 1)

    def test_priority_list_wait_item_remove(self, non_empty_priority_list):
        """ In a priority list, a call to wait_new_item() should return the new
        first item if the current first item is removed """
        expected_tuple = (128, 128)
        returned_tuple = non_empty_priority_list.wait_new_item() # Fetch the current first item
        def add_item_worker():
            """ Function to add an item to the list after a short pause """
            time.sleep(1.0)
            non_empty_priority_list.remove(non_empty_priority_list.get_first()[0])
        worker_thread = threading.Thread(target=add_item_worker)
        worker_thread.start()

        returned_tuple = non_empty_priority_list.wait_new_item() # Wait for a new item
        assert returned_tuple == expected_tuple

