import customtkinter
from mychatui.preferences import PreferencesWindow
import json
import os
import google.generativeai as genai
import threading
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from tkhtmlview import HTMLScrolledText
import tkinter as tk
from tkinter import filedialog

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
        self.bind_shortcuts()

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
        tab = self.tab_view.tab(tab_name)
        self.tab_view.set(tab_name)
        self.create_chat_widgets(tab)

    def rename_current_tab(self):
        dialog = customtkinter.CTkInputDialog(text="Enter new tab name:", title="Rename Tab")
        new_name = dialog.get_input()
        if new_name:
            current_tab_name = self.tab_view.get()
            self.tab_view.rename(current_tab_name, new_name)

    def close_current_tab(self):
        current_tab_name = self.tab_view.get()
        self.tab_view.delete(current_tab_name)

    def save_current_tab(self):
        current_tab_name = self.tab_view.get()
        tab = self.tab_view.tab(current_tab_name)
        history = tab.chat_history
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json"),
                                                            ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(history, f, indent=4)

    def open_tab(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                               filetypes=[("JSON files", "*.json"),
                                                          ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as f:
                history = json.load(f)
            
            self.add_new_tab()
            current_tab_name = self.tab_view.get()
            tab = self.tab_view.tab(current_tab_name)
            tab.chat_history = history
            self.update_textbox_html(tab, tab.winfo_children()[0])

    def create_chat_widgets(self, tab):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        tab.chat_history = []

        font = (None, self.font_size)

        textbox = HTMLScrolledText(tab, font=font)
        textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        if customtkinter.get_appearance_mode() == "Dark":
            textbox.configure(background="#2b2b2b")

        entry = customtkinter.CTkEntry(tab, placeholder_text="Send a message", font=font)
        entry.grid(row=1, column=0, sticky="ew", padx=(5, 0), pady=5)
        entry.bind("<Return>", lambda event: self.send_message(tab, textbox, entry))

        send_button = customtkinter.CTkButton(tab, text="Send", width=70, command=lambda: self.send_message(tab, textbox, entry))
        send_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)

    def send_message(self, tab, textbox, entry):
        message = entry.get()
        if message:
            tab.chat_history.append(f"<p>🧑 You: {message}</p>")
            self.update_textbox_html(tab, textbox)
            entry.delete(0, "end")
            self.progress_bar.pack(side="right", padx=5, pady=5)
            self.progress_bar.start()
            
            thread = threading.Thread(target=self._get_ai_response_threaded, args=(tab, textbox, message))
            thread.start()

    def _get_ai_response_threaded(self, tab, textbox, message):
        try:
            genai.configure(api_key=self.config.get("api_key"))
            model = genai.GenerativeModel(self.config.get("model"))
            response = model.generate_content(message)
            self.after(0, self.get_ai_response, tab, textbox, response.text, None)
        except Exception as e:
            self.after(0, self.get_ai_response, tab, textbox, None, e)

    def get_ai_response(self, tab, textbox, response_text, error):
        if error:
            tab.chat_history.append(f"<p>Error: {error}</p>")
        else:
            md = MarkdownIt()
            md.use(front_matter_plugin)
            html = md.render(response_text)
            tab.chat_history.append(f"🤖 AI: {html}")
        
        self.update_textbox_html(tab, textbox)
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

    def update_textbox_html(self, tab, textbox):
        history_html = "".join(tab.chat_history)
        if customtkinter.get_appearance_mode() == "Dark":
            html_to_render = f"<div style='color: white;'>{history_html}</div>"
        else:
            html_to_render = history_html
        textbox.set_html(html_to_render)
        textbox.see(tk.END)

    def create_menu(self):
        menu_frame = customtkinter.CTkFrame(self)
        menu_frame.grid(row=1, column=0, sticky="ew")
        menu_frame.grid_columnconfigure(1, weight=1)

        menu_button = customtkinter.CTkButton(menu_frame, text="☰", width=30)
        menu_button.pack(side="left", padx=5, pady=5)
        
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="New Tab", command=self.add_new_tab)
        self.menu.add_command(label="Rename Tab", command=self.rename_current_tab)
        self.menu.add_command(label="Close Tab", command=self.close_current_tab)
        self.menu.add_separator()
        self.menu.add_command(label="Save Tab", command=self.save_current_tab)
        self.menu.add_command(label="Open Tab", command=self.open_tab)
        self.menu.add_separator()
        self.menu.add_command(label="Preferences", command=self.open_preferences)
        
        menu_button.bind("<Button-1>", self.show_menu)

        self.progress_bar = customtkinter.CTkProgressBar(menu_frame, mode="indeterminate")
        self.progress_bar.pack(side="right", padx=5, pady=5)
        self.progress_bar.pack_forget()

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def open_preferences(self):
        preferences_window = PreferencesWindow(self)
        preferences_window.grab_set()

    def apply_font_change(self):
        self.load_config()
        font = (None, self.font_size)
        for tab_name in self.tab_view._name_list:
            tab = self.tab_view.tab(tab_name)
            for widget in tab.winfo_children():
                if isinstance(widget, (HTMLScrolledText, customtkinter.CTkEntry)):
                    widget.configure(font=font)
                if isinstance(widget, HTMLScrolledText) and customtkinter.get_appearance_mode() == "Dark":
                    widget.configure(background="#2b2b2b")

    def bind_shortcuts(self):
        self.bind("<Control-m>", self.show_menu_ctrl_m)
        self.bind("<Control-Shift-T>", lambda event: self.add_new_tab())
        self.bind("<Control-Shift-R>", lambda event: self.rename_current_tab())
        self.bind("<Control-w>", lambda event: self.close_current_tab())
        self.bind("<Control-q>", lambda event: self.destroy())
        self.bind("<Control-s>", lambda event: self.save_current_tab())
        self.bind("<Control-o>", lambda event: self.open_tab())

    def show_menu_ctrl_m(self, event):
        self.menu.tk_popup(self.winfo_x() + 5, self.winfo_y() + 30)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
