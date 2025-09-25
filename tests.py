import unittest
from contextlib import contextmanager
from io import StringIO
import sys
from main import Student, Faculty, StudentDatabase, StudentFieldMask, StudentFieldBitMask, print_student, print_student_bitmask


@contextmanager
def captured_output():
    """Capture stdout for testing print functions"""
    new_out = StringIO()
    old_out = sys.stdout
    try:
        sys.stdout = new_out
        yield new_out
    finally:
        sys.stdout = old_out


class TestStudent(unittest.TestCase):
    """Unit tests for Student class"""
    
    def test_student_creation(self):
        """Test Student object creation with all properties"""
        student = Student(20, "John", 4.5, Faculty.CS, True)
        
        self.assertEqual(student.age, 20)
        self.assertEqual(student.name, "John")
        self.assertEqual(student.average_grade, 4.5)
        self.assertEqual(student.faculty, Faculty.CS)
        self.assertTrue(student.is_leader)
    
    def test_student_properties_immutable(self):
        """Test that student properties are read-only"""
        student = Student(21, "Jane", 3.8, Faculty.MATH, False)
        
        # Properties should be accessible
        self.assertEqual(student.age, 21)
        self.assertEqual(student.name, "Jane")
        self.assertEqual(student.average_grade, 3.8)
        self.assertEqual(student.faculty, Faculty.MATH)
        self.assertFalse(student.is_leader)


class TestFaculty(unittest.TestCase):
    """Unit tests for Faculty enum"""
    
    def test_faculty_values(self):
        """Test Faculty enum has correct string values"""
        self.assertEqual(Faculty.MATH.value, "Math")
        self.assertEqual(Faculty.PHYSICS.value, "Physics")
        self.assertEqual(Faculty.CS.value, "Computer Science")
    
    def test_faculty_enum_members(self):
        """Test Faculty enum has all expected members"""
        faculties = list(Faculty)
        self.assertEqual(len(faculties), 3)
        self.assertIn(Faculty.MATH, faculties)
        self.assertIn(Faculty.PHYSICS, faculties)
        self.assertIn(Faculty.CS, faculties)


class TestStudentDatabase(unittest.TestCase):
    """Unit tests for StudentDatabase class"""
    
    def setUp(self):
        """Set up test database with sample data"""
        self.db = StudentDatabase()
        self.student1 = Student(20, "Alice", 4.2, Faculty.CS, True)
        self.student2 = Student(22, "Bob", 3.7, Faculty.MATH, False)
    
    def test_database_creation(self):
        """Test empty database creation"""
        db = StudentDatabase()
        self.assertEqual(len(db._students), 0)
    
    def test_add_student(self):
        """Test adding a single student"""
        self.db.add_student(self.student1)
        self.assertEqual(len(self.db._students), 1)
        self.assertEqual(self.db._students[0], self.student1)
    
    def test_add_multiple_students(self):
        """Test adding multiple students"""
        self.db.add_student(self.student1)
        self.db.add_student(self.student2)
        self.assertEqual(len(self.db._students), 2)
    
    def test_find_by_name_existing(self):
        """Test finding an existing student by name"""
        self.db.add_student(self.student1)
        self.db.add_student(self.student2)
        
        results = self.db.find_by_name("Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Alice")
    
    def test_find_by_name_non_existing(self):
        """Test finding a non-existing student by name"""
        self.db.add_student(self.student1)
        
        results = self.db.find_by_name("Charlie")
        self.assertEqual(len(results), 0)
    
    def test_find_by_name_multiple_matches(self):
        """Test finding multiple students with same name"""
        student3 = Student(19, "Alice", 4.0, Faculty.PHYSICS, False)
        self.db.add_student(self.student1)  # Alice
        self.db.add_student(student3)       # Also Alice
        
        results = self.db.find_by_name("Alice")
        self.assertEqual(len(results), 2)
        for student in results:
            self.assertEqual(student.name, "Alice")


class TestStudentFieldMask(unittest.TestCase):
    """Unit tests for StudentFieldMask class"""
    
    def test_mask_creation(self):
        """Test creating a boolean field mask"""
        mask = StudentFieldMask(True, False, True, False, True)
        
        self.assertTrue(mask.include_age)
        self.assertFalse(mask.include_name)
        self.assertTrue(mask.include_average_grade)
        self.assertFalse(mask.include_faculty)
        self.assertTrue(mask.include_is_leader)
    
    def test_mask_all_true(self):
        """Test mask with all fields enabled"""
        mask = StudentFieldMask(True, True, True, True, True)
        
        self.assertTrue(mask.include_age)
        self.assertTrue(mask.include_name)
        self.assertTrue(mask.include_average_grade)
        self.assertTrue(mask.include_faculty)
        self.assertTrue(mask.include_is_leader)
    
    def test_mask_all_false(self):
        """Test mask with all fields disabled"""
        mask = StudentFieldMask(False, False, False, False, False)
        
        self.assertFalse(mask.include_age)
        self.assertFalse(mask.include_name)
        self.assertFalse(mask.include_average_grade)
        self.assertFalse(mask.include_faculty)
        self.assertFalse(mask.include_is_leader)


class TestStudentFieldBitMask(unittest.TestCase):
    """Unit tests for StudentFieldBitMask enum"""
    
    def test_bitmask_values(self):
        """Test that bit mask values are powers of 2"""
        self.assertEqual(StudentFieldBitMask.NONE, 0)
        self.assertEqual(StudentFieldBitMask.AGE, 1)
        self.assertEqual(StudentFieldBitMask.NAME, 2)
        self.assertEqual(StudentFieldBitMask.AVERAGE_GRADE, 4)
        self.assertEqual(StudentFieldBitMask.FACULTY, 8)
        self.assertEqual(StudentFieldBitMask.IS_LEADER, 16)
    
    def test_bitmask_or_operation(self):
        """Test OR operation on bit masks"""
        combined = StudentFieldBitMask.AGE | StudentFieldBitMask.NAME
        self.assertEqual(combined, 3)  # 1 + 2 = 3
    
    def test_bitmask_and_operation(self):
        """Test AND operation on bit masks"""
        mask1 = StudentFieldBitMask.AGE | StudentFieldBitMask.NAME
        mask2 = StudentFieldBitMask.NAME | StudentFieldBitMask.FACULTY
        
        result = mask1 & mask2
        self.assertEqual(result, StudentFieldBitMask.NAME)
    
    def test_bitmask_checking(self):
        """Test checking if specific field is in mask"""
        mask = StudentFieldBitMask.AGE | StudentFieldBitMask.FACULTY
        
        self.assertTrue(mask & StudentFieldBitMask.AGE)
        self.assertFalse(mask & StudentFieldBitMask.NAME)
        self.assertTrue(mask & StudentFieldBitMask.FACULTY)


class TestPrintFunctions(unittest.TestCase):
    """Unit tests for print functions"""
    
    def setUp(self):
        """Set up test student"""
        self.student = Student(20, "Test", 4.5, Faculty.CS, True)
    
    def test_print_student_with_all_fields(self):
        """Test printing student with all fields enabled"""
        mask = StudentFieldMask(True, True, True, True, True)
        
        with captured_output() as output:
            print_student(self.student, mask)
        
        result = output.getvalue()
        self.assertIn("Student Info:", result)
        self.assertIn("Name: Test", result)
        self.assertIn("Age: 20", result)
        self.assertIn("Average Grade: 4.5", result)
        self.assertIn("Faculty: Computer Science", result)
        self.assertIn("Is Leader: True", result)
    
    def test_print_student_with_no_fields(self):
        """Test printing student with no fields enabled"""
        mask = StudentFieldMask(False, False, False, False, False)
        
        with captured_output() as output:
            print_student(self.student, mask)
        
        result = output.getvalue().strip()
        self.assertEqual(result, "Student Info:")
    
    def test_print_student_with_selective_fields(self):
        """Test printing student with some fields enabled"""
        mask = StudentFieldMask(True, False, True, False, False)  # age and grade only
        
        with captured_output() as output:
            print_student(self.student, mask)
        
        result = output.getvalue()
        self.assertIn("Age: 20", result)
        self.assertIn("Average Grade: 4.5", result)
        self.assertNotIn("Name:", result)
        self.assertNotIn("Faculty:", result)
        self.assertNotIn("Is Leader:", result)
    
    def test_print_student_bitmask_all_fields(self):
        """Test printing student with bitmask - all fields"""
        mask = (StudentFieldBitMask.AGE | StudentFieldBitMask.NAME | 
                StudentFieldBitMask.AVERAGE_GRADE | StudentFieldBitMask.FACULTY | 
                StudentFieldBitMask.IS_LEADER)
        
        with captured_output() as output:
            print_student_bitmask(self.student, mask)
        
        result = output.getvalue()
        self.assertIn("Name: Test", result)
        self.assertIn("Age: 20", result)
        self.assertIn("Average Grade: 4.5", result)
        self.assertIn("Faculty: Computer Science", result)
        self.assertIn("Is Leader: True", result)
    
    def test_print_student_bitmask_no_fields(self):
        """Test printing student with empty bitmask"""
        with captured_output() as output:
            print_student_bitmask(self.student, StudentFieldBitMask.NONE)
        
        result = output.getvalue().strip()
        self.assertEqual(result, "Student Info:")
    
    def test_print_student_bitmask_selective_fields(self):
        """Test printing student with selective bitmask"""
        mask = StudentFieldBitMask.AGE | StudentFieldBitMask.FACULTY
        
        with captured_output() as output:
            print_student_bitmask(self.student, mask)
        
        result = output.getvalue()
        self.assertIn("Age: 20", result)
        self.assertIn("Faculty: Computer Science", result)
        self.assertNotIn("Name:", result)
        self.assertNotIn("Average Grade:", result)
        self.assertNotIn("Is Leader:", result)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)