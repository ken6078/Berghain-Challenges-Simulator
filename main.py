import time

from concurrent.futures import ThreadPoolExecutor, as_completed

from SampleSolution import Solution
from GameSession import GameSession

player_id = "..."
scenario = 1
num_workers = 1

def run_game():
    try:
        gameSession = GameSession(scenario=scenario, player_id = player_id)
        solution = Solution(gameSession.new_game_resp)

        state = gameSession.get_first_person()

        while getattr(state, "status", None) == "running":
            accept = solution.decide(state)
            state = gameSession.next_person(accept=accept)

        return "SUCCESS"
    except Exception as ex:
        print(ex)
        return "FAILURE"

if __name__ == "__main__":
    while True:
        start_time = time.perf_counter()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(run_game) for _ in range(num_workers)]
            for future in as_completed(futures):
                logs = future.result()

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        if elapsed < 930:
            time.sleep(930 - elapsed)
        else:
            time.sleep(30)


