import customtkinter
import json
import os
import google.generativeai as genai

class PreferencesWindow(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Preferences")
        self.geometry("400x300")

        self.config_file = os.path.expanduser("~/.config/mychatui/config.json")
        self.config = self.load_config()

        self.create_widgets()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
                if "font_size" not in config:
                    config["font_size"] = 12  # Default font size
                return config
        else:
            return {"api_key": "", "model": "", "font_size": 12}

    def save_config(self):
        if not os.path.exists(os.path.dirname(self.config_file)):
            os.makedirs(os.path.dirname(self.config_file))
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def create_widgets(self):
        self.api_key_label = customtkinter.CTkLabel(self, text="API Key:")
        self.api_key_label.pack(pady=5)
        self.api_key_entry = customtkinter.CTkEntry(self, width=300)
        self.api_key_entry.pack(pady=5)
        self.api_key_entry.insert(0, self.config.get("api_key", ""))

        self.model_label = customtkinter.CTkLabel(self, text="Model:")
        self.model_label.pack(pady=5)

        self.models = self.get_models()
        self.model_menu = customtkinter.CTkOptionMenu(self, values=[name for name, full_name in self.models])
        self.model_menu.pack(pady=5)
        
        # Find the display name for the currently configured model
        current_model_fullname = self.config.get("model", "")
        current_model_displayname = ""
        for name, full_name in self.models:
            if full_name == current_model_fullname:
                current_model_displayname = name
                break
        self.model_menu.set(current_model_displayname)

        self.font_size_label = customtkinter.CTkLabel(self, text="Font Size:")
        self.font_size_label.pack(pady=5)
        self.font_size_menu = customtkinter.CTkOptionMenu(self, values=[str(s) for s in [10, 12, 14, 16, 18, 20]])
        self.font_size_menu.pack(pady=5)
        self.font_size_menu.set(str(self.config.get("font_size", 12)))


        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.pack(pady=10)

        self.ok_button = customtkinter.CTkButton(self.button_frame, text="OK", command=self.ok)
        self.ok_button.pack(side="left", padx=5)

        self.cancel_button = customtkinter.CTkButton(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.pack(side="left", padx=5)

        self.apply_button = customtkinter.CTkButton(self.button_frame, text="Apply", command=self.apply)
        self.apply_button.pack(side="left", padx=5)

    def get_models(self):
        try:
            genai.configure(api_key=self.api_key_entry.get())
            # Return a list of tuples (display_name, full_name)
            return [(m.display_name, m.name) for m in genai.list_models()]
        except Exception as e:
            print(f"Error getting models: {e}")
            return []

    def apply(self):
        self.config["api_key"] = self.api_key_entry.get()
        selected_display_name = self.model_menu.get()
        # Find the full name corresponding to the selected display name
        for name, full_name in self.models:
            if name == selected_display_name:
                self.config["model"] = full_name
                break
        self.config["font_size"] = int(self.font_size_menu.get())
        self.save_config()
        if hasattr(self.master, "apply_font_change"):
            self.master.apply_font_change()

    def ok(self):
        self.apply()
        self.destroy()

    def cancel(self):
        self.destroy()
