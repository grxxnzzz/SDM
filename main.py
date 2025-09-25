from enum import Enum, IntFlag
from typing import List

# enum for Faculty
class Faculty(Enum):
    MATH: str = "Math"
    PHYSICS: str = "Physics"
    CS: str = "Computer Science"

# Domain Model class
class Student:
    def __init__(self, age: int, name: str, average_grade: float, faculty: Faculty, is_leader: bool):
        self._age = age
        self._name = name
        self._average_grade = average_grade
        self._faculty = faculty
        self._is_leader = is_leader

    @property
    def age(self) -> int:
        return self._age

    @property
    def name(self) -> str:
        return self._name

    @property
    def average_grade(self) -> float:
        return self._average_grade

    @property
    def faculty(self) -> Faculty:
        return self._faculty

    @property
    def is_leader(self) -> bool:
        return self._is_leader

# class: field masks (boolean)
class StudentFieldMask:
    def __init__(self, include_age: bool, include_name: bool, include_average_grade: bool, include_faculty: bool, include_is_leader: bool):
        self.include_age = include_age
        self.include_name = include_name
        self.include_average_grade = include_average_grade
        self.include_faculty = include_faculty
        self.include_is_leader = include_is_leader

# function: print with bool mask 
def print_student(student: Student, mask: StudentFieldMask):
    print("\nStudent Info:")
    if mask.include_name:
        print(f"Name: {student.name}")
    if mask.include_age:
        print(f"Age: {student.age}")
    if mask.include_average_grade:
        print(f"Average Grade: {student.average_grade}")
    if mask.include_faculty:
        print(f"Faculty: {student.faculty.value}")
    if mask.include_is_leader:
        print(f"Is Leader: {student.is_leader}")

### BITS
# class: field masks (bits)
class StudentFieldBitMask(IntFlag):
    NONE = 0                # 0
    AGE = 1 << 0            # 00001 [ 1]
    NAME = 1 << 1           # 00010 [ 2]
    AVERAGE_GRADE = 1 << 2  # 00100 [ 4]
    FACULTY = 1 << 3        # 01000 [ 8]
    IS_LEADER = 1 << 4      # 10000 [16]

# function: print with bit mask 
def print_student_bitmask(student: Student, mask: StudentFieldBitMask):
    print("\nStudent Info:")
    if mask & StudentFieldBitMask.NAME:
        print(f"Name: {student.name}")
    if mask & StudentFieldBitMask.AGE:
        print(f"Age: {student.age}")
    if mask & StudentFieldBitMask.AVERAGE_GRADE:
        print(f"Average Grade: {student.average_grade}")
    if mask & StudentFieldBitMask.FACULTY:
        print(f"Faculty: {student.faculty.value}")
    if mask & StudentFieldBitMask.IS_LEADER:
        print(f"Is Leader: {student.is_leader}")

# functions: combining bit masks
def combine_masks_or(mask1: StudentFieldBitMask, mask2: StudentFieldBitMask) -> StudentFieldBitMask:
    return mask1 | mask2

def combine_masks_and(mask1: StudentFieldBitMask, mask2: StudentFieldBitMask) -> StudentFieldBitMask:
    return mask1 & mask2

def combine_masks_not(mask: StudentFieldBitMask) -> StudentFieldBitMask:
    return ~mask & (StudentFieldBitMask.AGE | StudentFieldBitMask.NAME | StudentFieldBitMask.AVERAGE_GRADE | 
                    StudentFieldBitMask.FACULTY | StudentFieldBitMask.IS_LEADER)

### DATABASE
# abstract database
class StudentDatabase:
    def __init__(self):
        self._students: List[Student] = []

    def add_student(self, student: Student):
        self._students.append(student)

    def find_by_name(self, name: str) -> List[Student]:
        return [student for student in self._students if student.name == name]

# testing the program
if __name__ == "__main__":
    db = StudentDatabase()
    db.add_student(Student(20, "Ion", 4.5, Faculty.CS, True))
    db.add_student(Student(22, "Alex", 3.8, Faculty.MATH, False))
    db.add_student(Student(20, "Ion", 4.0, Faculty.PHYSICS, False))

    # test: boolean mask 
    bool_mask = StudentFieldMask(True, True, False, True, False)
    print("--------------------\nTesting boolean mask:\n--------------------")
    for student in db.find_by_name("Ion"):
        print_student(student, bool_mask)

    # test: bit mask 
    bit_mask = StudentFieldBitMask.AGE | StudentFieldBitMask.NAME | StudentFieldBitMask.FACULTY
    print("\n--------------------\nTesting bit mask:\n--------------------")
    for student in db.find_by_name("Ion"):
        print_student_bitmask(student, bit_mask)

    # test: combined masks
    mask1 = StudentFieldBitMask.AGE | StudentFieldBitMask.NAME
    mask2 = StudentFieldBitMask.FACULTY | StudentFieldBitMask.IS_LEADER
    combined_or = combine_masks_or(mask1, mask2)
    combined_and = combine_masks_and(mask1, mask2)
    combined_not = combine_masks_not(mask1)
    print("\n--------------------\nTesting mask combinations:\n--------------------")
    print(f"OR mask: {combined_or}")
    print(f"AND mask: {combined_and}")
    print(f"NOT mask: {combined_not}")