from algorithms.prevention import resource_order_check, hold_and_wait_check

def test_resource_order():
    assert not resource_order_check(['B'],'A',['A','B','C'])['allowed']
    assert resource_order_check(['A'],'B',['A','B','C'])['allowed']
def test_hold_wait():
    assert not hold_and_wait_check(['A'],['B'],False)['allowed']
    assert hold_and_wait_check([],['A','B'],True)['allowed']
