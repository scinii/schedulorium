from matplotlib import pyplot as plt, patches
import pandas as pd
from matplotlib.ticker import (AutoMinorLocator, FixedFormatter, FixedLocator)
import numpy as np
from timetable_rug import timetable


def clean_data(events_dictionary, event_type):

    """
    :param events_dictionary: dictionary that comes out from the timetable_rug program
    :param event_type: type of event (Lecture, Tutorial, Lab)
    :return: a list that contains only the events that are scheduled (those that have a binary variable value equal to 1)
    """

    events_df = pd.DataFrame.from_dict([events_dictionary]) # convert dictionary to dataframe for easy data manipulation
    events_df = events_df.round()  # to avoid floating point error
    events_df.replace(0, float("NaN"),inplace=True) # replace all 0 values by Nan
    events_df.dropna(how='all', axis=1, inplace=True) # remove all elements with value Nan
    dicto = events_df.to_dict(orient='list') # convert dataframe to dictionary

    # construct the list [Course-Code, Day, Timeslot, Room, Lecturer_code if event == 'Lecture' and 'TA' otherwise, event_type].
    if event_type == "Lecture":
        final_list = [list(key) + [event_type] for key, val in dicto.items()]  #
    else:
        final_list = [list(key) + ['TA'] + [event_type] for key, val in dicto.items()]

    return final_list


def separate_events(day, slot, events, what_to_separate):

    """
    :param day: the day for which we want the events of
    :param slot: the timeslots for which we want the events of
    :param events: list of events
    :param what_to_separate: separate the events by "days" or timeslots
    :return: a list of events that happen in a specific day or timeslot
    """

    if what_to_separate == "days":
        day_plan = [info for info in events if info[1] == day]
        return day_plan
    else:
        slot_plan = [info for info in events if info[2] == slot]
        return slot_plan



def visualize_timetable(lectures_dict1, lectures_dict2, tutorials_dict1, tutorials_dict2, labs_dict1,labs_dict2, rooms_used):

    """
    :param lectures_dict1: first lecture dictionary
    :param lectures_dict2: second lecture dictionary
    :param tutorials_dict1: first tutorial dictionary
    :param tutorials_dict2: second tutorial dictionary
    :param labs_dict1: first lab dictionary
    :param labs_dict2: second lab dictionary
    :param rooms_used: dictionary of rooms used
    :return: 5 plots (one for each day). In each plot on the x-axis we have the 5 timeslots, on the y-axis we have the rooms used in a specific block.
             In this way a grid is formed. We fill each element of the grid with an event:
             Lectures --> Orange
             Tutorials --> Blue
             Labs --> Purple
    """

    days_of_the_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] # days of the week
    lectures = clean_data(lectures_dict1, "Lecture") + clean_data(lectures_dict2, "Lecture") # list of all lectures scheduled
    tutorials = clean_data(tutorials_dict1, "Tutorial") + clean_data(tutorials_dict2, "Tutorial") # list of all tutorials scheduled
    labs = clean_data(labs_dict1, " Lab") + clean_data(labs_dict2, "Lab") # list of all labs happening
    rooms = [key for key in rooms_used.keys() if rooms_used[key] > 0.9] # list of all rooms used (we have >0.9 to overcome any floating point errors)

    for k in range(5): # iterate over the days of the week
        lectures_day = separate_events(k + 1, "Not required", lectures, "days") # lectures scheduled on day k
        labs_day = separate_events(k + 1, "Not required", labs, "days") # tutorials scheduled on day k
        tutorials_day = separate_events(k + 1, "Not required", tutorials, "days") # labs scheduled on day k
        all_events_day = lectures_day + labs_day + tutorials_day # all events schedule on day k

        # Create the figure plot
        fig, ax = plt.subplots(1, 1, figsize=(9, 1 + 0.4 * len(rooms)))
        ax.set_title(str(days_of_the_week[k]))
        plt.tick_params(
            axis='x',
            which='major',
            bottom=False,
            labelbottom=False)
        plt.tick_params(
            axis='y',
            which='major',
            left=False,
            color='r',
            labelleft=False)
        def timeslots_formatter(val, pos):
            start = 9 + 2 * pos
            end = 11 + 2 * pos
            return str(start) + ':' + str(end)
        ax.xaxis.set_minor_locator((AutoMinorLocator(2)))
        ax.xaxis.set_minor_formatter(timeslots_formatter)
        y_minor_ticks = list(np.arange(0 + 0.5 / len(rooms), 1, 1 / len(rooms)))
        y_major_ticks = list(np.arange(0, 1 + 0.5 / len(rooms), 1 / len(rooms)))
        ax.yaxis.set_major_locator(FixedLocator(y_major_ticks))
        ax.yaxis.set_minor_locator(FixedLocator(y_minor_ticks))
        ax.yaxis.set_minor_formatter(FixedFormatter(rooms))


        for i in range(5): # iterate over the timeslots
            slot_events = separate_info("Not required", i + 1, all_events_day, "slots") # events happening in timeslot i
            number_events = len(slot_events) # number of events happening in timeslot i
            if number_events == 0:
                continue # is the number of events in slot i is 0 we go on to the next timeslot

            for j in range(number_events): # iterate over the number of events
                event = slot_events[j] # the j-th event
                room_index = rooms.index(event[3]) # room code of event j
                if event[5] == "Lecture":
                    color = "peachpuff" # orange color if event j is a lecture
                elif event[5] == "Tutorial":
                    color = "paleturquoise" # blue color if event j is a tutorial
                else:
                    color = "thistle" # purple color if event j is a lab
                rectangle = patches.Rectangle((i * 0.2, room_index / len(rooms)), 0.2, 1 / len(rooms), facecolor=color,edgecolor="black") # rectangle for the slot
                ax.annotate(slot_events[j][0], (i * 0.2 + 0.035, room_index / len(rooms) + (0.3 / len(rooms)))) # write the course code in the rectangle
                ax.add_patch(rectangle)

        ax.yaxis.grid(True, which='major')
        plt.grid(which='major', axis='x')
        plt.show()
    return True
