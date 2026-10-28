import pytest
from algorithms.banker import calculate_need, safety_algorithm, request_resources

def test_zero_available_and_zero_need():
    assert safety_algorithm([[1]],[[1]],[0])['safe']
    assert not safety_algorithm([[1]],[[2]],[0])['safe']
def test_invalid_request_inputs():
    assert request_resources([[0]],[[1]],[1],0,[-1])['status']=='invalid'
    assert request_resources([[0]],[[1]],[1],4,[0])['status']=='invalid'
def test_allocation_exceeds_maximum():
    with pytest.raises(ValueError): calculate_need([[2]],[[1]])
