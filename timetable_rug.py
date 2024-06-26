from amplpy import AMPL, add_to_path
import pandas as pd
import numpy as np

add_to_path(r'C:\Users\rober\AMPL')


def course_lecturer_matrix(block):

    """
    :param block: the trimester that we want to find the course lecture matrix for
    :return: a data frame (matrix) in which the rows are courses and columns are lecturers. If the i,j component is 1
             then lecturer j is teaching course i. Otherwise it is 0.
    """

    courses_df = pd.read_excel('Courses_RUG_Mathematics.xlsx', sheet_name=block)
    courses = list(courses_df["Subject"])
    lecturers = list(courses_df["Lecturer"])
    lecturer_course = pd.Series(courses_df.Lecturer.values,index = courses_df.Subject)
    matrix = np.zeros((len(lecturers), len(courses)))
    for i in range(len(lecturers)):
        for j in range(len(courses)):
            if lecturers[i] == lecturer_course.iloc[j]:
                matrix[i,j] = 1
    matrix_df = pd.DataFrame(matrix, columns = courses, index = lecturers)

    return matrix_df

def timetable(block,scaling_coefficients):

    """
    :param block: the trimester/block that we want to find the timetabeling for
    :param scaling_coefficients: coefficients for the three sub-objectives
    :return: six dictionaries with encoded when and where an event is happening
    """

    rooms_df = pd.read_excel('rooms_data.xlsx')
    courses_df = pd.read_excel('Courses_RUG_Mathematics.xlsx', sheet_name=block)


    # SETS

    courses_B1 = list((courses_df.query("Track1 == 'B1' | Track2 == 'B1'" ))["Subject"]) # Courses first years
    courses_B2 = list((courses_df.query("Track1 == 'B2'  | Track2 == 'B2'"))["Subject"]) # Courses common to second years
    courses_BG2_intended = list((courses_df.query("Track1 == 'BG2' | Track2 == 'BG2'"))["Subject"]) # courses intended for second year general
    courses_BA2_intended = list((courses_df.query("Track1 == 'BA2'  | Track2 == 'BA2'"))["Subject"]) # courses intended for second year applied
    courses_BP2_intended = list((courses_df.query("Track1 == 'BP2' | Track2 == 'BP2'"))["Subject"]) # courses intended for second year probability
    courses_B3 = list((courses_df.query("Track1 == 'B3' | Track2 == 'B3'"))["Subject"]) # Courses common to third years
    courses_BG3_intended = list((courses_df.query("Track1 == 'BG3' | Track2 == 'BG3'"))["Subject"])  # courses intended for third year probability
    courses_BA3_intended = list((courses_df.query("Track1 == 'BA3' | Track2 == 'BA3'"))["Subject"]) # courses intended for third year probability
    courses_BP3_intended = list((courses_df.query("Track1 == 'BP3' | Track2 == 'BP3'"))["Subject"]) # courses intended for third year probability
    courses_M = list((courses_df.query("Track1 == 'M' | Track2 == 'M'"))["Subject"]) # Courses common to master students
    courses_MG_intended = list((courses_df.query("Track1 == 'MG' | Track2 == 'MG'"))["Subject"])  # courses for master general
    courses_MA_intended = list((courses_df.query("Track1 == 'MA' | Track2 == 'MA'"))["Subject"]) # courses for master applied
    all_courses = list(courses_df["Subject"])
    days = [1, 2, 3, 4, 5] # days from Monday through Friday
    time = [1, 2, 3, 4, 5] # timeslots within a day
    room_lec_tut = list((rooms_df.query("Type == 'LT'"))["Room"]) # rooms used for lectures and tutorials
    room_lab = list((rooms_df.query("Type == 'LAB'"))["Room"]) # rooms used for computer labs
    all_rooms = list(rooms_df["Room"])
    lecturers = list(set(courses_df["Lecturer"]))

    # PARAMETERS

    avaliable_seats = pd.Series(rooms_df.Spots.values,index = rooms_df.Room).to_dict() # capacity for each room
    enrolled_students = pd.Series(courses_df.Students.values,index = courses_df.Subject).to_dict() # enrolled students in each course
    number_lectures_1 = pd.Series(courses_df.Lecture_1.values,index = courses_df.Subject).to_dict() # number "first" lectures for each course
    number_lectures_2 = pd.Series(courses_df.Lecture_2.values, index=courses_df.Subject).to_dict() # number "second" lectures for each course
    number_tutorials_1 = pd.Series(courses_df.Tutorial_1.values,index = courses_df.Subject).to_dict() # number "first" tutorials for each course
    number_tutorials_2 = pd.Series(courses_df.Tutorial_2.values, index=courses_df.Subject).to_dict() # number "first" tutorials for each course
    number_labs_1 = pd.Series(courses_df.Lab_1.values,index = courses_df.Subject).to_dict() # number "first" labs for each course
    number_labs_2 = pd.Series(courses_df.Lab_2.values, index=courses_df.Subject).to_dict() # number "first" labs for each course
    number_groups = pd.Series(courses_df.Groups.values,index = courses_df.Subject).to_dict() # number of groups for each course


    # AMPL execution
    schedule = AMPL()
    schedule.read("timetable_AMPL.mod")
    schedule.set["C_B1"] = courses_B1
    schedule.set["C_BA2"] = list(set(courses_B2 + courses_BA2_intended))
    schedule.set["C_BG2"] = list(set(courses_B2 + courses_BG2_intended))
    schedule.set["C_BP2"] = list(set(courses_B2 + courses_BP2_intended))
    schedule.set["C_BA3"] = list(set(courses_B3 + courses_BA3_intended))
    schedule.set["C_BG3"] = list(set(courses_B3 + courses_BG3_intended))
    schedule.set["C_BP3"] = list(set(courses_B3 + courses_BP3_intended))
    schedule.set["C_MA"] = list(set(courses_M + courses_MA_intended))
    schedule.set["C_MG"] = list(set(courses_M + courses_MG_intended))
    schedule.set["C"] = all_courses
    schedule.set["D"] = days
    schedule.set["T"] = time
    schedule.set["R_LT"] = room_lec_tut
    schedule.set["R_LAB"] = room_lab
    schedule.set["R"] = all_rooms
    schedule.set["L"] = lecturers
    schedule.set["SLOT"] = [(c,d,t,l) for c in all_courses for d in days for t in time for l in lecturers ]
    schedule.param["n_r"] = avaliable_seats
    schedule.param["n_c"] = enrolled_students
    schedule.param["n1_lec"] = number_lectures_1
    schedule.param["n2_lec"] = number_lectures_2
    schedule.param["n1_tut"] = number_tutorials_1
    schedule.param["n2_tut"] = number_tutorials_2
    schedule.param["n1_lab"] = number_labs_1
    schedule.param["n2_lab"] = number_labs_2
    schedule.param["n_g"] = number_groups
    schedule.param["scale_f1"] = scaling_coefficients[0]
    schedule.param["scale_f2"] = scaling_coefficients[1]
    schedule.param["scale_f3"] = scaling_coefficients[2]

    if block == '1A' or block == '1B':
        schedule.param["k_present"] = 0.9  # we can always assume that 10% of the students does not show up
    else:
        schedule.param["k_present"] = 0.8  # there are less students in the second half of the year
    schedule.param["M"] = course_lecturer_matrix(block)

    schedule.option["solver"] = "highs"
    schedule.solve()

    lecture1 = schedule.var["x1"].to_dict()
    lecture2 = schedule.var["x2"].to_dict()
    tutorial1 = schedule.var["y1"].to_dict()
    tutorial2 = schedule.var["y2"].to_dict()
    lab1 = schedule.var["z1"].to_dict()
    lab2 = schedule.var["z2"].to_dict()
    rooms_used = schedule.var["room_used"].to_dict()

    return lecture1,lecture2,tutorial1,tutorial2,lab1,lab2,rooms_used

timetable('2B',[1,1,1])