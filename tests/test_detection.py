from algorithms.detection import detect_deadlock, recover_by_terminating

def test_detect_deadlock():
    out=detect_deadlock([[1,0],[0,1]],[[0,1],[1,0]],[0,0]); assert out['detected'] and set(out['deadlocked'])=={'P0','P1'}
def test_recovery_releases_resources():
    out=recover_by_terminating([[1,0],[0,1]],[[0,1],[1,0]],[0,0],0); assert out['released']==[1,0] and out['available_after']==[1,0] and not out['detected']
