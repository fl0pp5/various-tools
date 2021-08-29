import tkinter as tk
from tkinter import ttk
from typing import List
import getpass

from tew652brp.client import Client
from tew652brp.core.access.virtual.types import VServerInfo


class SetupFrame(tk.Frame):
    def __init__(self, client: Client, virtual_server: VServerInfo, **kw):
        super().__init__(**kw)
        self._client = client
        self._server = virtual_server

        # vars
        self._name_var = tk.StringVar(value=self._server.name)
        self._ip_var = tk.StringVar(value=self._server.internal_ip)
        self._public_port_var = tk.StringVar(value=self._server.public_port)
        self._private_port_var = tk.StringVar(value=self._server.private_port)
        self._protocol_var = tk.IntVar(value=self._server.protocol)
        self._enabled_var = tk.BooleanVar(value=self._server.enabled)

        # widgets
        self._name_entry = tk.Entry(self, textvariable=self._name_var)
        self._ip_entry = tk.Entry(self, textvariable=self._ip_var)

        self._public_port_entry = tk.Entry(self, textvariable=self._public_port_var)
        self._private_port_entry = tk.Entry(self, textvariable=self._private_port_var)

        self._tcp_label = tk.Label(self, text='TCP')
        self._tcp_radio = tk.Radiobutton(self, variable=self._protocol_var, value=0)

        self._udp_label = tk.Label(self, text='UDP')
        self._udp_radio = tk.Radiobutton(self, variable=self._protocol_var, value=1)

        self._both_label = tk.Label(self, text='TCP/UDP')
        self._both_radio = tk.Radiobutton(self, variable=self._protocol_var, value=2)

        self._enable_label = tk.Label(self, text='Включить')
        self._enabled_check = tk.Checkbutton(self, variable=self._enabled_var, onvalue=1, offvalue=0)

        self._apply_button = tk.Button(self, text='Применить', command=self._apply)

        self._widgets = [
            lambda: self._name_entry.pack(),
            lambda: self._ip_entry.pack(),
            lambda: self._public_port_entry.pack(),
            lambda: self._private_port_entry.pack(),
            lambda: self._tcp_label.pack(side=tk.LEFT),
            lambda: self._tcp_radio.pack(side=tk.LEFT),
            lambda: self._udp_label.pack(side=tk.LEFT),
            lambda: self._udp_radio.pack(side=tk.LEFT),
            lambda: self._both_label.pack(side=tk.LEFT),
            lambda: self._both_radio.pack(side=tk.LEFT),
            lambda: self._enable_label.pack(),
            lambda: self._enabled_check.pack(),
            lambda: self._apply_button.pack(),
        ]
        self.init_view()

    def _apply(self):
        self._server.name = self._name_var.get()
        self._server.internal_ip = self._ip_var.get()
        self._server.public_port = self._public_port_var.get()
        self._server.private_port = self._private_port_var.get()
        self._server.protocol = self._protocol_var.get()
        self._server.enabled = int(self._enabled_var.get())

        self._client.virtual.update_server(self._server)

    def init_view(self):
        for widget in self._widgets:
            widget()


class VirtualFrame(tk.Frame):
    def __init__(self, client: Client, **kw):
        super().__init__(**kw)
        self._client = client

        self._servers = []
        self._server_listbox = tk.Listbox(
            self, height=10
        )
        self._server_listbox.bind('<<ListboxSelect>>', self._select_server)

        self._get_servers_button = tk.Button(
            self,
            text='Получить список серверов',
            command=self.get_servers,
        )

        self._current_server_settings = None

        self.init_view()

    def init_view(self):
        self._server_listbox.pack(expand=True, fill='both')
        self._get_servers_button.pack(expand=True, fill='both')

    def get_servers(self):
        if servers := self._client.virtual.get_servers():
            self._server_listbox.delete(0, tk.END)
            self._servers = servers

        for server in self._servers:
            self._server_listbox.insert(
                tk.END,
                f'{server.name} - {server.internal_ip}:{server.public_port}|{server.private_port}'
            )

    def _select_server(self, event):
        selection = event.widget.curselection()
        if selection:
            server = self._servers[selection[0]]
            if self._current_server_settings is not None:
                self._current_server_settings.pack_forget()

            self._current_server_settings = SetupFrame(self._client, server, master=self)
            self._current_server_settings.pack()


class RouterGUI:
    def __init__(self, width, height, url, username, passwd):
        self.root = tk.Tk()
        self.root.geometry(f'{width}x{height}')
        self.root.title('TEW652BRP')
        self.root.iconphoto(False, tk.PhotoImage(file='./src/icon.png'))
        self.notebook = ttk.Notebook(self.root)

        self.client = Client(url)
        self.client.login.login(username, passwd)

        self.frames = [
            VirtualFrame(
                self.client,
                master=self.notebook,
            ),
        ]

    def init_view(self):
        for frame in self.frames:
            # frame.pack(expand=False, fill=None)
            self.notebook.add(frame, text='virtual')
        self.notebook.pack(fill='both', expand=False)

    def exec(self):
        self.init_view()
        self.root.mainloop()


if __name__ == '__main__':
    router_url = input('Enter router URL: ')
    username = input('Enter your username: ')
    passwd = getpass.getpass()

    gui = RouterGUI(400, 400, router_url, username, passwd)
    gui.exec()
