import itertools

def generate_timetable(teachers, classes, time_slots):
    timetable = {}

    for time_slot in time_slots:
        timetable[time_slot] = {}

        # Use itertools.cycle to cycle through teachers in a round-robin fashion
        teacher_cycle = itertools.cycle(teachers)

        for _class in classes:
            teacher = next(teacher_cycle)
            timetable[time_slot][_class] = teacher

    return timetable

def print_timetable(timetable):
    for time_slot, class_assignments in timetable.items():
        print(f"\nTime Slot: {time_slot}")
        for _class, teacher in class_assignments.items():
            print(f"Class {_class}: Teacher {teacher}")

if __name__ == "__main__":
    # Example data
    teachers = ["Teacher1", "Teacher2", "Teacher3", "Teacher4", "Teacher5"]
    classes = range(1, 11)
    time_slots = ["9:00 AM", "10:00 AM", "11:00 AM", "1:00 PM", "2:00 PM"]

    # Generate timetable
    timetable = generate_timetable(teachers, classes, time_slots)

    # Print the generated timetable
    print_timetable(timetable)
