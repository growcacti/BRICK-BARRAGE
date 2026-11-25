BRICK BARRAGE
Python 3 / Pygame offline game for Linux and Windows.

MX Linux: open a terminal in this folder and run:
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  .venv/bin/python main.py
If venv is missing: sudo apt install python3-venv
Alternatively install python3-pygame through MX Package Installer and run python3 main.py.
Windows: py -m pip install -r requirements.txt
         py main.py

Click above the launch line to fire. Bricks lose one hit point per hit.
Green +1 circles add balls to future rounds. Red BOOM bricks damage neighbors.
Each round adds a row. Avoid bricks reaching the bottom.
S cycles speed; R recalls balls; P pauses; N starts over; D changes difficulty;
F toggles fullscreen; Esc quits. Progress saves between rounds in ~/.brick_barrage.json.
Quitting during a round resumes from the previous completed round.
