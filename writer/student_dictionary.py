# given an array of student names, assign each as the key of a dictionary pointing to an incrementing integer.

def student_keys(names):
    students = {}
    idx = 3
    for name in names:
        students[name] = idx
        idx += 1

    return students
