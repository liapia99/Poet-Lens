from flask import Flask, render_template, request
import subprocess
import os
import signal

app = Flask(__name__)

# Global variable to keep track of the running processes
current_process = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run-original", methods=["POST"])
def run_original():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/main.py"])
    return render_template("running.html", action="Original")

@app.route("/run-dreamlike", methods=["POST"])
def run_dreamlike():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/dream.py"])
    return render_template("running.html", action="Dreamlike")

@app.route("/run-haiku", methods=["POST"])
def run_haiku():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/haiku.py"])
    return render_template("running.html", action="Haiku")

@app.route("/run-sonnet", methods=["POST"])
def run_sonnet():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/sonnet.py"])
    return render_template("running.html", action="Sonnet")

@app.route("/run-limerick", methods=["POST"])
def run_limerick():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/limerick.py"])
    return render_template("running.html", action="Limerick")

@app.route("/run-acrostic", methods=["POST"])
def run_acrostic():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/acrostic.py"])
    return render_template("running.html", action="Acrostic")

@app.route("/run-future", methods=["POST"])
def run_future():
    global current_process
    if current_process:
        kill_process(current_process)
    current_process = subprocess.Popen(["python3", "/home/piascikj2/webapp/future.py"])
    return render_template("running.html", action="Future")

@app.route("/clear", methods=["POST"])
def clear():
    global current_process
    if current_process:
        kill_process(current_process)
        current_process = None
    return render_template("clear.html")


# Go back route to return to the index page
@app.route("/go-back", methods=["POST"])
def go_back():
    return render_template("index.html")

# Function to kill the process
def kill_process(process):
    if process:
        try:
            os.kill(process.pid, signal.SIGTERM)  # Try to terminate the process
            print(f"Process {process.pid} terminated.")
        except Exception as e:
            print(f"Error killing process: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5054, debug=True)

