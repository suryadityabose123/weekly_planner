import pandas as pd
import numpy as np


# =====================================================
# SLOT TYPES
# =====================================================

EMPTY = 0
NORMAL = 1
CREATIVE = 2





calendar_disp_dict = {
    EMPTY: "Plain_White",
    NORMAL: "Normal",
    CREATIVE: "Creative"
}


# =====================================================
# WEEK STRUCTURE
# =====================================================

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


time_series = np.arange(96)


empty_schedule = np.zeros(
    (96, 7),
    dtype=int
)


week_df = pd.DataFrame(
    empty_schedule,
    columns=DAYS,
    index=time_series
)


# =====================================================
# TIME CONVERSION
# =====================================================

def _to_timeslot(idx):

    total_minutes = idx * 15

    hour = (total_minutes // 60) % 24
    minute = total_minutes % 60

    if hour == 0:
        display_hour = 12
        suffix = "AM"

    elif hour < 12:
        display_hour = hour
        suffix = "AM"

    elif hour == 12:
        display_hour = 12
        suffix = "PM"

    else:
        display_hour = hour - 12
        suffix = "PM"

    return (
        f"{display_hour}:"
        f"{str(minute).zfill(2)} "
        f"{suffix}"
    )


timeslot_conv = {
    i: _to_timeslot(i)
    for i in range(96)
}


# =====================================================
# TIME VALIDATION
# =====================================================

def validate_ranges(ranges):

    for start, end in ranges:

        if start < 0 or end > 96:
            return False

        if start >= end:
            return False

    return True


# =====================================================
# TIMETABLE
# =====================================================

class TimeTable:

    def __init__(
        self,
        month=0,
        starting_slots=0,
        rest_day=None,
        daily_normal_slots=32,
        daily_creative_slots=4
    ):

        self.month = month

        self.starting_slots = starting_slots

        # Store the actual day name.
        # Example: "Wednesday"
        self.rest_day = rest_day

        # Kept for compatibility and for the
        # timetable's 96-slot structure.
        self.week_df = week_df.copy()

        # The actual user schedule now lives here.
        self.text_blocks = {
            day: []
            for day in DAYS
        }
        self.daily_normal_slots = daily_normal_slots
        self.daily_creative_slots = daily_creative_slots

    # =================================================
    # ADD BLOCK
    # =================================================

    def add_text_block(
        self,
        day,
        start,
        end,
        block_type="normal",
        text=""
    ):

        if day not in DAYS:
            raise ValueError("Invalid day.")

        if start < 0 or end > 96 or start >= end:
            raise ValueError("Invalid block range.")

        if block_type not in ["normal", "creative"]:
            raise ValueError("Invalid block type.")

        block = {
            "start": int(start),
            "end": int(end),
            "type": block_type,
            "text": text
        }

        self.text_blocks[day].append(block)

        return block


    # =================================================
    # UPDATE BLOCK
    # =================================================

    def update_text_block(
        self,
        day,
        start,
        end,
        block_type=None,
        text=None
    ):

        for block in self.text_blocks[day]:

            if (
                block["start"] == start
                and block["end"] == end
            ):

                if block_type is not None:
                    block["type"] = block_type

                if text is not None:
                    block["text"] = text

                return block

        return None


    # =================================================
    # REMOVE BLOCK
    # =================================================

    def remove_text_block(
        self,
        day,
        start,
        end
    ):

        self.text_blocks[day] = [

            block

            for block in self.text_blocks[day]

            if not (
                block["start"] == start
                and block["end"] == end
            )

        ]


    # =================================================
    # CLEAR DAY BLOCKS
    # =================================================

    def clear_text_blocks(self, day):

        self.text_blocks[day] = []


    # =================================================
    # CHECK BLOCK OVERLAP
    # =================================================

    def block_overlaps(
        self,
        day,
        start,
        end
    ):

        for block in self.text_blocks[day]:

            existing_start = block["start"]
            existing_end = block["end"]

            if (
                start < existing_end
                and end > existing_start
            ):

                return True

        return False


    # =================================================
    # RESIDUAL
    # =================================================

    def calc_residual(self, weekday):

        # weekday is:
        #
        # Monday    = 1
        # Tuesday   = 2
        # ...
        # Sunday    = 7

        days_so_far = DAYS[:weekday]


        # ---------------------------------------------
        # NORMAL REQUIRED
        # ---------------------------------------------

        normal_required = (
            self.daily_normal_slots * weekday
        )


        # Rest day removes one day's normal
        # requirement.

        if self.rest_day in days_so_far:

            normal_required -= self.daily_normal_slots


        # Starting slots are additional slots
        # already available.

        normal_required += self.starting_slots


        # ---------------------------------------------
        # CREATIVE REQUIRED
        # ---------------------------------------------

        creative_required = (
            self.daily_creative_slots * weekday
        )


        # ---------------------------------------------
        # NORMAL USED
        # ---------------------------------------------

        normal_used = 0


        # ---------------------------------------------
        # CREATIVE USED
        # ---------------------------------------------

        creative_used = 0


        for day in days_so_far:

            # Do not count blocks on a rest day.
            if day == self.rest_day:
                continue


            for block in self.text_blocks[day]:

                duration = (
                    block["end"]
                    - block["start"]
                )


                if block["type"] == "normal":

                    normal_used += duration


                elif block["type"] == "creative":

                    creative_used += duration


        normal_residual = (
            normal_required
            - normal_used
        )


        creative_residual = (
            creative_required
            - creative_used
        )


        return (
            normal_residual,
            creative_residual
        )