# SETS

set C_B1;  # set of courses for first year bachelor
set C_BA2; # set of courses for second year bachelor: applied track
set C_BG2; # set of courses for second year bachelor: general track
set C_BP2; # set of courses for second year bachelor: probability track
set C_BA3; # set of courses for third year bachelor: applied track
set C_BG3; # set of courses for third year bachelor: general track
set C_BP3; # set of courses for third year bachelor: probability track
set C_MA;  # set of courses for master students: applied track
set C_MG;  # set of courses for master students: general track
set C; # set of all courses
set D; # set of days: Monday to Friday respectively (1,2,3,4,5).
set T; # set of timeslots (1,2,3,4,5).
set R_LT; # set of rooms for tutorials and lectures
set R_LAB; # set of rooms for computer labs
set R; # set of all rooms
set L; # set of lecturers
set SLOT within {C,D,T,L}; # cartesian product of the sets C,D,T,L (used to determine if a room has been used or not)

# PARAMETERS

param n_r{R}; # capacity of room r
param n_c{C}; # number of students enrolled in course c
param n1_lec{C}; # 1 if the first lecture for course c takes place, 0 otherwise
param n2_lec{C}; # 1 if the second lecture for course c takes place, 0 otherwise
param n1_tut{C}; # 1 if the first tutorial for course c takes place, 0 otherwise
param n2_tut{C}; # 1 if the second lecture for course c takes place, 0 otherwise
param n1_lab{C}; # 1 if the first lab for course c takes place, 0 otherwise
param n2_lab{C}; # 1 if the second lecture for course c takes place, 0 otherwise
param n_g{C}; # number of groups for course c
param k_present; # cofficient that determines the proportion of student that are present for an event
param M{L,C}; # matrix of size |L| times |C|. If the element 'lc' is 1 then lecturer l is teaching course c. Otherwise it is 0
param scale_f1; # scaling factor for subobjective f_1
param scale_f2; # scaling factor for subobjective f_2
param scale_f3; # scaling factor for subobjective f_3 


# VARIABLES

var x1{C,D,T,R,L} binary; # binary variables with value 1 if course c has the first lecture on day d, in timeslot t, in room r, taught by lecturer l and it is 0 otherwise
var x2{C,D,T,R,L} binary; # as x1 but for the second lecture
var y1{C,D,T,R} binary; # binary variables with value 1 if course c has the first tutorial on day d, in timeslot t, in room r and it is 0 otherwise
var y2{C,D,T,R} binary; # as y1 but for the second tutorial
var z1{C,D,T,R} binary; # as y1 but for the first labs
var z2{C,D,T,R} binary; # as y1 but for the second lab
var u1{C,D,T} binary; # binary variable used to force the first tutorials to happen all at the same time
var u2{C,D,T} binary; # as u1 but for second tutorial
var v1{C,D,T} binary; # as u1 but for the first lab
var v2{C,D,T} binary; # as u1 but for the second lab
var room_used{R} binary; # binary variable with value 1 if room r is used at least one time. Otherwise it is 0


# OBJECTIVE FUNCTION

minimize objective_function: scale_f1*(sum{c in C,d in D, r in R, l in L}(x1[c,d,5,r,l]+x2[c,d,5,r,l]+y1[c,d,5,r]+y2[c,d,5,r]+z1[c,d,5,r]+z2[c,d,5,r]))
							+ scale_f2*(sum{c in C, d in D, t in T, r in R} (sum{l in L}((n_r[r]-k_present*n_c[c])*(x1[c,d,t,r,l]+x2[c,d,t,r,l])) + (n_r[r]-k_present*(n_c[c]/n_g[c]))*(y1[c,d,t,r]+y2[c,d,t,r]) + (n_r[r]-k_present*(n_c[c]/n_g[c]))*(z1[c,d,t,r]+z2[c,d,t,r])))
							+ scale_f3*(sum{r in R} room_used[r]);


# CONSTRAINTS


# Lecturers-Courses Constraints
subject to lectures_1_same_lecturer{c in C,l in L}:sum{d in D, t in T, r in R_LT} x1[c,d,t,r,l] = M[l,c]*n1_lec[c]; # Equation (4.1)
subject to lectures_2_same_lecturer{c in C,l in L}:sum{d in D, t in T, r in R_LT} x2[c,d,t,r,l] = M[l,c]*n2_lec[c];  # Equation (4.2)
subject to lecturer_one_course_per_time_1{t in T, d in D, l in L}: sum{r in R_LT,c in C} x1[c,d,t,r,l] <= 1; # Equation (4.3)
subject to lecturer_one_course_per_time_2{t in T, d in D, l in L}: sum{r in R_LT,c in C} x2[c,d,t,r,l] <= 1 ; # Equation (4.4)


# Courses-Rooms Constraints
subject to lecture_1_in_correct_rooms{c in C, d in D, t in T, r in R_LAB, l in L}: x1[c,d,t,r,l] = 0; # Equation (4.5)
subject to lecture_2_in_correct_rooms{c in C, d in D, t in T, r in R_LAB, l in L}: x2[c,d,t,r,l] = 0; # Equation (4.6)
subject to tutorial_1_in_correct_rooms{c in C, d in D, t in T, r in R_LAB}: y1[c,d,t,r] = 0; # Equation (4.7)
subject to tutorial_2_in_correct_rooms{c in C, d in D, t in T, r in R_LAB}: y2[c,d,t,r] = 0; # Equation (4.8)
subject to lab_1_in_correct_rooms{c in C, d in D, t in T, r in R_LT}: z1[c,d,t,r] = 0; # Equation (4.9)
subject to lab_2_in_correct_rooms{c in C, d in D, t in T, r in R_LT}: z2[c,d,t,r] = 0; # Equation (4.10)


# Rooms Capacity 
subject to lecture_1_capacity{c in C, d in D, t in T, r in R_LT, l in L}: x1[c,d,t,r,l]*k_present*n_c[c] <= n_r[r]; # Equation (4.11)
subject to lecture_2_capacity{c in C, d in D, t in T, r in R_LT, l in L}: x2[c,d,t,r,l]*k_present*n_c[c] <= n_r[r]; # Equation (4.12)
subject to tutorial_1_capacity{c in C, d in D, t in T, r in R_LT}: y1[c,d,t,r]*k_present*ceil(n_c[c]/n_g[c]) <= n_r[r]; # Equation (4.13)
subject to tutorial_2_capacity{c in C, d in D, t in T, r in R_LT}: y2[c,d,t,r]*k_present*ceil(n_c[c]/n_g[c]) <= n_r[r]; # Equation (4.14)
subject to lab_1_capacity{c in C, d in D, t in T, r in R_LAB}: z1[c,d,t,r]*k_present*ceil(n_c[c]/n_g[c]) <= n_r[r]; # Equation (4.15)
subject to lab_2_capacity{c in C, d in D, t in T, r in R_LAB}: z2[c,d,t,r]*k_present*ceil(n_c[c]/n_g[c]) <= n_r[r]; # Equation (4.16)


# Coorect Number of Events
subject to correct_number_tutorials_1{c in C}: sum{d in D, t in T, r in R_LT} y1[c,d,t,r] = n1_tut[c]*n_g[c]; # Equation (4.17)
subject to correct_number_tutorials_2{c in C}: sum{d in D, t in T, r in R_LT} y2[c,d,t,r] = n2_tut[c]*n_g[c]; # Equation (4.18)
subject to correct_numberlabs_1{c in C}: sum{d in D, t in T, r in R_LAB} z1[c,d,t,r] = n1_lab[c]*n_g[c] ; # Equation (4.19)
subject to correct_numberlabs_2{c in C}: sum{d in D, t in T, r in R_LAB} z2[c,d,t,r] = n2_lab[c]*n_g[c]; # Equation (4.20)


# Ordering lectures 
subject to lecture_1_first_half{c in C,d in {4,5}, t in T, r in R_LT, l in L}: x1[c,d,t,r,l] = 0; # Equation (4.21)
subject to lecture_2_second_half_not_friday{c in C,d in {1,2,5}, t in T, r in R_LT, l in L}: x2[c,d,t,r,l] = 0; # Equation (4.22)
subject to lectures_not_same_day{c in C}:sum{t in T,r in R_LT, l in L} (x1[c,3,t,r,l]+x2[c,3,t,r,l]) <= 1; # Equation (4.23)
subject to lectures_one_day_apart{c in C,d in D diff {5}}:sum{t in T,r in R_LT, l in L} (x1[c,d,t,r,l]+x2[c,d+1,t,r,l]) <= 1; # Equation (4.24)


#Unique Allocation and Collisions 
subject to unique_allocation{d in D, t in T, r in R}:(sum{c in C,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+(sum{c in C}(y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])) <= 1; # Equation (4.25)
subject to first_year_collisions{d in D, t in T}:((sum{c in C_B1, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_B1, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.26)
subject to second_year_general_collisions{d in D, t in T}:((sum{c in C_BG2, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_BG2, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.27)
subject to second_year_applied_collisions{d in D, t in T}:((sum{c in C_BA2, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_BA2, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.28)
subject to second_year_probbaility_collisions{d in D, t in T}:((sum{c in C_BP2, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_BP2, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1;  # Equation (4.29)
subject to third_year_general_collisions{d in D, t in T}:((sum{c in C_BG3, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_BG3, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.30)
subject to third_year_applied_collisions{d in D, t in T}:((sum{c in C_BA3, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_BA3, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.31)
subject to third_year_probability_collisions{d in D, t in T}:((sum{c in C_BP3, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_BP3, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.32)
subject to master_general_collisions{d in D, t in T}:((sum{c in C_MG, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_MG, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.33)
subject to master_applied_collisions{d in D, t in T}:((sum{c in C_MA, r in R,l in L} (x1[c,d,t,r,l]+x2[c,d,t,r,l]))+ (sum{c in C_MA, r in R}((y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])/n_g[c]))) <= 1; # Equation (4.34)


# Groups have labs and tutorials at the same time
subject to tutorials_1_same_time{c in C, d in D, t in T}:sum{r in R_LT} y1[c,d,t,r] = u1[c,d,t]*n1_tut[c]*n_g[c]; # Equation (4.35) 
subject to tutorials_2_same_time{c in C, d in D, t in T}:sum{r in R_LT} y2[c,d,t,r] = u2[c,d,t]*n2_tut[c]*n_g[c]; # Equation (4.36)
subject to labs_1_same_time{c in C, d in D,t in T}:sum{r in R_LAB} z1[c,d,t,r] = v1[c,d,t]*n1_lab[c]*n_g[c]; # Equation (4.37)
subject to labs_2_same_time{c in C, d in D,t in T}:sum{r in R_LAB} z2[c,d,t,r] = v2[c,d,t]*n2_lab[c]*n_g[c]; # Equation (4.38)


# Pattern for tutorials and labs
subject to tut_1_after_lec_1{c in C,d in D diff {5}, l  in L}:sum{r in R_LT, t in T} (x1[c,d,t,r,l] - (if (n1_tut[c]=0) then x1[c,d,t,r,l] else (y1[c,d+1,t,r]/n_g[c]) )) <= 0; # Equation (4.39)
subject to tut_2_after_lec_2{c in C,d in D diff {5}, l  in L}:sum{r in R_LT, t in T} (x2[c,d,t,r,l] - (if (n2_tut[c]=0) then x2[c,d,t,r,l] else (y2[c,d+1,t,r]/n_g[c]) )) <= 0; # Equation (4.40)
subject to lab_1_after_lec_1{c in C,d in D diff {5} , l  in L}:sum{r in R, t in T} (if (n1_lab[c]>0 and n1_tut[c]=0) then x1[c,d,t,r,l]-(z1[c,d+1,t,r]/n_g[c])) <= 0; # Equation (4.41)
subject to lab_2_after_lec_2{c in C,d in D diff {5} , l  in L}:sum{r in R, t in T} (if (n2_lab[c]>0 and n2_tut[c]=0) then x2[c,d,t,r,l]-(z2[c,d+1,t,r]/n_g[c])) <= 0; # Equation (4.42)
subject to no_tutorial_1_monday{c in C, t in T, r in R_LT}: y1[c,1,t,r] = 0; # Equation (4.43)
subject to no_tutorial_2_monday{c in C, t in T, r in R_LT}: y2[c,1,t,r] = 0; # Equation (4.44)
subject to no_lab_1_monday{c in C, t in T, r in R_LAB}: z1[c,1,t,r] = 0; # Equation (4.45)
subject to no_lab_2_monday{c in C, t in T, r in R_LAB}: z2[c,1,t,r] = 0; # Equation (4.46)
subject to lab_1_after_tutorial_1{c in C,d in D, t in T diff {1}}:sum{r in R} (z1[c,d,t,r]- (if (n1_lab[c]=0) then z1[c,d,t,r] else y1[c,d,t-1,r] )) <= 0; # Equation (4.47)
subject to lab2_2_after_tutorial_2{c in C,d in D, t in T diff {1}}:sum{r in R} (z2[c,d,t,r]- (if (n2_lab[c]=0) then z2[c,d,t,r] else y2[c,d,t-1,r] )) <= 0; # Equation (4.48)
subject to lab_1_no_first_period_if_tutorial_before{c in C, d in D, r in R_LAB}: (if (n1_tut[c] > 0) then z1[c,d,1,r] else 0) = 0; # Equation (4.49)
subject to lab_2_no_first_period_if_tutorial_before{c in C, d in D, r in R_LAB}: (if (n2_tut[c] > 0) then z2[c,d,1,r] else 0 )= 0; # Equation (4.50)

# Room used
subject to rooms_used{r in R}: sum{c in C, d in D, t in T, l in L}(x1[c,d,t,r,l]+x2[c,d,t,r,l]) + (sum{c in C, d in D, t in T}(y1[c,d,t,r]+y2[c,d,t,r]+z1[c,d,t,r]+z2[c,d,t,r])) <= card(SLOT) * room_used[r]; # Equation (4.51)


















