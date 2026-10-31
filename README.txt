SMARTNUMBERCHALLENGE - FLASK WEB VERSION

FILES
- app.py: Flask web server and game routes
- templates/: HTML pages
- static/style.css: responsive styling
- leaderboard.json: saved leaderboard records (created automatically if missing)

RUN ON WINDOWS
1. Extract this ZIP.
2. Open the extracted SmartNumberChallenge_Web folder in VS Code.
3. Open Terminal in that folder.
4. Install Flask:
   py -m pip install -r requirements.txt
5. Start the website:
   py app.py
6. Open this address in your browser:
   http://127.0.0.1:5000

NOTES
- Your existing main.py is not modified or required by this web version.
- Your old leaderboard.json can be copied into this folder to keep compatible previous records.
- The web version stores game session scores in leaderboard.json when the player chooses
  "Finish game and view final result" or "Finish & save score".
- This is a local development version. Do not deploy with Flask debug mode enabled.
- For public deployment, set a strong SECRET_KEY environment variable and use a production WSGI server.
