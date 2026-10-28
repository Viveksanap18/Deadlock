from algorithms.banker import calculate_need, safety_algorithm, request_resources

def test_need_and_safe_sequence():
    a=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]; m=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
    assert calculate_need(a,m)[0]==[7,4,3]
    out=safety_algorithm(a,m,[3,3,2]); assert out['safe'] and len(out['safe_sequence'])==5

def test_waiting_request_preserves_state():
    a=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]; m=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]; av=[3,3,2]; old=[r.copy() for r in a]
    out=request_resources(a,m,av,0,[0,0,3]); assert out['status']=='waiting' and a==old and av==[3,3,2]

def test_unsafe_request_denied_without_mutation():
    a=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]; m=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]; av=[3,3,2]
    out=request_resources(a,m,av,0,[0,0,2]); assert out['status']=='denied' and a[0]==[0,1,0] and av==[3,3,2]
