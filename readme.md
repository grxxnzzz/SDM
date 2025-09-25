# Lab 01: Field Mask
## Условие лабораторной работы

[(⊙_⊙;)<br>Оригинальное условие ](https://github.com/AntonC9018/uniCourse_csharp/blob/master/labs/design/01_field_mask.md)

**Основные задания:**
1. Сделайте domain model класс с хотя бы 5 полями, среди которых `int, string, float, enum`.
2. Сделайте абстракцию под базу данных, хранящую эти объекты. 
   Имплементация не принципиальна, можно хранить их просто в массиве под капотом.
3. Создайте класс маски полей (сначала как bool).
4. Реализуйте метод в абстракции базы данных, которая совершает поиск всех объектов по одному из полей (например, `FindByName(string)`).
5. Реализуйте статическую функцию, которая печатает в консоль значения полей, согласно переданной маски.
6. Протестируйте программу.

**Обязательные дополнительные 3 задания (выбранные):**
- Выполните unit test-ы используй фреймворк (xunit).
- Переделайте маску полей на основе битов.
- Сделайте 3 метода, работающие на основе масок, комбинирующих их тем или иным полезным образом.

# Описание

Выбранный язык реализации лабораторной работы: `Python`

Использованы библиотеки: `unittest`

## Класс `Faculty`

### Описание класса

Перечисление факультетов для последующего использования в объектах класса `Student`. Наследует [enum](https://docs.python.org/3/library/enum.html).

```python
class Faculty(Enum):
    MATH: str = "Math"
    PHYSICS: str = "Physics"
    CS: str = "Computer Science"
```

## Класс `Student`

### Описание класса

```python
class Student:
    def __init__(self, age: int, name: str, average_grade: float, faculty: Faculty, is_leader: bool):
        self._age = age
        self._name = name
        self._average_grade = average_grade
        self._faculty = faculty
        self._is_leader = is_leader
```

Класс `Student` описывает сущность "студент" с набором характеристик: 
- ссылка на создаваемый экземпляр класса (`self`)
1. возраст (`age`) 
1. имя (`name`) 
1. средний балл (`average_grade`) 
1. факультет (`faculty`) 
1. является ли старостой (`is_leader`)

### Нижнее подчеркивание (`_age`, `_name`, и т.д.)

Нижнее подчеркивание указывает, что атрибут защищенный (**protected**), но это только всеобщая договоренность чтобы сигнализировать, что атрибут не предназначен для прямого доступа извне.

### @property
 
Декоратор `@property` превращает метод в свойство (геттер), позволяя обращаться к нему как к атрибуту (например, `student.age` вместо `student.age()`), обеспечивая контролируемый доступ к атрибуту `_age` без прямого доступа.

### Методы getter-ы

```Python
@property
    def age(self) -> int:
        return self._age
```

Это определение метода-геттера для свойства `age` с аннотацией `-> int`, указывающей, что метод возвращает целое число. `return self._age` возвращает значение защищенного атрибута, давая доступ к значению без нарушения инкапсуляции.

Остальные getter-ы реализованы идентично.

### Пример использования класса

Создаем экземпляр класса Student

```Python
student = Student(20, "Ion", 4.5, Faculty.CS, True)
print(student.name)
print(student.age)
print(student.faculty)
```
**Нарушение инкапсуляции**

Так сделать возможно, но не рекомендуется ≡(▔﹏▔)≡

```Python
student._age = 18
```

## Класс `StudentFieldMask`

### Описание класса

Представляет маску полей, которая указывает, какие поля объекта `Student` (возраст, имя, средний балл, факультет, староста) должны использоваться, например, для вывода или фильтрации.

```python 
class StudentFieldMask:
    def __init__(self, include_age: bool, include_name: bool, include_average_grade: bool, include_faculty: bool, include_is_leader: bool):
        self.include_age = include_age
        self.include_name = include_name
        self.include_average_grade = include_average_grade
        self.include_faculty = include_faculty
        self.include_is_leader = include_is_leader
```

Конструктор инициализирует маску с заданными значениями (`True` или `False`) для каждого поля. `self.include_age = include_age` хранит информацию о том, включено ли поле `age` в маску. Если `include_age` равно `True`, это означает, что поле `age` будет учитываться, например, при выводе в функции `print_student`.

## Сдвиги по битам

Оператор `<<` — это побитовый сдвиг влево. Он сдвигает биты числа влево на указанное количество позиций, заполняя младшие биты нулями.

> **Например:**<br>
1 `<<` 0 = 00001 (**1** в десятичной системе) <br>
1 `<<` 1 = 00010 (**2** в десятичной системе) <br>
1 `<<` 2 = 00100 (**4** в десятичной системе) <br>
**и так далее.**

### Класс `StudentFieldBitMask`

Каждое значение в `StudentFieldBitMask` соответствует одному биту, что позволяет представлять каждое поле отдельным битом без пересечений значений и комбинировать несколько полей в одной переменной, что эффективнее и удобнее, чем использование отдельных булевых переменных.

> **Пример:**<br>
>Мы хотим включить поля `AGE` и `FACULTY`:<br>
>`AGE` = `00001` (1)<br>
>`FACULTY` = `01000` (8)<br>
>`AGE | FACULTY` = `01001` (9)<br><br>
>Проверяем тогда с помощью побитового AND `&`:<br>
>```python
>mask = StudentFieldBitMask.AGE | StudentFieldBitMask.FACULTY  # >01001
>if mask & StudentFieldBitMask.AGE:  # 01001 & 00001 = 00001 (True)
>    print("AGE included")
>if mask & StudentFieldBitMask.NAME:  # 01001 & 00010 = 00000 >False)
>    print("NAME not included")
>```
>Переменная маски со значением 9 указывает, что нужно включить `AGE` и `FACULTY`.

---

# Unit Tests

## Описание тестирования

Для обеспечения корректности работы всех компонентов системы были написаны unit тесты с использованием стандартной библиотеки `unittest`. Тесты покрывают все основные классы и функции проекта.

### Структура тестов

```
tests.py
├── TestStudent              # Тесты класса Student
├── TestFaculty              # Тесты enum Faculty  
├── TestStudentDatabase      # Тесты класса StudentDatabase
├── TestStudentFieldMask     # Тесты булевой маски
├── TestStudentFieldBitMask  # Тесты битовой маски
└── TestPrintFunctions       # Тесты функций печати
```

## Класс `TestStudent`

Тестирует основную функциональность класса `Student`:

```python
def test_student_creation(self):
    """Test Student object creation with all properties"""
    student = Student(20, "John", 4.5, Faculty.CS, True)
    
    self.assertEqual(student.age, 20)
    self.assertEqual(student.name, "John")
    self.assertEqual(student.average_grade, 4.5)
    self.assertEqual(student.faculty, Faculty.CS)
    self.assertTrue(student.is_leader)
```

**Покрытие:**
- Создание объекта студента
- Корректность всех свойств (`age`, `name`, `average_grade`, `faculty`, `is_leader`)
- Неизменяемость свойств (read-only доступ)

## Класс `TestFaculty`

Проверяет корректность enum `Faculty`:

```python
def test_faculty_values(self):
    """Test Faculty enum has correct string values"""
    self.assertEqual(Faculty.MATH.value, "Math")
    self.assertEqual(Faculty.PHYSICS.value, "Physics")
    self.assertEqual(Faculty.CS.value, "Computer Science")
```

**Покрытие:**
- Правильные строковые значения всех факультетов
- Наличие всех ожидаемых членов enum

## Класс `TestStudentDatabase`

Тестирует функциональность базы данных студентов:

```python
def test_find_by_name_existing(self):
    """Test finding an existing student by name"""
    self.db.add_student(self.student1)
    self.db.add_student(self.student2)
    
    results = self.db.find_by_name("Alice")
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0].name, "Alice")
```

**Покрытие:**
- Создание пустой базы данных
- Добавление одного и нескольких студентов
- Поиск существующих студентов по имени
- Поиск несуществующих студентов
- Обработка множественных совпадений по имени

## Класс `TestStudentFieldMask`

Проверяет работу булевой маски полей:

```python
def test_mask_creation(self):
    """Test creating a boolean field mask"""
    mask = StudentFieldMask(True, False, True, False, True)
    
    self.assertTrue(mask.include_age)
    self.assertFalse(mask.include_name)
    self.assertTrue(mask.include_average_grade)
```

**Покрытие:**
- Создание маски с различными комбинациями флагов
- Проверка корректности установки булевых значений
- Крайние случаи (все поля включены/выключены)

## Класс `TestStudentFieldBitMask`

Тестирует битовую маску и операции над ней:

```python
def test_bitmask_values(self):
    """Test that bit mask values are powers of 2"""
    self.assertEqual(StudentFieldBitMask.NONE, 0)
    self.assertEqual(StudentFieldBitMask.AGE, 1)
    self.assertEqual(StudentFieldBitMask.NAME, 2)
    self.assertEqual(StudentFieldBitMask.AVERAGE_GRADE, 4)
```

**Покрытие:**
- Корректные значения битовых флагов (степени двойки)
- Побитовые операции `OR` (`|`) и `AND` (`&`)
- Проверка наличия конкретных флагов в маске

## Класс `TestPrintFunctions`

Проверяет функции вывода информации о студентах:

### Контекстный менеджер для перехвата вывода

```python
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
```

Этот механизм позволяет перехватывать вывод `print()` функций для последующей проверки в тестах.

### Пример теста функции печати

```python
def test_print_student_with_selective_fields(self):
    """Test printing student with some fields enabled"""
    mask = StudentFieldMask(True, False, True, False, False)
    
    with captured_output() as output:
        print_student(self.student, mask)
    
    result = output.getvalue()
    self.assertIn("Age: 20", result)
    self.assertIn("Average Grade: 4.5", result)
    self.assertNotIn("Name:", result)
```

**Покрытие:**
- Вывод с булевой маской (все поля, без полей, выборочные поля)
- Вывод с битовой маской (различные комбинации)
- Проверка содержимого выводимого текста

## Запуск тестов

```bash
python tests.py
```

### Вывод с verbosity=2

```
test_add_multiple_students (TestStudentDatabase) ... ok
test_add_student (TestStudentDatabase) ... ok
test_database_creation (TestStudentDatabase) ... ok
test_faculty_enum_members (TestFaculty) ... ok
test_faculty_values (TestFaculty) ... ok
test_find_by_name_existing (TestStudentDatabase) ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.003s

OK
```

Параметр `verbosity=2` показывает название каждого выполняемого теста, что удобно для отладки и мониторинга процесса тестирования.

## Принципы тестирования

**Unit тесты** — каждый тест проверяет одну конкретную функциональность в изоляции.

**Arrange-Act-Assert паттерн:**
- **Arrange:** подготовка тестовых данных
- **Act:** выполнение тестируемого кода  
- **Assert:** проверка результатов

**Покрытие:** тесты покрывают все публичные методы и свойства классов, включая граничные случаи.

**Изоляция:** каждый тест независим и не влияет на результаты других тестов благодаря использованию `setUp()` метода.

# Выводы

В ходе выполнения данной лабораторной работы была успешно реализована система управления студентами с применением паттерна **Field Mask** для гибкого отображения информации. Основу системы составляет класс `Student` с инкапсулированными данными, доступ к которым осуществляется через свойства-геттеры, что обеспечивает контролируемый доступ к внутренним полям объекта. База данных `StudentDatabase` реализована как простое хранилище в памяти с базовой функциональностью поиска, демонстрируя принципы работы с коллекциями объектов и list comprehensions в Python.

Ключевой особенностью проекта стала реализация двух подходов к маскированию полей: булевого и битового. Булевая маска `StudentFieldMask` представляет интуитивно понятный способ управления отображением через отдельные флаги для каждого поля, в то время как битовая маска `StudentFieldBitMask` демонстрирует более эффективный подход с использованием побитовых операций и флагов `IntFlag`. Битовый подход позволяет компактно хранить состояние множества полей в одном числе и выполнять быстрые операции объединения, пересечения и инверсии масок через стандартные побитовые операторы.

Практическая ценность работы заключается в освоении фундаментальных концепций объектно-ориентированного программирования, таких как инкапсуляция, использование перечислений и свойств, а также в понимании различных подходов к фильтрации и представлению данных. Написанные unit-тесты с использованием фреймворка `unittest` обеспечивают надежность кода и демонстрируют важность тестирования в процессе разработки. Данная реализация может служить основой для более сложных систем управления данными, где требуется гибкое управление видимостью и форматированием информации.