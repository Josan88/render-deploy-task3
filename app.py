import os
from flask import Flask, render_template

app = Flask(__name__)

# Read environment variable (configured in Render)
APP_ENV = os.environ.get("APP_ENV", "development")
VERSION = "1.0.1"


@app.route("/")
def home():
    return render_template("index.html", environment=APP_ENV, version=VERSION)


@app.route("/health")
def health():
    return {"status": "ok", "environment": APP_ENV, "version": VERSION}, 200


@app.route("/version")
def version():
    return {"version": VERSION}, 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
