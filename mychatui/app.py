import customtkinter
from mychatui.preferences import PreferencesWindow
import json
import os
import google.generativeai as genai
import threading

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("ChatUI")
        self.geometry("700x500")

        self.load_config()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, sticky="nsew")

        self.tab_count = 0
        self.add_new_tab()

        self.create_menu()

    def load_config(self):
        self.config_file = os.path.expanduser("~/.config/mychatui/config.json")
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
                if "font_size" not in self.config:
                    self.config["font_size"] = 12
        else:
            self.config = {"api_key": "", "model": "", "font_size": 12}
        
        self.font_size = self.config.get("font_size", 12)

    def add_new_tab(self):
        self.tab_count += 1
        tab_name = f"Tab {self.tab_count}"
        self.tab_view.add(tab_name)
        self.tab_view.set(tab_name)
        self.create_chat_widgets(self.tab_view.tab(tab_name))

    def create_chat_widgets(self, tab):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        font = (None, self.font_size)

        textbox = customtkinter.CTkTextbox(tab, font=font)
        textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        entry = customtkinter.CTkEntry(tab, placeholder_text="Send a message", font=font)
        entry.grid(row=1, column=0, sticky="ew", padx=(5, 0), pady=5)
        entry.bind("<Return>", lambda event: self.send_message(textbox, entry))

        send_button = customtkinter.CTkButton(tab, text="Send", width=70, command=lambda: self.send_message(textbox, entry))
        send_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)

    def send_message(self, textbox, entry):
        message = entry.get()
        if message:
            textbox.insert("end", f"\n\n🧑 You: {message}\n")
            entry.delete(0, "end")
            self.progress_bar.pack(side="right", padx=5, pady=5)
            self.progress_bar.start()
            
            thread = threading.Thread(target=self._get_ai_response_threaded, args=(textbox, message))
            thread.start()

    def _get_ai_response_threaded(self, textbox, message):
        try:
            genai.configure(api_key=self.config.get("api_key"))
            model = genai.GenerativeModel(self.config.get("model"))
            response = model.generate_content(message)
            self.after(0, self.get_ai_response, textbox, response.text, None)
        except Exception as e:
            self.after(0, self.get_ai_response, textbox, None, e)

    def get_ai_response(self, textbox, response_text, error):
        if error:
            textbox.insert("end", f"Error: {error}\n")
        else:
            textbox.insert("end", f"🤖 AI: {response_text}\n")
        
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def create_menu(self):
        menu_frame = customtkinter.CTkFrame(self)
        menu_frame.grid(row=1, column=0, sticky="ew")
        menu_frame.grid_columnconfigure(2, weight=1)

        new_tab_button = customtkinter.CTkButton(menu_frame, text="New Tab", command=self.add_new_tab)
        new_tab_button.pack(side="left", padx=5, pady=5)

        preferences_button = customtkinter.CTkButton(menu_frame, text="Preferences", command=self.open_preferences)
        preferences_button.pack(side="left", padx=5, pady=5)

        self.progress_bar = customtkinter.CTkProgressBar(menu_frame, mode="indeterminate")
        self.progress_bar.pack(side="right", padx=5, pady=5)
        self.progress_bar.pack_forget()

    def open_preferences(self):
        preferences_window = PreferencesWindow(self)
        preferences_window.grab_set()

    def apply_font_change(self):
        self.load_config()
        font = (None, self.font_size)
        for tab_name in self.tab_view._name_list:
            tab = self.tab_view.tab(tab_name)
            for widget in tab.winfo_children():
                if isinstance(widget, (customtkinter.CTkTextbox, customtkinter.CTkEntry)):
                    widget.configure(font=font)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
