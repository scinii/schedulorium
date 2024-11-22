
This code accompanies my Bachelor Thesis which focus is on integer programming modeling for the University Course Timetabeling problem at the University of Groningen.

Further details can be found  in the [thesis]( https://fse.studenttheses.ub.rug.nl/33259/1/bMATH2024SchininaR.pdf ) itself.

The main objective is to develop an optimized timetable for university courses, considering constraints such as lecturer schedules, room availability, and student tracks.

The model is designed to optimize the allocation of courses, lectures, tutorials, and (computer) labs to available rooms and timeslots. We use the HiGHS as the optimization solver for the integer programming problem. The entire model is created using Python and AMPL.

## Problem Overview

At the University of Groningen, students are enrolled in one of three main tracks:
- Applied Mathematics
- General Mathematics
- Probability and Statistics

Students in these tracks follow a curriculum where certain courses are mandatory for specific years or specializations. 

### Key Features:
- Curriculum-Based University Course Timetabling : Courses are assigned according to tracks (Applied Mathematics, General Mathematics, Probability and Statistics).
- Room and timeslot optimization: Ensures that each event is scheduled in an appropriate room and timeslot, avoiding overlaps.
- Lecturer assignments: Lecturers are assigned to the courses they are supposed to teach, ensuring no conflicts in their schedules.
- Block-based scheduling: The academic year is divided into four blocks, each requiring specific scheduling considerations.

### Sub-objectives to Optimize:
1. Minimize the number of events scheduled in the late timeslot (17:00–19:00) as this timeslot is less desirable for both students and lecturers.
2. Minimize unused room capacity: Avoids wasting room space, ensuring rooms are used efficiently.
3. Minimize the number of rooms used: Aims to reduce the overall number of rooms required (for a logisitic purpose).


### Data Input:

The model requires input data in the form of Excel files. These files contain:
1. Courses Data: Information about courses, their associated tracks, and the events that need to be scheduled (lectures, tutorials, labs).
2. Room Data Details of the rooms available for scheduling, including capacity and type (lecture halls, computer labs, etc.).

The data files should be structured as follows:
- Courses Excel file: Contains columns like course name, track, number of students, event type, and number of events to be scheduled.
- Rooms Excel file: Contains information such as room name, capacity, and room type (e.g., lecture, computer lab).


A visual output of the end result is shown below where:

* Orange --> Lectures
* Blue   --> Tutorials
* Purple --> Computer Labs

![Sample Output](https://github.com/scinii/timetabling_RUG/blob/main/2A_scaled_wed.png)


## License

[MIT](https://choosealicense.com/licenses/mit/)
