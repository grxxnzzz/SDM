from __future__ import annotations
from typing import Protocol, Dict, Any, Callable, List, Optional
import io
import unittest

# -----------------------
# Контекст
# -----------------------
class Context:
    """
    Контейнер для передачи данных между шагами. 
    Это просто обёртка над dict с некоторыми удобными методами.
    """
    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = dict(initial or {})

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def items(self):
        return self._data.items()

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"Context({self._data})"

# -----------------------
# Интерфейс шага (абстракция + полиморфизм)
# -----------------------
class PipelineStep(Protocol):
    """
    Интерфейс указывающий, что шаг должен уметь делать:
    - execute(context): выполнять операцию, модифицируя Context
    - describe(builder): добавлять текстовое описание шага в builder (для интроспекции)
    """
    def execute(self, context: Context) -> None: ...
    def describe(self, builder: io.StringIO) -> None: ...

# -----------------------
# Простейший шаг: функция как стратегия
# -----------------------
class FuncStep:
    """
    Шаг, который инкапсулирует произвольную функцию action(context).
    Это реализация паттерна Strategy: поведение передаётся как параметр.
    """
    def __init__(self, name: str, action: Callable[[Context], None]) -> None:
        self.name = name
        self.action = action

    def execute(self, context: Context) -> None:
        self.action(context)

    def describe(self, builder: io.StringIO) -> None:
        builder.write(f"FuncStep: {self.name}\n")

# -----------------------
# Адаптер: адаптируем старую функцию с другой сигнатурой к PipelineStep
# -----------------------
class LegacyAdapter:
    """
    Пример адаптера. Допустим есть legacy_func(data_dict, extra) -> modifies dict.
    Адаптер оборачивает её и делает совместимой с PipelineStep.
    """
    def __init__(self, name: str, legacy_func: Callable[[Dict[str, Any], Any], None], extra: Any = None) -> None:
        self.name = name
        self.legacy_func = legacy_func
        self.extra = extra

    def execute(self, context: Context) -> None:
        # Преобразуем Context в plain dict, вызываем legacy и возвращаем изменения в Context
        data = context.to_dict()
        self.legacy_func(data, self.extra)
        for k, v in data.items():
            context.set(k, v)

    def describe(self, builder: io.StringIO) -> None:
        builder.write(f"LegacyAdapter: {self.name} (wraps legacy_func)\n")

# -----------------------
# Декоратор: выполняет до/после обёрнутого шага
# -----------------------
class BeforeAfterDecorator:
    """
    Декоратор шага: выполняет "before" действие, затем оригинальный шаг, затем "after".
    Подходит для логирования, измерения времени, трассировки и т.п.
    """
    def __init__(self, step: PipelineStep, before: Optional[Callable[[Context], None]] = None,
                 after: Optional[Callable[[Context], None]] = None, name: Optional[str] = None) -> None:
        self._step = step
        self.before = before
        self.after = after
        self.name = name or f"BeforeAfter({getattr(step, 'name', step.__class__.__name__)})"

    def execute(self, context: Context) -> None:
        if self.before:
            self.before(context)
        self._step.execute(context)
        if self.after:
            self.after(context)

    def describe(self, builder: io.StringIO) -> None:
        builder.write(f"Decorator: {self.name}\n")
        builder.write("  wraps -> ")
        self._step.describe(builder)

# -----------------------
# Декоратор: вложенный pipeline как шаг
# -----------------------
class NestedPipelineStep:
    """
    Позволяет вставлять целый Pipeline как шаг внутри другого Pipeline.
    Реализация паттерна Декоратор/Composite.
    """
    def __init__(self, name: str, pipeline: 'Pipeline') -> None:
        self.name = name
        self.pipeline = pipeline

    def execute(self, context: Context) -> None:
        self.pipeline.execute(context)

    def describe(self, builder: io.StringIO) -> None:
        builder.write(f"NestedPipelineStep: {self.name}\n")
        self.pipeline.describe(builder, indent=2)

# -----------------------
# Singleton (метакласс)
# -----------------------
class SingletonMeta(type):
    """
    Простейшая реализация синглтона на уровне метакласса.
    Полезно для шагов без состояния, чтобы не создавать их каждый раз.
    """
    _instances: Dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

class SingletonStep(metaclass=SingletonMeta):
    """
    Пример шага-синглтона. Он реализует PipelineStep интерфейс.
    """
    def __init__(self) -> None:
        self.name = "SingletonNoOp"

    def execute(self, context: Context) -> None:
        # Ничего не делает, пример шага без состояния.
        pass

    def describe(self, builder: io.StringIO) -> None:
        builder.write(f"SingletonStep: {self.name}\n")

# -----------------------
# Pipeline (хранит шаги как данные)
# -----------------------
class Pipeline:
    """
    Класс, управляющий последовательностью шагов. Data-oriented: операции со шагами
    — обычные методы (добавить/вставить/удалить), шаги хранятся в списке.
    """
    def __init__(self) -> None:
        self._steps: List[PipelineStep] = []

    def add_step(self, step: PipelineStep) -> None:
        self._steps.append(step)

    def insert_step(self, index: int, step: PipelineStep) -> None:
        self._steps.insert(index, step)

    def remove_step(self, step: PipelineStep) -> None:
        self._steps.remove(step)

    def execute(self, context: Context) -> None:
        for step in self._steps:
            step.execute(context)

    def describe(self, builder: io.StringIO, indent: int = 0) -> None:
        prefix = " " * indent
        builder.write(f"{prefix}Pipeline with {len(self._steps)} steps:\n")
        for i, step in enumerate(self._steps, 1):
            builder.write(f"{prefix} {i}. ")
            step.describe(builder)

# -----------------------
# Интроспекция: helper функции
# -----------------------
def pipeline_to_string(pipeline: Pipeline) -> str:
    """
    Собирает описание pipeline в единый текст и возвращает.
    """
    buf = io.StringIO()
    pipeline.describe(buf)
    return buf.getvalue()

def print_pipeline(pipeline: Pipeline) -> None:
    """
    Печатает описание pipeline (обёртка).
    """
    print(pipeline_to_string(pipeline))

# -----------------------
# Примеры действий (для тематического pipeline: обработка текста)
# -----------------------
def load_text_action(context: Context) -> None:
    # Простая загрузка: из context['src'] либо из строки по умолчанию
    src = context.get('src')
    text = src if isinstance(src, str) else "Default sample text, with SOME punctuation!"
    context.set('text', text)

def normalize_action(context: Context) -> None:
    text = context.get('text', '')
    # Lower + replace punctuation with spaces (очень простая нормализация)
    normalized = ''.join(ch.lower() if ch.isalnum() else ' ' for ch in text)
    context.set('text', normalized)

def tokenize_action(context: Context) -> None:
    text = context.get('text', '')
    tokens = [t for t in text.split() if t]
    context.set('tokens', tokens)

def filter_stopwords_action(context: Context) -> None:
    tokens = context.get('tokens', [])
    stopwords = {'and', 'or', 'the', 'with', 'a', 'an', 'in', 'on', 'of'}
    filtered = [t for t in tokens if t not in stopwords]
    context.set('tokens', filtered)

def join_action(context: Context) -> None:
    tokens = context.get('tokens', [])
    context.set('result', ' '.join(tokens))

# Legacy function example to be адаптирован
def legacy_uppercase(data: Dict[str, Any], extra: Any) -> None:
    # Предполагаем, что legacy изменяет data['text'] на upper()
    if 'text' in data:
        data['text'] = data['text'].upper()

# -----------------------
# Демонстрация конфигурации pipeline в main
# -----------------------
def main_demo() -> None:
    # Создаём контекст с исходным текстом
    ctx = Context({'src': "Hello, World! This is an Example with punctuation."})

    # Создаём pipeline
    pipeline = Pipeline()

    # Добавляем шаги: стратегия (FuncStep)
    pipeline.add_step(FuncStep("LoadText", load_text_action))
    pipeline.add_step(FuncStep("Normalize", normalize_action))
    pipeline.add_step(FuncStep("Tokenize", tokenize_action))

    # Добавим legacy шаг через адаптер (преобразование к верхнему регистру)
    pipeline.add_step(LegacyAdapter("LegacyUpper", legacy_uppercase, extra=None))

    # После legacy мы снова токенизируем (демонстрация вложенности и перестановки шагов)
    pipeline.add_step(FuncStep("Tokenize2", tokenize_action))

    # Декоратор: логируем до и после фильтрации стоп-слов
    def before_log(context: Context) -> None:
        print("Before filter, tokens:", context.get('tokens'))

    def after_log(context: Context) -> None:
        print("After filter, tokens:", context.get('tokens'))

    filter_step = FuncStep("FilterStopwords", filter_stopwords_action)
    decorated_filter = BeforeAfterDecorator(filter_step, before=before_log, after=after_log)
    pipeline.add_step(decorated_filter)

    # Nested pipeline example: небольшой вложенный pipeline собирает результат
    nested = Pipeline()
    nested.add_step(FuncStep("Join", join_action))
    nested_step = NestedPipelineStep("MakeResult", nested)
    pipeline.add_step(nested_step)

    # Singleton example: вставим бездействующий синглтон шаг (показывает, что можно переиспользовать)
    pipeline.add_step(SingletonStep())

    # Интроспекция: печать структуры pipeline
    print("=== Pipeline structure ===")
    print_pipeline(pipeline)

    # Выполнение pipeline
    print("\n=== Executing pipeline ===")
    pipeline.execute(ctx)

    # Результат
    print("\n=== Final context ===")
    print(ctx)

    # Ожидаем, что ctx.get('result') содержит строку с обработанными токенами
    print("\nResult:", ctx.get('result'))

# -----------------------
# Unit tests (basic)
# -----------------------
class TestPipelineBasics(unittest.TestCase):
    def test_text_pipeline(self):
        ctx = Context({'src': "A quick brown fox, and a lazy dog."})
        p = Pipeline()
        p.add_step(FuncStep("Load", load_text_action))
        p.add_step(FuncStep("Normalize", normalize_action))
        p.add_step(FuncStep("Tokenize", tokenize_action))
        p.add_step(FuncStep("Filter", filter_stopwords_action))
        p.add_step(FuncStep("Join", join_action))
        p.execute(ctx)
        result = ctx.get('result')
        # Проверяем базовые свойства результата
        self.assertIsInstance(result, str)
        self.assertIn("quick", result)  # ожидаем, что важные слова остались
        self.assertNotIn(",", result)   # знаки препинания должны быть удалены

    def test_singleton(self):
        s1 = SingletonStep()
        s2 = SingletonStep()
        self.assertIs(s1, s2)  # оба должны быть одним объектом

    def test_adapter(self):
        ctx = Context({'text': "abc"})
        adapter = LegacyAdapter("L", legacy_uppercase, extra=None)
        adapter.execute(ctx)
        self.assertEqual(ctx.get('text'), "ABC")

# -----------------------
# Выполнение демо и тестов если запущено как скрипт
# -----------------------
if __name__ == "__main__":
    # Демонстрация — запускаем для визуальной проверки
    main_demo()

    # Запускаем unit тесты (базовые)
    print("\nRunning unit tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
