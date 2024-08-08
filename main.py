import os
import time
from datetime import datetime
from uuid import uuid4
from faker import Faker
from flask import Flask, Response, redirect, render_template
from threading import Thread
from loguru import logger

fake = Faker()
app = Flask(__name__)

DATASETS_LOGS = "../data"


def mockDeployment(deploymentId: str):
    filepath = os.path.join(DATASETS_LOGS, f"{deploymentId}.log")
    logger.info("Initiating Deployment {}", deploymentId)
    logger.info("Pushing the logs to {}", filepath)

    with open(filepath, "a", encoding="utf-8") as fp:
        for _ in range(100000):
            fp.write(f"{datetime.now().isoformat()}: {fake.text(max_nb_chars=64)}\n")
            fp.flush()
            time.sleep(0.5)


@app.route('/')
def indexHandler():
    deployments = [
        x.split(".")[0] for x in os.listdir(DATASETS_LOGS) if x.endswith(".log")
    ]
    return render_template("index.html", deployments=deployments)


@app.route("/deployments/<deployment_id>", methods=["GET"])
def deploymentHandler(deployment_id):
    return render_template("deployment.html", deployment_id=deployment_id)


@app.route("/deployments", methods=["POST"])
def createDeploymentHandler():
    deployment_id = uuid4().hex
    thread = Thread(target=mockDeployment, args=(deployment_id,))
    thread.start()

    return redirect(f"/deployments/{deployment_id}", 301)


def logTailer(deploymentId: str):
    filepath = os.path.join(DATASETS_LOGS, f"{deploymentId}.log")
    logger.info("Initiating Deployment {}", deploymentId)
    logger.info("Pushing the logs to {}", filepath)

    with open(filepath, "r", encoding="utf-8") as fp:
        while True:
            line = fp.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield f"data: {line.strip()}\n\n"


@app.route("/logs/<deployment_id>")
def streamLogHandler(deployment_id):
    logstream = logTailer(deployment_id)
    return Response(logstream, mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)
