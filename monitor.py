import json
from harness import run_report
from fixtures import incident
if __name__=='__main__':
    result=run_report(*incident())
    print(json.dumps({'fixture':'authored, no live data','window_seconds':[0,180],'expected_rows':6,'actual_rows':len(result),'rows':result},indent=2))
