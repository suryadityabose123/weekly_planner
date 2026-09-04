import os
import datetime
from config import DEFINITIONS_FOLDER
from Definitions.definitions import TimeTable, timeslot_conv

from flask import Flask, render_template, request, url_for

app = Flask(__name__)


@app.route("/")
def planner():

    timetable = TimeTable()

    today = datetime.datetime.today().strftime("%A")

    return render_template(
        "planner.html",
        timetable=timetable,
        timeslot_conv=timeslot_conv,
        today=today
    )


if __name__ == "__main__":
    app.run(debug=True)