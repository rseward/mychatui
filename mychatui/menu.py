import customtkinter
import tkinter as tk


class HamburgerMenu(customtkinter.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        self.grid_columnconfigure(1, weight=1)

        self.menu_button = customtkinter.CTkButton(self, text="☰", width=30)
        self.menu_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(
            label="New Tab", accelerator="Ctrl+Shift+T", command=self.app.add_new_tab
        )
        self.menu.add_command(
            label="Rename Tab",
            accelerator="Ctrl+Shift+R",
            command=self.app.rename_current_tab,
        )
        self.menu.add_command(
            label="Close Tab", accelerator="Ctrl+W", command=self.app.close_current_tab
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="Save Tab", accelerator="Ctrl+S", command=self.app.save_current_tab
        )
        self.menu.add_command(
            label="Open Tab", accelerator="Ctrl+O", command=self.app.open_tab
        )
        self.menu.add_separator()
        self.menu.add_command(label="Preferences", command=self.app.open_preferences)
        self.menu.add_separator()
        self.menu.add_command(
            label="Quit", accelerator="Ctrl+Q", command=self.app.destroy
        )

        self.menu_button.bind("<Button-1>", self.show_menu)

        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.progress_bar.grid_remove()

        self.model_menu = customtkinter.CTkOptionMenu(
            self, values=[], command=self.on_model_select
        )
        self.model_menu.grid(row=0, column=2, sticky="e", padx=5, pady=5)

    def on_model_select(self, model_display_name):
        # Find the full name for the selected display name
        full_name = ""
        for model in self.app.config.get("user_models", []):
            if model["display_name"] == model_display_name:
                full_name = model["full_name"]
                break

        # Update the model for the current tab
        current_tab = self.app.tab_view.get()
        if current_tab:
            tab = self.app.tab_view.tab(current_tab)
            tab.model = full_name

    def update_model_menu(self):
        # Populate the model menu with display names
        models = self.app.config.get("user_models", [])
        display_names = [m["display_name"] for m in models]
        self.model_menu.configure(values=display_names)

        # Set the current model for the active tab
        current_tab_name = self.app.tab_view.get()
        if current_tab_name:
            tab = self.app.tab_view.tab(current_tab_name)
            model_full_name = tab.model

            # Find the display name for the current model
            display_name = ""
            for model in models:
                if model["full_name"] == model_full_name:
                    display_name = model["display_name"]
                    break
            self.model_menu.set(display_name)

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)
