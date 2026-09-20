import datetime
import threading
import webbrowser
from zoneinfo import ZoneInfo
from flask import Flask, render_template, request
import json
import os
from config import SAVE_FILE

from Definitions.definitions import (
    TimeTable,
    timeslot_conv,
    DAYS
)


app = Flask(__name__)


# =====================================================
# GLOBAL TIMETABLE
# =====================================================

timetable = TimeTable()
# =====================================================
# SAVE TIMETABLE
# =====================================================

def save_timetable():

    data = {
        "text_blocks": timetable.text_blocks,
        "rest_day": timetable.rest_day,
        "starting_slots": timetable.starting_slots,
        "daily_normal_slots": timetable.daily_normal_slots
    }

    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

# =====================================================
# LOAD TIMETABLE
# =====================================================

def load_timetable():

    if not os.path.exists(SAVE_FILE):
        return

    with open(
        SAVE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)


    timetable.text_blocks = data.get(
        "text_blocks",
        timetable.text_blocks
    )

    timetable.rest_day = data.get(
        "rest_day",
        timetable.rest_day
    )

    timetable.starting_slots = data.get(
        "starting_slots",
        timetable.starting_slots
    )

    timetable.daily_normal_slots = data.get(
        "daily_normal_slots",
        timetable.daily_normal_slots
    )

# =====================================================
# LOAD SAVED STATE
# =====================================================

load_timetable()

# =====================================================
# FORMAT RESIDUAL
# =====================================================

def format_duration(slots):

    total_minutes = int(slots) * 15

    sign = ""

    if total_minutes < 0:

        sign = "- "

        total_minutes = abs(total_minutes)


    hours = total_minutes // 60

    minutes = total_minutes % 60


    if hours == 0:

        return f"{sign}{minutes} minutes"


    if minutes == 0:

        return f"{sign}{hours} hours"


    return (
        f"{sign}{hours} hours "
        f"{minutes} minutes"
    )


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def planner():

    today = datetime.datetime.now(
    ZoneInfo("Asia/Kolkata")
).strftime("%A")


    return render_template(
        "planner2.html",

        timetable=timetable,

        timeslot_conv=timeslot_conv,

        today=today
    )


# =====================================================
# SAVE BLOCK
# =====================================================

@app.route(
    "/save_block",
    methods=["POST"]
)
def save_block():

    data = request.get_json()


    print("Received block:")
    print(data)


    day = data["day"]

    start = int(data["start"])

    end = int(data["end"])

    block_type = data["type"]

    text = data.get(
        "text",
        ""
    )


    # ================================================
    # CHECK FOR EXISTING BLOCK
    # ================================================

    existing_block = None


    for block in timetable.text_blocks[day]:

        if (
            block["start"] == start
            and block["end"] == end
        ):

            existing_block = block

            break


    # ================================================
    # UPDATE EXISTING
    # ================================================

    if existing_block is not None:

        existing_block["type"] = block_type

        existing_block["text"] = text

        block = existing_block


    # ================================================
    # CREATE NEW
    # ================================================

    else:

        if timetable.block_overlaps(
            day,
            start,
            end
        ):

            return {
                "status": "error",
                "message": "Block overlaps another block."
            }, 400


        block = timetable.add_text_block(
            day,
            start,
            end,
            block_type,
            text
        )


    print("Current text blocks:")

    print(
        timetable.text_blocks
    )

    save_timetable()

    return {
        "status": "success",
        "block": block
    }


# =====================================================
# DELETE BLOCK
# =====================================================

@app.route(
    "/delete_block",
    methods=["POST"]
)
def delete_block():

    data = request.get_json()
    
    print("DELETE DATA:")
    print(data)

    day = data["day"]

    start = int(data["start"])

    end = int(data["end"])


    print("Deleting block:")

    print(data)


    timetable.remove_text_block(
        day,
        start,
        end
    )


    print("Current text blocks:")

    print(
        timetable.text_blocks
    )
    
    save_timetable()

    return {
        "status": "success",

        "deleted": {
            "day": day,
            "start": start,
            "end": end
        }
    }


# =====================================================
# REST DAY TOGGLE
# =====================================================

@app.route(
    "/set_rest_day",
    methods=["POST"]
)
def set_rest_day():

    data = request.get_json()

    day = data["day"]


    # -----------------------------------------------
    # Clicking the current rest day again removes it
    # -----------------------------------------------

    if timetable.rest_day == day:

        timetable.rest_day = None

        active = False


    # -----------------------------------------------
    # Otherwise make this the rest day
    # -----------------------------------------------

    else:

        timetable.rest_day = day

        active = True


    print(
        "Rest day:",
        timetable.rest_day
    )

    save_timetable()

    return {

        "status": "success",

        "rest_day":
            timetable.rest_day,

        "active":
            active

    }


@app.route("/reset_day", methods=["POST"])
def reset_day():
    data = request.get_json()
    day = data["day"]

    timetable.clear_text_blocks(day)

    print("Reset day:", day)
    print("Current text blocks:")
    print(timetable.text_blocks)

    save_timetable()
    
    return {
        "status": "success",
        "day": day
    }

# =====================================================
# STARTING SLOTS
# =====================================================

@app.route(
    "/set_starting_slots",
    methods=["POST"]
)
def set_starting_slots():

    data = request.get_json()


    starting_slots = int(
        data["starting_slots"]
    )


    timetable.starting_slots = (
        starting_slots
    )


    print(
        "Starting slots:",
        timetable.starting_slots
    )

    save_timetable()
    return {

        "status": "success",

        "starting_slots":
            starting_slots

    }


# =====================================================
# GET RESIDUAL
# =====================================================

@app.route(
    "/get_residual",
    methods=["POST"]
)
def get_residual():

    data = request.get_json()

    day = data["day"]


    weekday = (
        DAYS.index(day) + 1
    )


    normal_residual, creative_residual = \
        timetable.calc_residual(
            weekday
        )


    return {

        "normal_residual":
            format_duration(
                normal_residual
            ),

        "creative_residual":
            format_duration(
                creative_residual
            )

    }

@app.route(
    "/set_daily_normal_hours",
    methods=["POST"]
)
def set_daily_normal_hours():

    data = request.get_json()

    minutes = int(data["minutes"])

    timetable.daily_normal_slots = (
        minutes // 15
    )

    print(
        "Daily normal minutes:",
        minutes
    )

    print(
        "Daily normal slots:",
        timetable.daily_normal_slots
    )
    save_timetable()
    return {
        "status": "success",
        "daily_normal_slots":
            timetable.daily_normal_slots
    }
# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

        threading.Timer(
        1.5,
        lambda: webbrowser.open(
            "http://127.0.0.1:5000"
        )).start()

        app.run(debug=True)