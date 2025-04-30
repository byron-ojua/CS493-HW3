# main.py
from __future__ import annotations
from app import create_app

app = create_app()

# index is the root route for the API
@app.route('/')
def index():
    return "You have reached the root API route for Byron Ojua-Nice's CS493 Homework 3!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)