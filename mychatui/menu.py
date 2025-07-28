import customtkinter
import tkinter as tk

class HamburgerMenu(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(1, weight=1)

        menu_button = customtkinter.CTkButton(self, text="☰", width=30)
        menu_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="New Tab", accelerator="Ctrl+Shift+T", command=self.app.add_new_tab)
        self.menu.add_command(label="Rename Tab", accelerator="Ctrl+Shift+R", command=self.app.rename_current_tab)
        self.menu.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.app.close_current_tab)
        self.menu.add_separator()
        self.menu.add_command(label="Save Tab", accelerator="Ctrl+S", command=self.app.save_current_tab)
        self.menu.add_command(label="Open Tab", accelerator="Ctrl+O", command=self.app.open_tab)
        self.menu.add_separator()
        self.menu.add_command(label="Preferences", command=self.app.open_preferences)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.app.destroy)
        
        menu_button.bind("<Button-1>", self.show_menu)

        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=5, pady=5)
        self.progress_bar.grid_remove()

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)
