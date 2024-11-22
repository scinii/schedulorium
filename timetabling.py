from amplpy import AMPL, add_to_path
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt, patches
from matplotlib.ticker import (AutoMinorLocator, FixedFormatter, FixedLocator)

def courseLecturerMatrix(filepathCourses, block):

    """
    :param filepathCourses: the filepath for the Excel file containing the offered courses.
    :param block: the trimester that we want to find the course lecture matrix for (it is the name of the Excel sheet).
    :return: a data frame (matrix) in which the rows are courses and columns are lecturers. If the i,j component is 1
             then lecturer j is teaching course i. Otherwise, it is 0.
    """

    coursesDf = pd.read_excel(filepathCourses, sheet_name=block)
    courses = list(pd.read_excel(filepathCourses, sheet_name=block)["Subject"])
    lecturers = list(coursesDf["Lecturer"])
    lecturerCourse = pd.Series(coursesDf.Lecturer.values,index = coursesDf.Subject)
    matrix = np.zeros((len(lecturers), len(courses)))
    for i in range(len(lecturers)):
        for j in range(len(courses)):
            if lecturers[i] == lecturerCourse.iloc[j]:
                matrix[i,j] = 1
    matrixDf = pd.DataFrame(matrix, columns = courses, index = lecturers)

    return matrixDf

def generateTimetable(filepathCourses,filepathRooms,block,filepathAmpl,scalingCoefficients):

    """
    :param filepathCourses: the filepath for the Excel file containing the offered courses.
    :param filepathRooms: the filepath for the Excel file containing the Rooms.
    :param block: the trimester/block that we want to find the timetable for.
    :param filepathAmpl: the filepath for the AMPL file.
    :param scalingCoefficients: coefficients for the three sub-objectives.
    :return: six dictionaries with the following structure (courseCode, Day , Timeslot, Room, Lecturer): scheduledState.
             The scheduledState takes value 1 if the event is scheduled and 0 otherwise.
    """

    roomsDf = pd.read_excel(filepathRooms)
    coursesDf = pd.read_excel(filepathCourses, sheet_name=block)


    # SETS

    coursesB1 = list((coursesDf.query("Track1 == 'B1' | Track2 == 'B1'" ))["Subject"]) # Courses first year bachelor
    coursesB2 = list((coursesDf.query("Track1 == 'B2'  | Track2 == 'B2'"))["Subject"]) # Courses common to second years
    coursesBG2 = list((coursesDf.query("Track1 == 'BG2' | Track2 == 'BG2'"))["Subject"]) # courses intended for second year general
    coursesBA2 = list((coursesDf.query("Track1 == 'BA2'  | Track2 == 'BA2'"))["Subject"]) # courses intended for second year applied
    coursesBP2= list((coursesDf.query("Track1 == 'BP2' | Track2 == 'BP2'"))["Subject"]) # courses intended for second year probability
    coursesB3 = list((coursesDf.query("Track1 == 'B3' | Track2 == 'B3'"))["Subject"]) # Courses common to third years
    coursesBG3 = list((coursesDf.query("Track1 == 'BG3' | Track2 == 'BG3'"))["Subject"])  # courses intended for third year probability
    coursesBA3= list((coursesDf.query("Track1 == 'BA3' | Track2 == 'BA3'"))["Subject"]) # courses intended for third year probability
    coursesBP3 = list((coursesDf.query("Track1 == 'BP3' | Track2 == 'BP3'"))["Subject"]) # courses intended for third year probability
    coursesM = list((coursesDf.query("Track1 == 'M' | Track2 == 'M'"))["Subject"]) # Courses common to master students
    coursesMG= list((coursesDf.query("Track1 == 'MG' | Track2 == 'MG'"))["Subject"])  # courses for master general
    coursesMA = list((coursesDf.query("Track1 == 'MA' | Track2 == 'MA'"))["Subject"]) # courses for master applied
    courses = list(coursesDf["Subject"]) # all courses
    days = [1, 2, 3, 4, 5] # days from Monday through Friday
    time = [1, 2, 3, 4, 5] # timeslots within a day
    roomsNormal = list((roomsDf.query("Type == 'LT'"))["Room"]) # rooms used for lectures and tutorials
    roomsLab = list((roomsDf.query("Type == 'LAB'"))["Room"]) # rooms used for computer labs
    rooms = list(roomsDf["Room"]) # all rooms
    lecturers = list(set(coursesDf["Lecturer"])) # all lecturers

    # PARAMETERS

    avaliableSeats = pd.Series(roomsDf.Spots.values,index = roomsDf.Room).to_dict() # capacity for each room
    enrolledStudents = pd.Series(coursesDf.Students.values,index = coursesDf.Subject).to_dict() # enrolled students in each course
    numberLectures1 = pd.Series(coursesDf.Lecture_1.values,index = coursesDf.Subject).to_dict() # number "first" lectures for each course
    numberLectures2 = pd.Series(coursesDf.Lecture_2.values, index=coursesDf.Subject).to_dict() # number "second" lectures for each course
    numberTutorials1 = pd.Series(coursesDf.Tutorial_1.values,index = coursesDf.Subject).to_dict() # number "first" tutorials for each course
    numberTutorials2 = pd.Series(coursesDf.Tutorial_2.values, index=coursesDf.Subject).to_dict() # number "first" tutorials for each course
    numberLabs1 = pd.Series(coursesDf.Lab_1.values,index = coursesDf.Subject).to_dict() # number "first" labs for each course
    numberLabs2 = pd.Series(coursesDf.Lab_2.values, index=coursesDf.Subject).to_dict() # number "first" labs for each course
    numberGroups = pd.Series(coursesDf.Groups.values,index = coursesDf.Subject).to_dict() # number of groups for each course


    # AMPL execution
    schedule = AMPL()
    schedule.read(filepathAmpl)
    schedule.set["C_B1"] = coursesB1
    schedule.set["C_BA2"] = list(set(coursesB2 + coursesBA2))
    schedule.set["C_BG2"] = list(set(coursesB2 + coursesBG2))
    schedule.set["C_BP2"] = list(set(coursesB2 + coursesBP2))
    schedule.set["C_BA3"] = list(set(coursesB3 + coursesBA3))
    schedule.set["C_BG3"] = list(set(coursesB3 + coursesBG3))
    schedule.set["C_BP3"] = list(set(coursesB3 + coursesBP3))
    schedule.set["C_MA"] = list(set(coursesM + coursesMA))
    schedule.set["C_MG"] = list(set(coursesM + coursesMG))
    schedule.set["C"] = courses
    schedule.set["D"] = days
    schedule.set["T"] = time
    schedule.set["R_LT"] = roomsNormal
    schedule.set["R_LAB"] = roomsLab
    schedule.set["R"] = rooms
    schedule.set["L"] = lecturers
    schedule.set["SLOT"] = [(c,d,t,l) for c in courses for d in days for t in time for l in lecturers ]
    schedule.param["n_r"] = avaliableSeats
    schedule.param["n_c"] = enrolledStudents
    schedule.param["n1_lec"] = numberLectures1
    schedule.param["n2_lec"] = numberLectures2
    schedule.param["n1_tut"] = numberTutorials1
    schedule.param["n2_tut"] = numberTutorials2
    schedule.param["n1_lab"] = numberLabs1
    schedule.param["n2_lab"] = numberLabs2
    schedule.param["n_g"] = numberGroups
    schedule.param["scale_f1"] = scalingCoefficients[0]
    schedule.param["scale_f2"] = scalingCoefficients[1]
    schedule.param["scale_f3"] = scalingCoefficients[2]

    if block == '1A' or block == '1B':
        schedule.param["k_present"] = 0.9  # we can always assume that 10% of the students does not show up
    else:
        schedule.param["k_present"] = 0.8  # there are fewer students in the second half of the year
    schedule.param["M"] = courseLecturerMatrix(filepathCourses,block)

    schedule.option["solver"] = "highs"
    schedule.solve()

    lecture1 = schedule.var["x1"].to_dict()
    lecture2 = schedule.var["x2"].to_dict()
    tutorial1 = schedule.var["y1"].to_dict()
    tutorial2 = schedule.var["y2"].to_dict()
    lab1 = schedule.var["z1"].to_dict()
    lab2 = schedule.var["z2"].to_dict()
    roomsUsed = schedule.var["room_used"].to_dict()

    return lecture1,lecture2,tutorial1,tutorial2,lab1,lab2,roomsUsed

def cleanData(eventsDict, eventType):

    """
    :param eventsDict: dictionary as output from timetable_rug.
    :param event_type: type of event (Lecture, Tutorial, Lab)
    :return: a list that contains only the events that are scheduled (those that have a binary variable value equal to 1)
    """

    eventsDf = pd.DataFrame.from_dict([eventsDict]) # convert dictionary to dataframe for easy data manipulation
    eventsDf = eventsDf.round()  # to avoid floating point error
    eventsDf.replace(0, float("NaN"),inplace=True) # replace all 0 values by Nan
    eventsDf.dropna(how='all', axis=1, inplace=True) # remove all elements with value Nan
    cleanedEvents = eventsDf.to_dict(orient='list') # convert dataframe to dictionary

    # construct the list [Course-Code, Day, Timeslot, Room, Lecturer_code if event == 'Lecture' and 'TA' otherwise, event_type].
    if eventType == "Lecture":
         return [list(key) + [eventType] for key, val in cleanedEvents.items()]
    else:
        return [list(key) + ['TA'] + [eventType] for key, val in cleanedEvents.items()]




def separateEvents(day, slot, events, separationKey):

    """
    :param day: the day for which we want the events of.
    :param slot: the timeslots for which we want the events of.
    :param events: list of events.
    :param separationKey: what to separate the events by (either day or timeslot).
    :return: a list of events that happen in a specific day or timeslot.
    """

    if separationKey == "days":
        return [info for info in events if info[1] == day]
    else:
        return [info for info in events if info[2] == slot]




def visualizeTimetable(lecturesDict1, lecturesDict2, tutorialsDict1, tutorialsDict2, labsDict1,labsDict2, roomsUsed):

    """
    :param lecturesDict1: first lectures dictionary.
    :param lecturesDict2: second lectures dictionary.
    :param tutorialsDict1: first tutorials dictionary.
    :param tutorialsDict2: second tutorials dictionary.
    :param labsDict1: first labs dictionary.
    :param labsDict2: second labs dictionary.
    :param roomsUsed: dictionary of rooms used.
    :return: 5 plots (one for each day). In each plot on the x-axis we have the 5 timeslots, on the y-axis we have the rooms used in a specific block.
             In this way a grid is formed. We fill each element of the grid with an event:
             Lectures --> Orange
             Tutorials --> Blue
             Labs --> Purple
    """

    daysOfTheWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] # days of the week
    lectures = cleanData(lecturesDict1, "Lecture") + cleanData(lecturesDict2, "Lecture") # list of all lectures scheduled
    tutorials = cleanData(tutorialsDict1, "Tutorial") + cleanData(tutorialsDict2, "Tutorial") # list of all tutorials scheduled
    labs = cleanData(labsDict1, " Lab") + cleanData(labsDict2, "Lab") # list of all labs happening
    rooms = [key for key in roomsUsed.keys() if roomsUsed[key] > 0.9] # list of all rooms used (we have >0.9 to overcome any floating point errors)

    for k in range(5): # iterate over the days of the week
        dailyLectures = separateEvents(k + 1, "Not required", lectures, "days") # lectures scheduled on day k
        dailyLabs = separateEvents(k + 1, "Not required", labs, "days") # tutorials scheduled on day k
        dailyTutorials = separateEvents(k + 1, "Not required", tutorials, "days") # labs scheduled on day k
        dailyEvents = dailyLectures + dailyLabs + dailyTutorials  # all events schedule on day k

        # Create the figure plot
        fig, ax = plt.subplots(1, 1, figsize=(9, 1 + 0.4 * len(rooms)))
        ax.set_title(str(daysOfTheWeek[k]))
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
            slotEvents = separateEvents("Not required", i + 1, dailyEvents, "slots") # events happening in timeslot i
            numberEvents = len(slotEvents) # number of events happening in timeslot i
            if numberEvents == 0:
                continue # is the number of events in slot i is 0 we go on to the next timeslot

            for j in range(numberEvents): # iterate over the number of events
                event = slotEvents[j] # the j-th event
                roomIndex = rooms.index(event[3]) # room code of event j
                if event[5] == "Lecture":
                    color = "peachpuff" # orange color if event j is a lecture
                elif event[5] == "Tutorial":
                    color = "paleturquoise" # blue color if event j is a tutorial
                else:
                    color = "thistle" # purple color if event j is a lab
                rectangle = patches.Rectangle((i * 0.2, roomIndex / len(rooms)), 0.2, 1 / len(rooms), facecolor=color,edgecolor="black") # rectangle for the slot
                ax.annotate(slotEvents[j][0], (i * 0.2 + 0.035, roomIndex / len(rooms) + (0.3 / len(rooms)))) # write the course code in the rectangle
                ax.add_patch(rectangle)

        ax.yaxis.grid(True, which='major')
        plt.grid(which='major', axis='x')
        plt.show()
    return True
