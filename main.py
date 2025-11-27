import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QComboBox, QMenuBar,
    QAction, QHBoxLayout, QMessageBox, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CRM Viewer (PyQt5)")
        self.resize(1100, 600)

        self.conn = None
        self.cursor = None

        # Меню
        menubar = self.menuBar()
        menu = menubar.addMenu("Menu")

        act_connect = QAction("Set connection", self)
        act_connect.triggered.connect(self.set_connection)
        menu.addAction(act_connect)

        act_close = QAction("Close connection", self)
        act_close.triggered.connect(self.close_connection)
        menu.addAction(act_close)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Панель кнопок и контролов
        controls = QHBoxLayout()

        self.bt1 = QPushButton('bt1 "Orders with Client & Manager"')
        self.bt1.clicked.connect(self.query_bt1)
        controls.addWidget(self.bt1)

        controls.addWidget(QLabel("Orders columns:"))
        self.combo = QComboBox()
        self.combo.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.combo.currentIndexChanged.connect(self.query_combo)
        controls.addWidget(self.combo)

        self.bt2 = QPushButton('bt2 "Revenue by Country"')
        self.bt2.clicked.connect(self.query_bt2)
        controls.addWidget(self.bt2)

        self.bt3 = QPushButton('bt3 "Top Products"')
        self.bt3.clicked.connect(self.query_bt3)
        controls.addWidget(self.bt3)

        main_layout.addLayout(controls)

        # Tabs: Tab1..Tab5 (каждая — QTableWidget)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tables = []
        for i in range(5):
            table = QTableWidget()
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)
            self.tabs.addTab(table, f"Tab{i+1}")
            self.tables.append(table)

        # Подсказка в статусбаре
        self.statusBar().showMessage("Ready. Use Menu → Set connection to open crm.db")

    def set_connection(self):
        """Подключаемся к crm.db и загружаем Tab1 и ComboBox"""
        try:
            self.conn = sqlite3.connect("crm.db")
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Не удалось подключиться: {e}")
            return

        try:
            # Tab1: SELECT * FROM orders
            self.cursor.execute("SELECT * FROM orders ORDER BY date DESC LIMIT 200")
            rows = self.cursor.fetchall()
            columns = rows[0].keys() if rows else [d[0] for d in self.cursor.description]
            data = [tuple(r) for r in rows]
            self.show_table(data, list(columns), self.tables[0])
            self.tabs.setCurrentIndex(0)
            self.statusBar().showMessage("Connected to crm.db — orders loaded into Tab1")

            # Заполнить ComboBox колонками таблицы orders
            self.combo.blockSignals(True)
            self.combo.clear()
            self.cursor.execute("PRAGMA table_info(orders)")
            cols_info = self.cursor.fetchall()
            orders_cols = [c[1] for c in cols_info]  # (cid, name, type, ...)
            for col in orders_cols:
                self.combo.addItem(col)
            self.combo.blockSignals(False)

        except Exception as e:
            QMessageBox.warning(self, "Query Error", f"Ошибка при загрузке orders: {e}")

    def close_connection(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
            self.cursor = None
            # очистим таблицы
            for t in self.tables:
                t.clear()
                t.setRowCount(0)
                t.setColumnCount(0)
            self.combo.clear()
            self.statusBar().showMessage("Connection closed")
        else:
            self.statusBar().showMessage("No active connection")

    def query_bt1(self):
        """bt1: показать заказы + имя клиента + имя пользователя (менеджера) + date + amount"""
        if not self.cursor:
            QMessageBox.information(self, "Not connected", "Сначала выполните Set connection")
            return
        q = """
            SELECT o.id AS order_id,
                   c.name AS customer_name,
                   u.name AS user_name,
                   o.amount,
                   o.date
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            LEFT JOIN users u ON o.user_id = u.id
            ORDER BY o.date DESC
            LIMIT 200
        """
        try:
            self.cursor.execute(q)
            rows = self.cursor.fetchall()
            cols = rows[0].keys() if rows else [d[0] for d in self.cursor.description]
            data = [tuple(r) for r in rows]
            self.show_table(data, list(cols), self.tables[1])
            self.tabs.setCurrentIndex(1)
            self.statusBar().showMessage("bt1: orders with client & manager shown in Tab2")
        except Exception as e:
            QMessageBox.warning(self, "Query error", f"Ошибка bt1: {e}")

    def query_combo(self):
        """При выборе колонки orders → SELECT <col> FROM orders → Tab3"""
        if not self.cursor:
            return
        col = self.combo.currentText()
        if not col:
            return
        q = f"SELECT {col} FROM orders ORDER BY date DESC LIMIT 500"
        try:
            self.cursor.execute(q)
            rows = self.cursor.fetchall()
            # rows may be list of sqlite3.Row or tuples
            if isinstance(rows, list) and rows and isinstance(rows[0], sqlite3.Row):
                data = [tuple(r) for r in rows]
            else:
                data = [tuple(r) for r in rows]
            self.show_table(data, [col], self.tables[2])
            self.tabs.setCurrentIndex(2)
            self.statusBar().showMessage(f"Column '{col}' from orders shown in Tab3")
        except Exception as e:
            QMessageBox.warning(self, "Query error", f"Ошибка combo query: {e}")

    def query_bt2(self):
        """bt2: выручка (sum amount) по странам (customers.country) -> Tab4"""
        if not self.cursor:
            QMessageBox.information(self, "Not connected", "Сначала выполните Set connection")
            return
        q = """
            SELECT c.country AS country, 
                   COUNT(o.id) AS orders_count,
                   ROUND(SUM(o.amount), 2) AS total_revenue,
                   ROUND(AVG(o.amount), 2) AS avg_order
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            GROUP BY c.country
            ORDER BY total_revenue DESC
        """
        try:
            self.cursor.execute(q)
            rows = self.cursor.fetchall()
            cols = rows[0].keys() if rows else [d[0] for d in self.cursor.description]
            data = [tuple(r) for r in rows]
            self.show_table(data, list(cols), self.tables[3])
            self.tabs.setCurrentIndex(3)
            self.statusBar().showMessage("bt2: revenue by country shown in Tab4")
        except Exception as e:
            QMessageBox.warning(self, "Query error", f"Ошибка bt2: {e}")

    def query_bt3(self):
        """bt3: топ товаров по количеству и выручке -> Tab5"""
        if not self.cursor:
            QMessageBox.information(self, "Not connected", "Сначала выполните Set connection")
            return
        q = """
            SELECT p.name AS product_name,
                   p.category,
                   SUM(oi.qty) AS total_qty,
                   ROUND(SUM(oi.qty * p.price), 2) AS total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.id
            ORDER BY total_qty DESC, total_revenue DESC
            LIMIT 100
        """
        try:
            self.cursor.execute(q)
            rows = self.cursor.fetchall()
            cols = rows[0].keys() if rows else [d[0] for d in self.cursor.description]
            data = [tuple(r) for r in rows]
            self.show_table(data, list(cols), self.tables[4])
            self.tabs.setCurrentIndex(4)
            self.statusBar().showMessage("bt3: top products shown in Tab5")
        except Exception as e:
            QMessageBox.warning(self, "Query error", f"Ошибка bt3: {e}")

    def show_table(self, data, columns, table_widget):
        """data: list of tuples; columns: list of column names"""
        table_widget.clear()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels(columns)

        for r, row in enumerate(data):
            for c, val in enumerate(row):
                if val is None:
                    disp = ""
                else:
                    disp = str(val)
                item = QTableWidgetItem(disp)
                # числа в правую сторону ячейки
                if isinstance(val, (int, float)):
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                table_widget.setItem(r, c, item)

        table_widget.resizeColumnsToContents()
        if len(columns) > 0:
            table_widget.horizontalHeader().setStretchLastSection(True)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
