#Examination Seating Arrangement System

A **rule-based Python project** that automatically generates an
examination seating plan while following section, subject,
room-capacity, preferred-room, and special-seat constraints.

## Project Overview

The system assigns students to seats across multiple examination rooms.
It uses a deterministic allocation process, so the same input data
produces the same seating arrangement.

This project is built using **core Python and standard language
features**. It does not require external libraries, a database, AI/ML,
recursion, or randomisation.

## Features

-   Generate a room-wise examination seating plan.
-   Prevent adjacent students from belonging to the same section.
-   Prevent adjacent students from writing the same subject.
-   Check room capacity before allocation.
-   Give students with special requirements priority-seat access.
-   Try a student's preferred room first when a valid seat is available.
-   Add and remove students.
-   Display student details in roll-number order.
-   Search for a student's room and seat using their roll number.
-   Display room-wise summaries, including invigilator names and seat
    counts.
-   Validate the final arrangement against the seating rules.
-   Check reproducibility by generating the arrangement twice and
    comparing the results.

## Technologies Used

-   **Language:** Python 3
-   **Libraries:** No external libraries required
-   **Concepts:** Lists, dictionaries, functions, loops, sorting,
    conditional statements, and validation

## Project Structure

``` text
Examination-Seating-Arrangement/
│
├── DOC-20261123-WA0004.py
└── README.md
```

You may rename the Python file to `exam_seating_system.py` if you prefer
a shorter filename. If you do, use the renamed file when running the
project.

## How to Run

1.  Install Python 3 on your computer.
2.  Download or clone this repository.
3.  Open a terminal in the project folder.
4.  Run:

``` bash
python DOC-20261123-WA0004.py
```

On some systems, use:

``` bash
python3 DOC-20261123-WA0004.py
```

## Menu Options

When the program starts, it displays the following menu:

  Option   Function
  -------- ----------------------------------------------
  1        Display students
  2        Add student
  3        Remove student
  4        Generate or regenerate the seating plan
  5        Display the seating plan
  6        Display the room-wise summary
  7        Search for a student's seat by roll number
  8        Check whether the allocation is reproducible
  0        Exit the program

## Sample Data

The program starts with sample data:

-   **Rooms:** 101, 102, 103, and 104
-   **Total room capacity:** 30 seats
-   **Sample students:** 24
-   **Sections:** A, B, C, and D
-   **Subjects:** Maths, Physics, Chemistry, and English
-   **Priority seats:** Seats 1 and 2 in each room

The sample data is defined in `load_sample_rooms()` and
`load_sample_students()` and can be changed in the Python source file.

## Seating Rules

1.  Adjacent students in the same room must belong to different
    sections.
2.  Adjacent students in the same room must be writing different
    subjects.
3.  A room's capacity must not be exceeded.
4.  A student can be assigned no more than one seat.
5.  A student with a special requirement can only be assigned a priority
    seat.
6.  A preferred room is tried first; another room may be used if no
    valid seat is available in the preferred room.
7.  The final arrangement is independently checked by the validation
    function.

**Note:** A student may remain unallocated if no seat satisfies the
applicable constraints. The program reports unallocated students rather
than silently breaking the seating rules.

## Main Program Functions

  -----------------------------------------------------------------------
  Function                            Purpose
  ----------------------------------- -----------------------------------
  `load_sample_rooms()`               Loads the sample room details

  `load_sample_students()`            Loads the sample student details

  `add_student()`                     Adds a student after checking for a
                                      duplicate roll number

  `remove_student()`                  Removes a student by roll number

  `check_capacity()`                  Checks whether total room capacity
                                      is sufficient

  `group_students()`                  Groups students by section

  `arrange_students()`                Creates the student allocation
                                      queue

  `assign_seats()`                    Assigns students to valid seats

  `validate_arrangement()`            Checks the completed seating plan

  `display_seating_plan()`            Displays the room-wise seating
                                      arrangement

  `generate_room_summary()`           Displays room usage and
                                      section/subject counts

  `find_student_seat()`               Finds a student's allocated seat

  `generate_plan()`                   Runs the validation and allocation
                                      process
  -----------------------------------------------------------------------

## Algorithm (Overview)

1.  Load room and student information.
2.  Validate the student data.
3.  Check the total available room capacity.
4.  Group students by section and arrange the allocation queue.
5.  Give allocation priority to students with special requirements,
    followed by students with preferred rooms.
6.  Search for a seat that satisfies the adjacency and priority-seat
    rules.
7.  Validate the completed arrangement.
8.  Display the seating plan, any unallocated students, and relevant
    notes.

## Limitations

-   The current version uses sample data stored directly in the Python
    file.
-   It does not use a database or save changes to a file.
-   The seating model treats each room as a single row of seats;
    adjacent seats are consecutive seat numbers in that row.
-   The program is a command-line application, not a graphical user
    interface.

## Future Improvements

-   Add file-based student and room data storage.
-   Create a graphical user interface.
-   Export seating plans to PDF or Excel.
-   Support multiple rows and columns of seats.
-   Add automated test cases.

## Author

**Bidisha Biswas**

------------------------------------------------------------------------

If you find this project useful, feel free to ⭐ the repository!



