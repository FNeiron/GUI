# Лабораторная работа 3
## Фазылов Руслан 6233-010402D

## CRM Viewer — PyQt5 & SQLite

Графическое приложение для просмотра и анализа данных CRM-системы на базе SQLite.
### Проект включает:

- сложную учебную CRM-базу данных (crm.db);
- скрипт для её создания и заполнения (init_db.py);
- PyQt5-приложение для просмотра таблиц, выполнения запросов и аналитики (main_crm.py).

### Возможности приложения
#### Подключение к базе

В меню Menu доступны пункты:
- Set connection — подключение к crm.db
- Close connection — закрытие соединения
- После подключения автоматически загружается таблица orders во вкладку Tab1.

### Таблицы CRM базы данных

#### База crm.db включает 5 взаимосвязанных таблиц:
- users — сотрудники компании
- customers — клиенты
- products — товары
- orders — заказы
- order_items — позиции заказов

Структура позволяет выполнять JOIN-запросы, аналитику и агрегирование данных.

### Функциональность интерфейса

Приложение содержит панель кнопок и 5 вкладок (Tab1–Tab5).

- #### bt1 — Orders with Client & Manager
Выполняет JOIN-запрос: заказ → клиент → менеджер
Результат отображается в Tab2.

- #### ComboBox — выбор столбца из таблицы orders
Выполняет:
SELECT <column> FROM orders
Результат отображается в Tab3.

- #### bt2 — Revenue by Country
Показывает аналитику по странам: количество заказов, суммарная выручка, средний чек.
Результат — Tab4.

- #### bt3 — Top Products
Показывает аналитику по товарам: количество продаж и суммарная выручка.
Результат — Tab5.

### Файлы проекта

project/
│ main_crm.py — приложение PyQt5
│ init_db.py — создание crm.db и заполнение данными
│ crm.db — созданная база данных
│ README.md — описание проекта

### Установка и запуск

Установить зависимости:
```
pip install pyqt5
```


Создать базу данных:
```
python init_db.py
```


Запустить приложение:
```
python main_crm.py
```

### Пример SQL-запросов

Топ менеджеров по выручке:

```sql
SELECT u.name, SUM(o.amount) AS revenue
FROM orders o
JOIN users u ON u.id = o.user_id
GROUP BY u.id
ORDER BY revenue DESC;
```


Продажи по категориям:

```sql
SELECT p.category, SUM(oi.qty * p.price) AS revenue
FROM order_items oi
JOIN products p ON p.id = oi.product_id
GROUP BY p.category;
```

### Возможные улучшения

- выполнение произвольных SQL-запросов;
- экспорт результатов в CSV/XLSX;
- графики;
- выбор файла базы через диалог;
- фильтрация заказов по датам.

## Пример работы

<img width="1087" height="618" alt="image" src="https://github.com/user-attachments/assets/dec56588-aafd-40b4-b568-33e240270d7c" />
<img width="1084" height="607" alt="image" src="https://github.com/user-attachments/assets/a7eb6e1c-9182-49b0-a30c-950a2771d9d1" />
<img width="1087" height="614" alt="image" src="https://github.com/user-attachments/assets/9aa9836a-b4f7-4a14-b372-3f0cc7910086" />
<img width="1082" height="625" alt="image" src="https://github.com/user-attachments/assets/c1220538-f566-4f83-924f-1320efe2e6b7" />
<img width="1098" height="624" alt="image" src="https://github.com/user-attachments/assets/ab0abd06-9bfa-4b66-bafd-ca9ee2e83a8e" />
<img width="1090" height="624" alt="image" src="https://github.com/user-attachments/assets/15837e35-d938-4833-89a7-f74d11048c51" />
