import os
import pandas as pd
import numpy as np
import datetime

EMPTY = 0
NORMAL = 1
CREATIVE = 2

DAILY_NORMAL_SLOTS = 32
DAILY_CREATIVE_SLOTS = 4

# Display dictionary

calendar_disp_dict = {
    EMPTY: "Plain_White",
    NORMAL: "Normal",
    CREATIVE: "Creative"
}


# Human-readable default schedule
default_ranges = {
    "Monday": [
        ("9:00 AM", "11:00 AM"),
        ("11:30 AM", "1:00 PM"),
        ("2:45 PM", "5:00 PM"),
        ("7:00 PM", "9:15 PM")
    ]
}


# Create all 96 15-minute time slots
time_series = np.arange(96)

empty_schedule = np.zeros((96, 7), dtype=int)

week_df = pd.DataFrame(
    empty_schedule,
    columns=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ],
    index=time_series
)


def _to_timeslot(idx):

    hour = idx // 4 if idx <= 51 else (idx - 48) // 4

    if idx <= 3:
        hour = 12

    remainder = idx % 4

    suffix = "AM" if idx < 48 else "PM"

    return (
        str(hour)
        + ":"
        + str(remainder * 15).zfill(2)
        + " "
        + suffix
    )


# Maps:
# 0 -> "12:00 AM"
# 1 -> "12:15 AM"
# ...
# 95 -> "11:45 PM"
timeslot_conv = {
    i: _to_timeslot(i)
    for i in range(96)
}

def validate_ranges(ranges):

    time_to_slot = {
        value: key
        for key, value in timeslot_conv.items()
    }

    for start, end in ranges:

        if start not in time_to_slot or end not in time_to_slot:
            return False

        start_slot = time_to_slot[start]
        end_slot = time_to_slot[end]

        if start_slot >= end_slot:
            return False

    return True

class TimeTable:

    def __init__(self, month=0, starting_slots=0, rest_day=None):

        self.month = month
        self.starting_slots = starting_slots
        self.rest_day = rest_day
        self.week_df = week_df.copy()
        self.default_ranges = {
            day: [
                ("9:00 AM", "11:00 AM"),
                ("11:30 AM", "1:00 PM"),
                ("2:45 PM", "5:00 PM"),
                ("7:00 PM", "9:15 PM")
            ]
            for day in self.week_df.columns
        }

        self.populate_defaults()


    def populate_defaults(self):

        # Reverse lookup:
        # "9:00 AM" -> 36
        # "11:00 AM" -> 44
        time_to_slot = {
            value: key
            for key, value in timeslot_conv.items()
        }

        for day, ranges in self.default_ranges.items():

            for start, end in ranges:

                start_slot = time_to_slot[start]
                end_slot = time_to_slot[end]

                self.week_df.loc[
                    start_slot:end_slot - 1,
                    day
                ] = 1

    def assign_slots(self, day, ranges, slot_type=NORMAL):

        if not validate_ranges(ranges):
            raise ValueError("Invalid time ranges provided.")

        if slot_type not in calendar_disp_dict:
            raise ValueError("Invalid slot type provided.")

        time_to_slot = {
            value: key
            for key, value in timeslot_conv.items()
        }

        for start, end in ranges:

            start_slot = time_to_slot[start]
            end_slot = time_to_slot[end]

            self.week_df.loc[
                start_slot:end_slot - 1,
                day
            ] = slot_type         

    def calc_residual(self, weekday):

        # =========================
        # NORMAL SLOTS
        # =========================

        normal_required = DAILY_NORMAL_SLOTS * weekday

        if self.rest_day is not None and self.rest_day <= weekday:
            normal_required -= DAILY_NORMAL_SLOTS

        normal_required += self.starting_slots

        normal_used = (
            self.week_df.iloc[:, :weekday] == NORMAL
        ).sum().sum()

        normal_residual = normal_required - normal_used


        # =========================
        # CREATIVE SLOTS
        # =========================

        creative_required = DAILY_CREATIVE_SLOTS * weekday

        creative_used = (
            self.week_df.iloc[:, :weekday] == CREATIVE
        ).sum().sum()

        creative_residual = creative_required - creative_used


        return normal_residual, creative_residual

if __name__ == "__main__":

    timetable = TimeTable()

    print(timeslot_conv)

    print(timetable.week_df)
