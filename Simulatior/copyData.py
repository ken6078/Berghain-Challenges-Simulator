import pickle
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from SampleSolution import Solution
from GameSession import GameSession

def run_game(scenario: int, output_file):
    try:
        gameSession = GameSession(scenario=scenario)
        solution = Solution(gameSession.new_game_resp)
        state_history = []

        state = gameSession.get_first_person()

        while getattr(state, "status", None) == "running":
            accept = False
            state_history.append(state)
            if gameSession.person_index == 20000:
                break
            state = gameSession.next_person(accept=accept)

        with open(f'problem/p{scenario}/{output_file}', "wb") as f:
            pickle.dump(state_history, f)

        return "SUCCESS"
    except Exception as ex:
        print(ex)
        return "FAILURE"

if __name__ == "__main__":
    # scenario = 2
    num_workers = 10

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(run_game, 2 if num < 5 else 3, f"{str(uuid.uuid4())}-{num}.pkg") for num in range(num_workers)]
        for future in as_completed(futures):
            logs = future.result()
            print("Game finished:", logs)
