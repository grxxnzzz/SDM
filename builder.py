from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid
import inspect

# ==================== MUTABLE МОДЕЛИ (для Builder) ====================
class MutableProduct:
    """Изменяемая модель продукта для Builder"""
    def __init__(self):
        self._id: Optional[str] = None
        self._name: Optional[str] = None
    
    @property
    def id(self) -> Optional[str]:
        return self._id
    
    @id.setter
    def id(self, value: str):
        if not value.strip():
            raise ValueError("ID продукта не может быть пустым")
        self._id = value
    
    @property
    def name(self) -> Optional[str]:
        return self._name
    
    @name.setter
    def name(self, value: str):
        if not value.strip() or len(value.strip()) < 2:
            raise ValueError("Название продукта должно содержать минимум 2 символа")
        self._name = value

class MutableOrderItem:
    """Изменяемая модель элемента заказа для Builder"""
    def __init__(self):
        self._product_id: Optional[str] = None
        self._quantity: Optional[int] = None
    
    @property
    def product_id(self) -> Optional[str]:
        return self._product_id
    
    @product_id.setter
    def product_id(self, value: str):
        if not value.strip():
            raise ValueError("ID продукта не может быть пустым")
        self._product_id = value
    
    @property
    def quantity(self) -> Optional[int]:
        return self._quantity
    
    @quantity.setter
    def quantity(self, value: int):
        if value <= 0:
            raise ValueError("Количество должно быть положительным числом")
        self._quantity = value

class MutableOrder:
    """Изменяемая модель заказа для Builder"""
    def __init__(self):
        self._id: Optional[str] = None
        self._items: List[MutableOrderItem] = []
    
    @property
    def id(self) -> Optional[str]:
        return self._id
    
    @id.setter
    def id(self, value: str):
        if not value.strip():
            raise ValueError("ID заказа не может быть пустым")
        self._id = value
    
    def add_item(self, item: MutableOrderItem):
        self._items.append(item)

# ==================== IMMUTABLE МОДЕЛИ (результат Builder) ====================
@dataclass(frozen=True)
class Product:
    """Неизменяемая модель продукта"""
    id: str
    name: str

@dataclass(frozen=True)
class OrderItem:
    """Неизменяемая модель элемента заказа"""
    product_id: str  # Ссылка по ID, а не по объекту
    quantity: int

@dataclass(frozen=True)
class Order:
    """Неизменяемая модель заказа"""
    id: str
    items: List[OrderItem]

# ==================== БАЗА ДАННЫХ ====================
class Database:
    """Простая база данных с ID-ссылками"""
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
    
    def add_product(self, product: Product):
        self.products[product.id] = product
    
    def add_order(self, order: Order):
        self.orders[order.id] = order
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

# ==================== БИЛДЕРЫ ====================
class ProductBuilder:
    """Билдер для создания Product"""
    
    def __init__(self, database: Database):
        self._product = MutableProduct()
        self._database = database
        self._errors: List[str] = []
    
    def set_id(self, product_id: str) -> 'ProductBuilder':
        try:
            self._product.id = product_id
        except ValueError as e:
            self._add_error(f"Строка {self._get_line()}: {e}")
        return self
    
    def set_name(self, name: str) -> 'ProductBuilder':
        try:
            self._product.name = name
        except ValueError as e:
            self._add_error(f"Строка {self._get_line()}: {e}")
        return self
    
    def build(self) -> Product:
        if self._errors:
            raise ValueError("\n".join(self._errors))
        
        if not self._product.id or not self._product.name:
            raise ValueError(f"Строка {self._get_line()}: Не все обязательные поля заполнены")
        
        product = Product(id=self._product.id, name=self._product.name)
        self._database.add_product(product)
        return product
    
    def _add_error(self, error: str):
        self._errors.append(error)
    
    def _get_line(self) -> int:
        return inspect.currentframe().f_back.f_back.f_lineno

class OrderItemBuilder:
    """Билдер для создания OrderItem"""
    
    def __init__(self, database: Database):
        self._item = MutableOrderItem()
        self._database = database
        self._errors: List[str] = []
    
    def set_product_id(self, product_id: str) -> 'OrderItemBuilder':
        try:
            # Проверяем, существует ли продукт в базе
            if not self._database.get_product(product_id):
                raise ValueError(f"Продукт с ID '{product_id}' не найден")
            self._item.product_id = product_id
        except ValueError as e:
            self._add_error(f"Строка {self._get_line()}: {e}")
        return self
    
    def set_quantity(self, quantity: int) -> 'OrderItemBuilder':
        try:
            self._item.quantity = quantity
        except ValueError as e:
            self._add_error(f"Строка {self._get_line()}: {e}")
        return self
    
    def build(self) -> OrderItem:
        if self._errors:
            raise ValueError("\n".join(self._errors))
        
        if not self._item.product_id or not self._item.quantity:
            raise ValueError(f"Строка {self._get_line()}: Не все обязательные поля заполнены")
        
        return OrderItem(
            product_id=self._item.product_id,
            quantity=self._item.quantity
        )
    
    def _add_error(self, error: str):
        self._errors.append(error)
    
    def _get_line(self) -> int:
        return inspect.currentframe().f_back.f_back.f_lineno

class OrderBuilder:
    """Билдер для создания Order"""
    
    def __init__(self, database: Database):
        self._order = MutableOrder()
        self._database = database
        self._items: List[OrderItem] = []
        self._errors: List[str] = []
    
    def set_id(self, order_id: str) -> 'OrderBuilder':
        try:
            self._order.id = order_id
        except ValueError as e:
            self._add_error(f"Строка {self._get_line()}: {e}")
        return self
    
    def add_item(self, item: OrderItem) -> 'OrderBuilder':
        self._items.append(item)
        return self
    
    def build(self) -> Order:
        if self._errors:
            raise ValueError("\n".join(self._errors))
        
        if not self._order.id:
            raise ValueError(f"Строка {self._get_line()}: ID заказа обязателен")
        
        if not self._items:
            raise ValueError(f"Строка {self._get_line()}: Заказ должен содержать хотя бы один товар")
        
        order = Order(id=self._order.id, items=self._items)
        self._database.add_order(order)
        return order
    
    def _add_error(self, error: str):
        self._errors.append(error)
    
    def _get_line(self) -> int:
        return inspect.currentframe().f_back.f_back.f_lineno

# ==================== HIGH-LEVEL КОНФИГУРАТОР ====================
class StoreConfigurator:
    """Высокоуровневый конфигуратор для создания стандартных наборов"""
    
    def __init__(self, database: Database):
        self._db = database
    
    def create_electronics_pack(self) -> Order:
        """Создает заказ с электроникой"""
        # Создаем продукты
        laptop = ProductBuilder(self._db) \
            .set_id("p1") \
            .set_name("Ноутбук") \
            .build()
        
        mouse = ProductBuilder(self._db) \
            .set_id("p2") \
            .set_name("Мышь") \
            .build()
        
        # Создаем элементы заказа
        item1 = OrderItemBuilder(self._db) \
            .set_product_id("p1") \
            .set_quantity(1) \
            .build()
        
        item2 = OrderItemBuilder(self._db) \
            .set_product_id("p2") \
            .set_quantity(3) \
            .build()
        
        # Создаем заказ
        order = OrderBuilder(self._db) \
            .set_id(str(uuid.uuid4())) \
            .add_item(item1) \
            .add_item(item2) \
            .build()
        
        return order

# ==================== ИСПОЛЬЗОВАНИЕ ====================
def main():
    """Демонстрация работы"""
    print("=== СИСТЕМА УПРАВЛЕНИЯ ЗАКАЗАМИ ===\n")
    
    # Создаем базу данных
    db = Database()
    
    # Используем высокоуровневый конфигуратор
    configurator = StoreConfigurator(db)
    order = configurator.create_electronics_pack()
    
    print(f"Заказ создан успешно!")
    print(f"   ID заказа: {order.id}")
    print(f"   Количество товаров: {len(order.items)}")
    
    # Выводим детали заказа
    print("\nДетали заказа:")
    for item in order.items:
        product = db.get_product(item.product_id)
        print(f"   - {product.name}: {item.quantity} шт.")
    
    # Демонстрация валидации с ошибками
    print("\nДемонстрация валидации:")
    try:
        bad_product = ProductBuilder(db) \
            .set_id("") \
            .set_name("A") \
            .build()
    except ValueError as e:
        print("Ошибки при создании продукта:")
        print(e)

if __name__ == "__main__":
    main()