"""
Examination Seating Arrangement System Using Rule-Based Student Allocation
==========================================================================

Pure Python, standard constructs only: no recursion, no AI/ML, no database,
no external libraries, no randomness (same input -> same seating plan).

SEATING MODEL
    Each room is a single row of seats numbered 1..capacity.
    Seats n and n+1 in the same room are "adjacent".

RULES ENFORCED
    1. Adjacent students must be from different SECTIONS.
    2. Adjacent students must be writing different SUBJECTS.
    3. Room capacity is never exceeded.
    4. Every eligible student gets exactly one seat.
    5. No seat is given to two students.
    6. A student with a preferred room is seated there if a valid seat exists.
    7. Students with special requirements get priority seats only.
    8. Each room's plan shows its invigilator.
    9. Fully deterministic allocation.
   10. Seat look-up by roll number.

ALGORITHM (all steps are plain loops)
    1. check_capacity()       - total seats >= number of students?
    2. group_students()       - group students by section (sorted by roll no.)
    3. arrange_students()     - interleave the section groups round-robin so
                                neighbouring students in the queue differ in
                                section; then order the queue as
                                special -> preferred-room -> everyone else.
    4. assign_seats()         - for each student in the queue, pick candidate
                                rooms (preferred room first, else the room with
                                most free seats), then the first free seat
                                (priority seats only for special students)
                                that passes check_seat_constraints().
    5. validate_arrangement() - independent re-check of every rule.
"""


# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------

def load_sample_rooms():
    """Return the 4 sample examination rooms."""
    return [
        {"room_no": 101, "capacity": 8, "invigilator": "Dr. A. Sharma",
         "priority_seats": [1, 2]},
        {"room_no": 102, "capacity": 8, "invigilator": "Prof. R. Iyer",
         "priority_seats": [1, 2]},
        {"room_no": 103, "capacity": 7, "invigilator": "Dr. S. Menon",
         "priority_seats": [1, 2]},
        {"room_no": 104, "capacity": 7, "invigilator": "Prof. K. Das",
         "priority_seats": [1, 2]},
    ]


def load_sample_students():
    """Return 24 sample students: 4 sections, 4 subjects,
    3 preferred-room students, 3 special-requirement students."""
    sections = ["A", "B", "C", "D"]
    subjects = ["Maths", "Physics", "Chemistry", "English"]
    names = [
        "Aarav Mehta", "Diya Nair", "Kabir Singh", "Ishita Rao",
        "Rohan Gupta", "Ananya Iyer", "Vihaan Shah", "Meera Joshi",
        "Arjun Verma", "Sneha Pillai", "Aditya Kulkarni", "Priya Reddy",
        "Karan Malhotra", "Tanvi Desai", "Yash Patel", "Riya Banerjee",
        "Siddharth Jain", "Neha Kapoor", "Harsh Vardhan", "Pooja Menon",
        "Dev Choudhary", "Kavya Bhat", "Manav Arora", "Simran Kaur",
    ]
    preferred = {2403: 102, 2410: 104, 2409: 103}   # roll -> preferred room
    special = [2402, 2409, 2420]                    # need priority seats

    students = []
    for idx in range(24):
        roll = 2401 + idx
        students.append({
            "roll": roll,
            "name": names[idx],
            "section": sections[idx % 4],
            "subject": subjects[(idx % 4 + idx // 4) % 4],
            "preferred_room": preferred.get(roll),
            "special": roll in special,
        })
    return students


# ---------------------------------------------------------------------------
# STUDENT MANAGEMENT
# ---------------------------------------------------------------------------

def find_student(students, roll):
    """Return the student dict with this roll number, or None."""
    for s in students:
        if s["roll"] == roll:
            return s
    return None


def add_student(students, roll, name, section, subject,
                preferred_room=None, special=False):
    """Add a student. Returns (True, message) or (False, reason)."""
    if find_student(students, roll) is not None:
        return False, "Roll number %s already exists." % roll
    students.append({
        "roll": roll, "name": name.strip(), "section": section.strip().upper(),
        "subject": subject.strip().title(),
        "preferred_room": preferred_room, "special": special,
    })
    return True, "Student %s added." % roll


def remove_student(students, roll):
    """Remove a student by roll number. Returns (True, msg) / (False, msg)."""
    s = find_student(students, roll)
    if s is None:
        return False, "Roll number %s not found." % roll
    students.remove(s)
    return True, "Student %s removed." % roll


def display_students(students):
    """Print the student list in roll-number order."""
    print("\n%-6s %-18s %-4s %-10s %-9s %-7s" %
          ("Roll", "Name", "Sec", "Subject", "Pref.Room", "Special"))
    print("-" * 60)
    for s in sorted(students, key=lambda x: x["roll"]):
        pref = s["preferred_room"] if s["preferred_room"] else "-"
        print("%-6s %-18s %-4s %-10s %-9s %-7s" %
              (s["roll"], s["name"], s["section"], s["subject"], pref,
               "Yes" if s["special"] else "No"))
    print("Total students:", len(students))


def validate_students(students, rooms):
    """Check input data. Returns a list of problem strings (empty = OK)."""
    problems = []
    seen = []
    room_numbers = [r["room_no"] for r in rooms]
    for s in students:
        if s["roll"] in seen:
            problems.append("Duplicate roll number %s." % s["roll"])
        seen.append(s["roll"])
        if not s["name"]:
            problems.append("Roll %s has no name." % s["roll"])
        if not s["section"]:
            problems.append("Roll %s has no section." % s["roll"])
        if not s["subject"]:
            problems.append("Roll %s has no subject." % s["roll"])
        if s["preferred_room"] is not None and \
                s["preferred_room"] not in room_numbers:
            problems.append("Roll %s prefers unknown room %s." %
                            (s["roll"], s["preferred_room"]))
    return problems


# ---------------------------------------------------------------------------
# CAPACITY
# ---------------------------------------------------------------------------

def calculate_room_capacity(rooms):
    """Total number of seats across all rooms."""
    total = 0
    for r in rooms:
        total += r["capacity"]
    return total


def check_capacity(students, rooms):
    """Return (ok, total_seats, total_students)."""
    seats = calculate_room_capacity(rooms)
    return seats >= len(students), seats, len(students)


# ---------------------------------------------------------------------------
# SORTING / GROUPING
# ---------------------------------------------------------------------------

def group_students(students):
    """Group students by section. Returns a list of (section, [students]),
    sections in alphabetical order, students in roll-number order."""
    sections = []
    for s in students:
        if s["section"] not in sections:
            sections.append(s["section"])
    sections.sort()

    groups = []
    for sec in sections:
        members = [s for s in students if s["section"] == sec]
        members.sort(key=lambda x: x["roll"])
        groups.append((sec, members))
    return groups


def arrange_students(students):
    """Build the allocation queue.

    Step 1: interleave section groups round-robin (A, B, C, D, A, B, ...).
    Step 2: stable-sort so special students come first, then students with a
            preferred room, then everyone else.  Sorting is stable, so the
            round-robin order is kept inside each tier.
    """
    groups = group_students(students)
    queue = []
    position = 0
    longest = 0
    for _, members in groups:
        if len(members) > longest:
            longest = len(members)
    while position < longest:
        for _, members in groups:
            if position < len(members):
                queue.append(members[position])
        position += 1

    def tier(s):
        if s["special"]:
            return 0
        if s["preferred_room"] is not None:
            return 1
        return 2

    queue.sort(key=tier)
    return queue


# ---------------------------------------------------------------------------
# CONSTRAINT CHECKING
# ---------------------------------------------------------------------------

def check_seat_constraints(seats, index, student, student_lookup):
    """Can `student` sit at list position `index` (0-based) of `seats`?
    seats holds roll numbers or None.  Returns (ok, reason)."""
    if seats[index] is not None:
        return False, "seat occupied"
    for nb in (index - 1, index + 1):
        if 0 <= nb < len(seats) and seats[nb] is not None:
            other = student_lookup[seats[nb]]
            if other["section"] == student["section"]:
                return False, "same section as neighbour"
            if other["subject"] == student["subject"]:
                return False, "same subject as neighbour"
    return True, ""


def candidate_rooms(student, rooms, seating):
    """Rooms to try, in order. Preferred room first (if any), then the
    remaining rooms ordered by most free seats (ties -> lower room number)."""
    def free_count(room):
        return len([x for x in seating[room["room_no"]] if x is None])

    others = [r for r in rooms if r["room_no"] != student["preferred_room"]]
    others.sort(key=lambda r: (-free_count(r), r["room_no"]))
    ordered = []
    if student["preferred_room"] is not None:
        for r in rooms:
            if r["room_no"] == student["preferred_room"]:
                ordered.append(r)
    return ordered + others


# ---------------------------------------------------------------------------
# ALLOCATION
# ---------------------------------------------------------------------------

def assign_seats(students, rooms):
    """Allocate every student. Returns (seating, unallocated, notes).

    seating     : {room_no: [roll or None, ...]}  (index 0 = seat 1)
    unallocated : list of (student, reason)
    notes       : {roll: text} for students not placed in their preferred room
    """
    lookup = {s["roll"]: s for s in students}
    seating = {}
    for r in rooms:
        seating[r["room_no"]] = [None] * r["capacity"]

    unallocated = []
    notes = {}

    for s in arrange_students(students):
        placed = False
        for room in candidate_rooms(s, rooms, seating):
            seats = seating[room["room_no"]]
            if s["special"]:
                positions = [p - 1 for p in room["priority_seats"]
                             if 1 <= p <= room["capacity"]]
                positions.sort()
            else:
                positions = list(range(room["capacity"]))
            for idx in positions:
                ok, _ = check_seat_constraints(seats, idx, s, lookup)
                if ok:
                    seats[idx] = s["roll"]
                    placed = True
                    break
            if placed:
                if s["preferred_room"] is not None and \
                        room["room_no"] != s["preferred_room"]:
                    notes[s["roll"]] = ("Preferred room %s had no valid seat"
                                        % s["preferred_room"])
                break
        if not placed:
            if s["special"]:
                why = "no valid priority seat available"
            else:
                why = "no valid seat available"
            unallocated.append((s, why))

    return seating, unallocated, notes


# ---------------------------------------------------------------------------
# VALIDATION OF THE FINAL ARRANGEMENT
# ---------------------------------------------------------------------------

def validate_arrangement(students, rooms, seating, unallocated):
    """Independently re-check every rule. Returns a list of violations."""
    errors = []
    lookup = {s["roll"]: s for s in students}
    room_by_no = {r["room_no"]: r for r in rooms}
    where = {}                                   # roll -> (room, seat)

    for r in rooms:
        seats = seating[r["room_no"]]
        if len(seats) > r["capacity"]:                         # capacity
            errors.append("Room %s over capacity." % r["room_no"])
        for i in range(len(seats)):
            roll = seats[i]
            if roll is None:
                continue
            if roll in where:                                  # unique student
                errors.append("Roll %s seated twice." % roll)
            where[roll] = (r["room_no"], i + 1)
            if i + 1 < len(seats) and seats[i + 1] is not None:  # adjacency
                a, b = lookup[roll], lookup[seats[i + 1]]
                if a["section"] == b["section"]:
                    errors.append("Room %s seats %d-%d: same section %s." %
                                  (r["room_no"], i + 1, i + 2, a["section"]))
                if a["subject"] == b["subject"]:
                    errors.append("Room %s seats %d-%d: same subject %s." %
                                  (r["room_no"], i + 1, i + 2, a["subject"]))

    skipped = [u[0]["roll"] for u in unallocated]
    for s in students:                                         # everyone placed
        if s["roll"] not in where and s["roll"] not in skipped:
            errors.append("Roll %s has no seat." % s["roll"])

    for roll in where:
        s = lookup[roll]
        room_no, seat_no = where[roll]
        if s["special"] and seat_no not in room_by_no[room_no]["priority_seats"]:
            errors.append("Special student %s not on a priority seat." % roll)
        pref = s["preferred_room"]
        if pref is not None and room_no != pref:
            # allowed only if the preferred room truly has no valid seat
            seats = seating[pref]
            for i in range(len(seats)):
                if s["special"] and (i + 1) not in room_by_no[pref]["priority_seats"]:
                    continue
                ok, _ = check_seat_constraints(seats, i, s, lookup)
                if ok:
                    errors.append("Roll %s not in preferred room %s although "
                                  "seat %d was valid." % (roll, pref, i + 1))
                    break
    return errors


# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------

def display_seating_plan(students, rooms, seating):
    """Print the room-wise seating arrangement with invigilator names."""
    lookup = {s["roll"]: s for s in students}
    for r in rooms:
        print("\n" + "=" * 70)
        print("ROOM %s   |   Invigilator: %s   |   Capacity: %d" %
              (r["room_no"], r["invigilator"], r["capacity"]))
        print("=" * 70)
        print("%-5s %-6s %-18s %-4s %-10s %s" %
              ("Seat", "Roll", "Name", "Sec", "Subject", "Remarks"))
        print("-" * 70)
        seats = seating[r["room_no"]]
        for i in range(len(seats)):
            seat_no = i + 1
            remark = "Priority seat" if seat_no in r["priority_seats"] else ""
            if seats[i] is None:
                print("%-5d %-6s %-18s %-4s %-10s %s" %
                      (seat_no, "-", "(empty)", "-", "-", remark))
            else:
                s = lookup[seats[i]]
                extra = []
                if s["special"]:
                    extra.append("Special")
                if s["preferred_room"] is not None:
                    extra.append("Pref. room")
                if extra:
                    remark = (remark + " | " if remark else "") + ", ".join(extra)
                print("%-5d %-6s %-18s %-4s %-10s %s" %
                      (seat_no, s["roll"], s["name"], s["section"],
                       s["subject"], remark))


def generate_room_summary(students, rooms, seating):
    """Print a one-line-per-room summary plus section/subject counts."""
    lookup = {s["roll"]: s for s in students}
    print("\n" + "=" * 70)
    print("ROOM-WISE SUMMARY")
    print("=" * 70)
    print("%-6s %-15s %-5s %-6s %-6s %-8s" %
          ("Room", "Invigilator", "Cap", "Used", "Empty", "Special"))
    print("-" * 70)
    grand_used = 0
    for r in rooms:
        seats = seating[r["room_no"]]
        used = [lookup[x] for x in seats if x is not None]
        n_special = len([s for s in used if s["special"]])
        grand_used += len(used)
        print("%-6s %-15s %-5d %-6d %-6d %-8d" %
              (r["room_no"], r["invigilator"], r["capacity"], len(used),
               r["capacity"] - len(used), n_special))
        sec_count, sub_count = {}, {}
        for s in used:
            sec_count[s["section"]] = sec_count.get(s["section"], 0) + 1
            sub_count[s["subject"]] = sub_count.get(s["subject"], 0) + 1
        print("       Sections:", ", ".join("%s=%d" % (k, sec_count[k])
                                            for k in sorted(sec_count)))
        print("       Subjects:", ", ".join("%s=%d" % (k, sub_count[k])
                                            for k in sorted(sub_count)))
    print("-" * 70)
    print("Total seated: %d / %d seats" % (grand_used,
                                           calculate_room_capacity(rooms)))


# ---------------------------------------------------------------------------
# SEARCH
# ---------------------------------------------------------------------------

def find_student_seat(students, rooms, seating, roll):
    """Return a dict with the student's details and seat, or None."""
    s = find_student(students, roll)
    if s is None:
        return None
    for r in rooms:
        seats = seating[r["room_no"]]
        for i in range(len(seats)):
            if seats[i] == roll:
                return {"name": s["name"], "section": s["section"],
                        "subject": s["subject"], "room": r["room_no"],
                        "seat": i + 1, "invigilator": r["invigilator"]}
    return {"name": s["name"], "section": s["section"],
            "subject": s["subject"], "room": None, "seat": None,
            "invigilator": None}


def search_student(students, rooms, seating):
    """Ask for a roll number and print the student's seat details."""
    text = input("Enter roll number: ").strip()
    if not text.isdigit():
        print("Roll number must be numeric.")
        return
    info = find_student_seat(students, rooms, seating, int(text))
    if info is None:
        print("No student with roll number", text)
    elif info["room"] is None:
        print("%s (%s, %s) has NOT been allocated a seat yet." %
              (info["name"], info["section"], info["subject"]))
    else:
        print("\n  Student Name : %s" % info["name"])
        print("  Section      : %s" % info["section"])
        print("  Subject      : %s" % info["subject"])
        print("  Room         : %s (Invigilator: %s)" %
              (info["room"], info["invigilator"]))
        print("  Seat Number  : %d" % info["seat"])


# ---------------------------------------------------------------------------
# DRIVER
# ---------------------------------------------------------------------------

def generate_plan(students, rooms):
    """Run the full pipeline and print status. Returns (seating, unalloc, notes)."""
    problems = validate_students(students, rooms)
    if problems:
        print("\nInput problems found:")
        for p in problems:
            print("  -", p)
        return None, None, None

    ok, seats, count = check_capacity(students, rooms)
    print("\nTotal capacity: %d seats | Students: %d" % (seats, count))
    if not ok:
        print("WARNING: not enough seats for every student (%d short)." %
              (count - seats))

    seating, unallocated, notes = assign_seats(students, rooms)

    errors = validate_arrangement(students, rooms, seating, unallocated)
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
    else:
        print("Validation passed: all seating rules satisfied.")

    for s, why in unallocated:
        print("UNALLOCATED: %s (%s) - %s" % (s["roll"], s["name"], why))
    for roll in sorted(notes):
        print("NOTE: roll %s - %s" % (roll, notes[roll]))
    return seating, unallocated, notes


def read_int(prompt):
    """Read an integer; return None if input is not numeric."""
    text = input(prompt).strip()
    if text.lstrip("-").isdigit():
        return int(text)
    return None


def add_student_menu(students):
    roll = read_int("Roll number: ")
    if roll is None:
        print("Roll number must be numeric.")
        return
    name = input("Name: ")
    section = input("Section: ")
    subject = input("Subject: ")
    pref_text = input("Preferred room (blank for none): ").strip()
    pref = int(pref_text) if pref_text.isdigit() else None
    special = input("Special requirement? (y/n): ").strip().lower() == "y"
    print(add_student(students, roll, name, section, subject, pref, special)[1])


def main():
    rooms = load_sample_rooms()
    students = load_sample_students()
    seating = None

    seating, _, _ = generate_plan(students, rooms)

    while True:
        print("\n--------- EXAM SEATING SYSTEM ---------")
        print(" 1. Display students")
        print(" 2. Add student")
        print(" 3. Remove student")
        print(" 4. (Re)generate seating plan")
        print(" 5. Display seating plan")
        print(" 6. Room-wise summary")
        print(" 7. Search student seat by roll number")
        print(" 8. Check reproducibility (run twice and compare)")
        print(" 0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            display_students(students)
        elif choice == "2":
            add_student_menu(students)
        elif choice == "3":
            roll = read_int("Roll number to remove: ")
            if roll is None:
                print("Roll number must be numeric.")
            else:
                print(remove_student(students, roll)[1])
        elif choice == "4":
            seating, _, _ = generate_plan(students, rooms)
        elif choice in ("5", "6", "7"):
            if seating is None:
                print("Generate a seating plan first (option 4).")
            elif choice == "5":
                display_seating_plan(students, rooms, seating)
            elif choice == "6":
                generate_room_summary(students, rooms, seating)
            else:
                search_student(students, rooms, seating)
        elif choice == "8":
            first = assign_seats(students, rooms)[0]
            second = assign_seats(students, rooms)[0]
            print("Identical arrangements:", first == second)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
