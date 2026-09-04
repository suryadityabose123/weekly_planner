import os
import datetime

from config import DEFINITIONS_FOLDER
from Definitions.definitions import (
    TimeTable,
    timeslot_conv,
    EMPTY,
    NORMAL,
    CREATIVE
)

from flask import Flask, render_template, request

app = Flask(__name__)


# One TimeTable instance for the whole running Flask application
timetable = TimeTable()


@app.route("/")
def planner():

    today = datetime.datetime.today().strftime("%A")

    return render_template(
        "planner.html",
        timetable=timetable,
        timeslot_conv=timeslot_conv,
        today=today
    )


@app.route("/set_day", methods=["POST"])
def set_day():


    data = request.get_json()

    day = data["day"]

    normal_ranges = data["normal_ranges"]
    creative_ranges = data["creative_ranges"]

    print("Day:", day)
    print("Normal ranges:", normal_ranges)
    print("Creative ranges:", creative_ranges)


    # =========================================
    # Convert NORMAL ranges
    # =========================================

    normal_time_ranges = []

    for r in normal_ranges:

        start = timeslot_conv[r["start"]]
        end = timeslot_conv[r["end"]]

        normal_time_ranges.append((start, end))


    # =========================================
    # Convert CREATIVE ranges
    # =========================================

    creative_time_ranges = []

    for r in creative_ranges:

        start = timeslot_conv[r["start"]]
        end = timeslot_conv[r["end"]]

        creative_time_ranges.append((start, end))


    print("Normal time ranges:", normal_time_ranges)
    print("Creative time ranges:", creative_time_ranges)


    # =========================================
    # Replace current state of this day
    # =========================================

    timetable.week_df[day] = EMPTY


    # =========================================
    # Assign NORMAL slots
    # =========================================

    if normal_time_ranges:

        timetable.assign_slots(
            day,
            normal_time_ranges,
            NORMAL
        )


    # =========================================
    # Assign CREATIVE slots
    # =========================================

    if creative_time_ranges:

        timetable.assign_slots(
            day,
            creative_time_ranges,
            CREATIVE
        )


    # Monday = 1, Tuesday = 2, etc.

    weekday = (
        list(timetable.week_df.columns).index(day) + 1
    )


    # =========================================
    # Calculate residuals
    # =========================================

    normal_residual, creative_residual = \
        timetable.calc_residual(weekday)

    normal_residual = int(normal_residual)
    creative_residual = int(creative_residual)


    print("Normal residual:", normal_residual)
    print("Creative residual:", creative_residual)


    return {
        "status": "success",
        "day": day,
        "normal_ranges": normal_ranges,
        "creative_ranges": creative_ranges,
        "normal_residual": normal_residual,
        "creative_residual": creative_residual
    }

@app.route("/set_rest_day", methods=["POST"])
def set_rest_day():

    data = request.get_json()

    day = data["day"]

    # Monday = 1, Tuesday = 2, etc.
    weekday = (
        list(timetable.week_df.columns).index(day) + 1
    )

    timetable.rest_day = weekday

    print("Rest day:", day)
    print("Rest day number:", timetable.rest_day)

    return {
        "status": "success",
        "rest_day": day
    }


@app.route("/set_starting_slots", methods=["POST"])
def set_starting_slots():

    data = request.get_json()

    starting_slots = int(data["starting_slots"])

    timetable.starting_slots = starting_slots

    print("Starting slots:", timetable.starting_slots)

    return {
        "status": "success",
        "starting_slots": timetable.starting_slots
    }

if __name__ == "__main__":
    app.run(debug=True)