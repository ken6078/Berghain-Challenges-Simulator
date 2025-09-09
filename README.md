# Berghain Challenges Simulator
This tool pulls guest data from a game server and uses randomization to generate new customers, allowing players (or "bouncer") to quickly test and refine their decision-making strategies.

Game Link: https://berghain.challenges.listenlabs.ai/

# 🚀 Features
* Server Integration: Fetch guest data directly from the game server.
* Random Guest Generation: Simulate diverse guest profiles with randomized attributes.
* Fast Strategy Testing: Train and evaluate bouncer strategies in a controlled environment.
* Modular Design: Easy to extend or adjust the rules and guest behavior.

# 🛠 Tech Stack
* Language: Python
* Random generation: random / numpy
* Server communication: requests

📦 Installation
```bash
# Clone the repository
git clone https://github.com/ken6078/Berghain-Challenges-Simulator.git
cd Berghain-Challenges-Simulator

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

# ▶️ Usage
### 🔹 Simulation Mode
Run the simulator with random guests for testing strategies:
```bash
python Simulator/main.py
```

### 🔹 Competition Mode
Run with live guest data pulled from the game server:
```bash
python main.py
```

# 📂 Project Structure
```bash
Berghain-Challenges/
│── Problem/
│   │── Dataset/         # problem dataset (p1/p2/p3)
│   │── introduce.md    # Introduce of the game
│   └── ...             # NewGame return
│── Simulator/
│   └── main.py         # Simulation mode (random guest generator)
│   └── Simulator.py    # Simulator mod implementation
│── main.py             # Competition mode (live server connection)
│── GameSession.py      # Competition mode implementation
│── Model.py            # The Model type of Simulator and Gamesession return
│── requirements.txt    # Dependencies
```

# 🤝 Contributing
Contributions are welcome!
Feel free to open issues or submit PRs to improve the simulation.

# 📜 License
This project is licensed under the Apache License 2.0.
See the LICENSE file for details.
