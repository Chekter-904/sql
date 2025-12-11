import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "goods.db"


def get_tables():
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [t[0] for t in cur.fetchall() if t[0] != "sqlite_sequence"]


def load_table():
    table = table_box.get()
    if not table:
        return

    tree.delete(*tree.get_children())

    # столбцы
    cur.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cur.fetchall()]
    tree["columns"] = cols
    tree["show"] = "headings"

    for c in cols:
        tree.heading(c, text=c)

    # данные
    cur.execute(f"SELECT * FROM {table}")
    for row in cur.fetchall():
        tree.insert("", tk.END, values=row)


def add_record():
    table = table_box.get()
    if not table:
        return

    cols = get_columns(table)

    win = tk.Toplevel(root)
    win.title("Добавить запись")

    entries = {}
    for i, col in enumerate(cols):
        tk.Label(win, text=col).grid(row=i, column=0)
        ent = tk.Entry(win)
        ent.grid(row=i, column=1)
        entries[col] = ent

    def save():
        values = [entries[c].get() for c in cols]
        placeholders = ",".join(["?"] * len(cols))
        try:
            cur.execute(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})", values)
            conn.commit()
            load_table()
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(win, text="Сохранить", command=save).grid(row=len(cols), column=0, columnspan=2)


def delete_record():
    table = table_box.get()
    if not table:
        return

    pk = get_pk(table)

    win = tk.Toplevel(root)
    win.title("Удалить запись")

    tk.Label(win, text=f"{pk} =").pack()
    id_entry = tk.Entry(win)
    id_entry.pack()

    def delete():
        try:
            cur.execute(f"DELETE FROM {table} WHERE {pk}=?", (id_entry.get(),))
            conn.commit()
            load_table()
            win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    tk.Button(win, text="Удалить", command=delete).pack()


def get_columns(table):
    cur.execute(f"PRAGMA table_info({table})")
    return [c[1] for c in cur.fetchall()]


def get_pk(table):
    cur.execute(f"PRAGMA table_info({table})")
    for c in cur.fetchall():
        if c[5] == 1:
            return c[1]
    return None


conn = sqlite3.connect(DB)
cur = conn.cursor()

root = tk.Tk()
root.title("Простой интерфейс к БД")

# Выбор таблицы
tk.Label(root, text="Таблица:").pack()
table_box = ttk.Combobox(root, values=get_tables(), state="readonly")
table_box.pack()
table_box.bind("<<ComboboxSelected>>", lambda e: load_table())

# Кнопки
btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Показать", command=load_table).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Добавить", command=add_record).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Удалить", command=delete_record).grid(row=0, column=2, padx=5)

# Таблица данных
tree = ttk.Treeview(root)
tree.pack(expand=True, fill="both")

root.mainloop()


