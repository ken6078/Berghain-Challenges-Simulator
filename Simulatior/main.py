from concurrent.futures import ProcessPoolExecutor, as_completed
import os
import numpy as np

from Simulatior.Simulator import Simulator
from SampleSolution import Solution

PROBLEM_PATHS = "../Problem/"
N_RUNS = 100
SCENARIO_ID = 1

def run_one_simulation(_idx: int):
    sim = Simulator(PROBLEM_PATHS)
    ngr = sim.new_game(SCENARIO_ID)
    solution = Solution(ngr)

    state = sim.decide_and_next(ngr.gameId)
    while getattr(state, "status", None) == "running":
        accept = solution.decide(state)
        state = sim.decide_and_next(ngr.gameId, accept=accept)

    result = sim.settle_game(ngr.gameId)

    out = {
        "status": result.get("status"),
        "rejectedPeople": getattr(solution, "rejectedPeople", None),
        "rejectedCount": result.get("rejectedCount"),
        "tag": getattr(solution, "tag", []),
        "tag_reject": getattr(solution, "tag_reject", []),
        "constraints": result.get("constraints", []),
    }
    return out

if __name__ == "__main__":
    success_nums = []
    fail_nums = []

    results = []
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        futures = [ex.submit(run_one_simulation, i) for i in range(N_RUNS)]
        for fut in as_completed(futures):
            results.append(fut.result())

    for r in results:
        if r["status"] == "success":
            success_nums.append(r["rejectedPeople"])
        else:
            fail_nums.append(r["rejectedPeople"])

        if (
            True #Put the filter here
        ):
            counts_pretty = {
                c.get('attribute'): f"{c.get('actual')}/{c.get('required')}"
                for c in (r["constraints"] or [])
            }
            print('Score: ', r["rejectedCount"])
            print('Accept: ', r["tag"])
            print('Reject: ', r["tag_reject"])
            print('Count: ', counts_pretty)
            print('=' * 100)

    print(f'Fail Count: {len(fail_nums)}/{N_RUNS}')
    if success_nums:
        print(f'avg: {np.average(success_nums)}')
        print(f'max: {np.max(success_nums)}')
        print(f'min: {np.min(success_nums)}')
        print(f'std: {np.std(success_nums):.3f}')
        print(f'5%: {np.percentile(success_nums, 5)}')
        print(f'10%: {np.percentile(success_nums, 10)}')
        print(f'25%: {np.percentile(success_nums, 25)}')
        print(f'50%: {np.percentile(success_nums, 50)}')
        print(f'75%: {np.percentile(success_nums, 75)}')
    else:
        print('No successful runs.')
