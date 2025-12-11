import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox


DB_PATH = "goods.db"


class DBApp:
    def __init__(self, root):
        self.root = root
        root.title("Простой интерфейс к базе данных (SQLite)")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        # --- Верхняя панель: выбор таблицы ---
        tk.Label(root, text="Выберите таблицу:").pack()

        self.table_box = ttk.Combobox(root, state="readonly")
        self.table_box.pack(pady=5)
        self.table_box["values"] = self.get_tables()
        self.table_box.bind("<<ComboboxSelected>>", self.load_table)

        # --- Таблица вывода данных ---
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both", pady=5)

        # --- Панель добавления / удаления / изменения ---
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Button(frame, text="Добавить", command=self.add_entry).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Удалить по ID", command=self.delete_entry).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Изменить по ID", command=self.update_entry).grid(row=0, column=2, padx=5)

    # ------------------ Получение таблиц ------------------
    def get_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.cursor.fetchall() if row[0] != "sqlite_sequence"]

    # ------------------ Загрузка таблицы ------------------
    def load_table(self, event=None):
        table = self.table_box.get()

        # Очистить дерево
        self.tree.delete(*self.tree.get_children())

        # Получаем данные
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = [c[1] for c in self.cursor.fetchall()]

        self.tree["columns"] = columns
        self.tree["show"] = "headings"

        for col in columns:
            self.tree.heading(col, text=col)

        self.cursor.execute(f"SELECT * FROM {table}")
        for row in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=row)

    # ------------------ Добавление записи ------------------
    def add_entry(self):
        table = self.table_box.get()
        if not table:
            return

        cols = self.get_columns(table)

        win = tk.Toplevel(self.root)
        win.title("Добавление записи")

        entries = {}
        for i, col in enumerate(cols):
            tk.Label(win, text=col).grid(row=i, column=0)
            ent = tk.Entry(win)
            ent.grid(row=i, column=1)
            entries[col] = ent

        def save():
            values = [entries[c].get() for c in cols]
            q = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})"
            try:
                self.cursor.execute(q, values)
                self.conn.commit()
                self.load_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Сохранить", command=save).grid(row=len(cols), column=0, columnspan=2)

    # ------------------ Удаление по ID ------------------
    def delete_entry(self):
        table = self.table_box.get()
        if not table:
            return

        pk = self.get_primary_key(table)

        win = tk.Toplevel(self.root)
        win.title("Удалить запись")

        tk.Label(win, text=f"{pk} =").pack()
        id_entry = tk.Entry(win)
        id_entry.pack()

        def delete():
            try:
                self.cursor.execute(f"DELETE FROM {table} WHERE {pk}=?", (id_entry.get(),))
                self.conn.commit()
                self.load_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Удалить", command=delete).pack(pady=5)

    # ------------------ Обновление записи ------------------
    def update_entry(self):
        table = self.table_box.get()
        if not table:
            return

        cols = self.get_columns(table)
        pk = self.get_primary_key(table)

        win = tk.Toplevel(self.root)
        win.title("Изменить запись")

        tk.Label(win, text=f"ID ({pk}) изменяемой строки:").grid(row=0, column=0)
        id_entry = tk.Entry(win)
        id_entry.grid(row=0, column=1)

        entries = {}
        for i, c in enumerate(cols, start=1):
            tk.Label(win, text=c).grid(row=i, column=0)
            ent = tk.Entry(win)
            ent.grid(row=i, column=1)
            entries[c] = ent

        def update():
            id_val = id_entry.get()
            set_expr = ", ".join([f"{c}=?" for c in cols])
            values = [entries[c].get() for c in cols]
            values.append(id_val)

            try:
                self.cursor.execute(f"UPDATE {table} SET {set_expr} WHERE {pk}=?", values)
                self.conn.commit()
                self.load_table()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Сохранить изменения", command=update).grid(row=len(cols)+1, column=0, columnspan=2)

    # ------------------ Утилиты ------------------
    def get_columns(self, table):
        self.cursor.execute(f"PRAGMA table_info({table})")
        return [c[1] for c in self.cursor.fetchall()]

    def get_primary_key(self, table):
        self.cursor.execute(f"PRAGMA table_info({table})")
        for c in self.cursor.fetchall():
            if c[5] == 1:
                return c[1]
        return None


# ------------------ Запуск ------------------
root = tk.Tk()
app = DBApp(root)
root.mainloop()
