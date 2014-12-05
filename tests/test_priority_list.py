import pytest
import hyperemote2boblight.lib.priority_list as priority_list

class TestPriorityList:
  """ Define the PriorityList class features/behaviour """

  @pytest.fixture
  def empty_priority_list(self):
    return priority_list.PriorityList();

  @pytest.fixture
  def non_empty_priority_list(self, empty_priority_list):
    empty_priority_list.put(1, 1)
    empty_priority_list.put(128, 128)
    empty_priority_list.put(255, 255)
    return empty_priority_list
  
  def test_empty_priority_list_get_first(self, empty_priority_list):
    """ Fetching an item in an empty list must return the tuple (None, None) """
    assert empty_priority_list.get_first() == (None, None)

  def test_empty_priority_list_put_one_value(self, empty_priority_list):
    """ Putting only one value in the priority, the get_first() function must return this value """
    empty_priority_list.put(1, 1)
    assert empty_priority_list.get_first() == (1, 1)

  def test_priority_list_get_first(self, non_empty_priority_list):
    """ Fetching an item in a priority list must return the tuple with lowest priority value """
    assert non_empty_priority_list.get_first() == (1, 1)

  def test_priority_list_remove_first(self, non_empty_priority_list):
    """ When first (lowest priority) item is removed, next call to get_first() must return the second element """
    first_item = non_empty_priority_list.get_first()
    non_empty_priority_list.remove(first_item[0])
    assert non_empty_priority_list.get_first() != first_item
  
  def test_priority_list_put_first(self, non_empty_priority_list):
    """ A new value with lowest priority must become the first """
    non_empty_priority_list.put(0, 0)
    assert non_empty_priority_list.get_first() == (0, 0)

  def test_priority_list_clear(self, non_empty_priority_list):
    """ A call to clear must remove all the items in the priority list """
    non_empty_priority_list.clear()
    assert non_empty_priority_list.get_first() == (None, None)

  