import datetime
import os
import pathlib
import time
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import imghdr

from PIL import Image


def crop_to_parts(filename, part_n):
    _image: Image.Image = Image.open(filename)
    parts = []
    k = _image.width / part_n
    for i in range(part_n):
        box = k*i, 0, k*(i+1), _image.height
        parts.append(_image.crop(box))

    return parts


def resize_list(images, width, height):
    to_ret = []
    for image in images:
        to_ret.append(image.resize((width, height)))

    return to_ret


def is_image(filename):
    if imghdr.what(filename) in ['jpeg', 'png']:
        return True
    return False


class Window:
    FILETYPES = (
        ('image files', ('*.jpg', '*.png')),
        ('All files', '*'),
    )

    WIDTH_SIZE = 3256
    HEIGHT_SIZE = 860
    DEFAULT_SAVE_DIR = 'saves-{}'
    DEFAULT_SAVE_FILE = 'file-{}.jpg'

    def __init__(self, width, height):
        self.root = tk.Tk()
        self.root.geometry(f'{width}x{height}')
        self.root.iconphoto(False, tk.PhotoImage(file='./src/icon.png'))

        self.menubar = tk.Menu(self.root)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Добавить', command=self.add_files)
        self.filemenu.add_command(label='Удалить выделенные файлы', command=self.delete_files)

        self.menubar.add_cascade(label='Файл', menu=self.filemenu)

        self.files_listbox = tk.Listbox(self.root, selectmode=tk.EXTENDED, width=65)
        self.files_listbox.bind('<<ListboxSelect>>', self.select_files)

        self.delete_button = tk.Button(self.root, text='Удалить выделенные файлы', command=self.delete_files)

        self.start_button = tk.Button(self.root, text='Сделать магию', command=self.save_images)

        self.widgets = [
            self.files_listbox,
            self.delete_button,
            self.start_button,
        ]
        self.selected = []

    def transform_images(self):
        for filename in self.files_listbox.get(0, tk.END):
            yield from resize_list(
                crop_to_parts(filename, 2),
                self.WIDTH_SIZE,
                self.HEIGHT_SIZE
            )

    def save_images(self):
        folder_name = self.DEFAULT_SAVE_DIR.format(datetime.date.today())
        pathlib.Path(folder_name).mkdir(
            exist_ok=True
        )

        for image in self.transform_images():
            file_name = self.DEFAULT_SAVE_FILE.format(time.time())
            image.save(f'{folder_name}/{file_name}')

        mb.showinfo('Файлы обработаны', message=f'Файлы сохранены в {os.path.join(os.getcwd(), folder_name)}')

    def add_files(self):
        bad_files = []
        good_files = []
        for file in fd.askopenfilenames(filetypes=self.FILETYPES):
            if is_image(file):
                good_files.append(file)
            else:
                bad_files.append(file)

        self.files_listbox.insert(tk.END, *good_files)
        if bad_files:
            mb.showerror(
                "Неверный формат",
                message=f"Не были добавлены файлы: {bad_files}",
            )

    def select_files(self, event):
        self.selected = event.widget.curselection()

    def delete_files(self):
        [self.files_listbox.delete(i) for i in self.selected]

    def init(self):
        self.root.config(menu=self.menubar)
        for widget in self.widgets:
            widget.pack()

    def show(self):
        self.root.mainloop(0)


def main():
    window = Window(400, 400)
    window.init()
    window.show()


if __name__ == '__main__':
    main()
