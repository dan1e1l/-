import tkinter as tk
from tkinter import messagebox
import mysql.connector

# Настройка подключения к базе данных
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='123456',
    database='MusicStreamingService'
)
cursor = conn.cursor()

# Функции для работы с базой данных
def add_song():
    title = title_entry.get()
    artist = artist_entry.get()
    if title and artist:
        cursor.execute("INSERT INTO songs (title, artist) VALUES (%s, %s)", (title, artist))
        conn.commit()
        messagebox.showinfo("Успех", "Песня добавлена!")
    else:
        messagebox.showwarning("Ошибка", "Заполните все поля")

def view_songs():
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    listbox.delete(0, tk.END)
    for song in songs:
        listbox.insert(tk.END, f"{song[0]}. {song[1]} - {song[2]}")

def delete_song():
    song_id = int(id_entry.get())
    cursor.execute("DELETE FROM songs WHERE SongID = %s", (song_id,))
    conn.commit()
    messagebox.showinfo("Успех", "Песня удалена!")

# Создание интерфейса
root = tk.Tk()
root.title("Music Database")

tk.Label(root, text="Название").grid(row=0, column=0)
tk.Label(root, text="Исполнитель").grid(row=1, column=0)
tk.Label(root, text="ID для удаления").grid(row=2, column=0)

title_entry = tk.Entry(root)
artist_entry = tk.Entry(root)
id_entry = tk.Entry(root)

title_entry.grid(row=0, column=1)
artist_entry.grid(row=1, column=1)
id_entry.grid(row=2, column=1)

tk.Button(root, text="Добавить песню", command=add_song).grid(row=3, column=0)
tk.Button(root, text="Просмотреть песни", command=view_songs).grid(row=3, column=1)
tk.Button(root, text="Удалить песню", command=delete_song).grid(row=3, column=2)

listbox = tk.Listbox(root)
listbox.grid(row=4, column=0, columnspan=3)

root.mainloop()

# Закрытие соединения с базой данных при выходе
conn.close()