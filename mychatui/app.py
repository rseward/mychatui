#!/usr/bin/env python3
"""
MyChatUI - A custom chat application using customtkinter
"""

import os
import sys
import logging
import traceback
from datetime import datetime
# import google.generativeai as genai

import any_llm as ai
from mychatui.adapters.aisuite import AiSuiteAdapter
from mychatui.adapters.anyllm import AnyLlmAdapter

# Set up basic logging
log_file = os.path.expanduser("~/mychatui_debug.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def log_environment():
    """Log important environment information."""
    logger.info("=" * 50)
    logger.info(f"Starting MyChatUI at {datetime.now()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Script path: {os.path.abspath(__file__)}")
    logger.info("Environment variables:")
    for var in ["DISPLAY", "WAYLAND_DISPLAY", "PYTHONPATH", "PATH"]:
        logger.info(f"  {var}: {os.environ.get(var, 'Not set')}")
    logger.info("=" * 50)


# Import other modules after setting up logging
try:
    import customtkinter

    logger.info(
        f"customtkinter imported successfully (v{customtkinter.__version__ if hasattr(customtkinter, '__version__') else 'unknown'})"
    )

    from mychatui.preferences import PreferencesWindow
    from mychatui.menu import HamburgerMenu
    from mychatui.voice_input import VoiceInput
    import json
    import threading
    from markdown_it import MarkdownIt
    from mdit_py_plugins.front_matter import front_matter_plugin
    from tkhtmlview import HTMLScrolledText
    import tkinter as tk
    from tkinter import filedialog
    from bs4 import BeautifulSoup

    logger.info("All required modules imported successfully")

except ImportError as e:
    logger.error(f"Import error: {str(e)}")
    logger.error(traceback.format_exc())
    raise


class App(customtkinter.CTk):
    def __init__(self):
        logger.info("Initializing App class...")
        try:
            # Initialize the main window
            super().__init__()
            logger.info("CTk parent class initialized")

            # Set window properties
            self.title("MyChatUI")
            self.geometry("700x500")
            customtkinter.set_appearance_mode("dark")

            # Set window class and name for proper desktop integration
            try:
                # Method 1: Set WM_CLASS using wm_class
                self.tk.call("wm", "class", self._w, "MyChatUI")
                # Method 2: Set WM_NAME
                self.tk.call("wm", "name", self._w, "MyChatUI")
                # Method 3: Set both class and name
                self.tk.call("wm", "command", self._w, "MyChatUI")
                logger.info("Set window class and name to 'MyChatUI'")
                customtkinter.set_appearance_mode("dark")

            except Exception as e:
                logger.error(f"Failed to set window class/name: {e}")

            # Set the application icon using multiple methods
            icon_paths = [
                os.path.expanduser(
                    "~/.local/share/icons/hicolor/128x128/apps/mychatui.png"
                ),
                os.path.expanduser(
                    "~/.local/share/mychatui.app/share/icons/hicolor/128x128/apps/jarvis128.png"
                ),
                "/usr/share/icons/hicolor/128x128/apps/mychatui.png",
                "/usr/share/pixmaps/mychatui.png",
            ]

            icon_loaded = False
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        # Try different methods to set the icon
                        try:
                            self.iconphoto(True, tk.PhotoImage(file=icon_path))
                            self.tk.call(
                                "wm",
                                "iconphoto",
                                self._w,
                                tk.PhotoImage(file=icon_path),
                            )
                            if icon_path.lower().endswith(".ico"):
                                self.iconbitmap(icon_path)
                            logger.info(f"Loaded application icon from {icon_path}")
                            icon_loaded = True
                            break
                        except Exception as e:
                            logger.warning(f"Failed to load icon from {icon_path}: {e}")
                    except Exception as e:
                        logger.warning(f"Error processing icon at {icon_path}: {e}")

            if not icon_loaded:
                logger.warning("Could not load any application icon")

            logger.info("Window properties set")

            self.load_config()
            logger.info("Configuration loaded")

            # Set up grid
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
            logger.info("Grid layout configured")

            # Initialize UI components
            self.init_ui()
            self.aisuite_adapter = AiSuiteAdapter()
            self.anyllm_adapter = AnyLlmAdapter()
            logger.info("UI initialization complete")

        except Exception as e:
            logger.error(f"Error during App initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def init_ui(self):
        """Initialize all UI components."""
        try:
            logger.info("Initializing menu...")
            self.menu_frame = HamburgerMenu(self, self)
            self.menu_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

            logger.info("Initializing tab view...")
            self.tab_view = customtkinter.CTkTabview(self, command=self.on_tab_change)
            self.tab_view.grid(row=1, column=0, sticky="nsew")

            self.tab_count = 0
            logger.info("Adding initial tabs from config...")
            for tab_name in self.config.get("active_tabs", ["Tab 1"]):
                self.add_new_tab(tab_name)

            self.menu_frame.update_model_menu()

            logger.info("Setting up keyboard shortcuts...")
            self.bind_shortcuts()

            self.protocol("WM_DELETE_WINDOW", self.on_closing)

        except Exception as e:
            logger.error(f"Error in UI initialization: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def on_tab_change(self):
        self.menu_frame.update_model_menu()

    def on_closing(self):
        self.save_config()
        self.destroy()

    def load_config(self):
        logger.info("Loading configuration...")
        try:
            self.config_file = os.path.expanduser("~/.config/mychatui/config.json")
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
                    if "font_size" not in self.config:
                        self.config["font_size"] = 12
                    if "active_tabs" not in self.config:
                        self.config["active_tabs"] = ["Tab 1"]
                    if (
                        "user_models" not in self.config
                        or not self.config.get("user_models")
                        or not isinstance(self.config.get("user_models")[0], dict)
                    ):
                        self.config["user_models"] = [
                            {
                                "display_name": "Gemini 1.0 Pro",
                                "full_name": "models/gemini-1.0-pro",
                            },
                            {
                                "display_name": "Gemini 1.5 Pro",
                                "full_name": "models/gemini-1.5-pro-latest",
                            },
                        ]
            else:
                self.config = {
                    "api_key": "",
                    "model": "",
                    "font_size": 12,
                    "active_tabs": ["Tab 1"],
                    "user_models": [
                        {
                            "display_name": "Gemini 1.0 Pro",
                            "full_name": "models/gemini-1.0-pro",
                        },
                        {
                            "display_name": "Gemini 1.5 Pro",
                            "full_name": "models/gemini-1.5-pro-latest",
                        },
                    ],
                }

            self.font_size = self.config.get("font_size", 12)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def save_config(self):
        logger.info("Saving configuration...")
        try:
            self.config["active_tabs"] = list(self.tab_view._name_list)
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def add_new_tab(self, tab_name=None):
        logger.info("Adding new tab...")
        try:
            self.tab_count += 1
            if tab_name is None:
                tab_name = f"Tab {self.tab_count}"
            self.tab_view.add(tab_name)
            tab = self.tab_view.tab(tab_name)
            tab.model = self.config.get("model")
            self.tab_view.set(tab_name)
            self.create_chat_widgets(tab)
            logger.info("New tab added successfully")
        except Exception as e:
            logger.error(f"Error adding new tab: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def rename_current_tab(self):
        logger.info("Renaming current tab...")
        try:
            dialog = customtkinter.CTkInputDialog(
                text="Enter new tab name:", title="Rename Tab"
            )
            new_name = dialog.get_input()
            if new_name:
                current_tab_name = self.tab_view.get()
                self.tab_view.rename(current_tab_name, new_name)
                logger.info("Tab renamed successfully")
        except Exception as e:
            logger.error(f"Error renaming tab: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def clear_current_tab_history(self):
        logger.info("Clearing current tab history...")
        try:
            current_tab_name = self.tab_view.get()
            tab = self.tab_view.tab(current_tab_name)
            tab.chat_history = []
            self.update_textbox_html(tab, tab.winfo_children()[0])
            logger.info("Tab history cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing tab history: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def refresh_current_tab_history(self):
        logger.info("Refreshing current tab history...")
        try:
            current_tab_name = self.tab_view.get()
            tab = self.tab_view.tab(current_tab_name)
            self.update_textbox_html(tab, tab.winfo_children()[0])
            logger.info("Tab history refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing tab history: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def close_current_tab(self):
        logger.info("Closing current tab...")
        try:
            current_tab_name = self.tab_view.get()
            self.tab_view.delete(current_tab_name)
            logger.info("Tab closed successfully")
        except Exception as e:
            logger.error(f"Error closing tab: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def save_current_tab(self):
        logger.info("Saving current tab...")
        try:
            current_tab_name = self.tab_view.get()
            tab = self.tab_view.tab(current_tab_name)

            tab_data = {
                "tab_name": current_tab_name,
                "model_name": tab.model,
                "chat_history": tab.chat_history,
            }

            config_dir = os.path.dirname(self.config_file)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            file_path = os.path.join(config_dir, f"{current_tab_name}.json")

            with open(file_path, "w") as f:
                json.dump(tab_data, f, indent=4)
            logger.info(f"Tab saved successfully to {file_path}")
            self.show_transient_message(f"Tab '{current_tab_name}' saved successfully.")
        except Exception as e:
            logger.error(f"Error saving tab: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_transient_message(f"Error saving tab: {e}", is_error=True)

    def show_transient_message(self, message, is_error=False):
        """Displays a transient message label that fades out."""
        if is_error:
            fg_color = ("#ffcccc", "#990000")  # Light red, Dark red
            text_color = ("#990000", "#ffcccc")
        else:
            fg_color = ("#ccffcc", "#006600")  # Light green, Dark green
            text_color = ("#006600", "#ccffcc")

        label = customtkinter.CTkLabel(
            self,
            text=message,
            fg_color=fg_color,
            text_color=text_color,
            corner_radius=5,
        )
        label.place(relx=0.5, rely=0.05, anchor="center")
        self.after(5000, label.destroy)

    def open_tab(self):
        logger.info("Opening tab...")
        try:
            config_dir = os.path.dirname(self.config_file)
            file_path = filedialog.askopenfilename(
                initialdir=config_dir,
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if file_path:
                with open(file_path, "r") as f:
                    tab_data = json.load(f)

                tab_name = tab_data.get("tab_name", "New Tab")

                # Check if tab already exists
                if tab_name in self.tab_view._name_list:
                    tab = self.tab_view.tab(tab_name)
                else:
                    self.add_new_tab(tab_name)
                    tab = self.tab_view.tab(tab_name)

                tab.model = tab_data.get("model_name")
                tab.chat_history = tab_data.get("chat_history", [])

                self.update_textbox_html(tab, tab.winfo_children()[0])
                self.menu_frame.update_model_menu()
                logger.info("Tab opened successfully")
        except Exception as e:
            logger.error(f"Error opening tab: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def create_chat_widgets(self, tab):
        logger.info("Creating chat widgets...")
        try:
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_rowconfigure(1, weight=0)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_columnconfigure(1, weight=0)
            tab.grid_columnconfigure(2, weight=0)

            tab.chat_history = []
            tab.history_index = None

            font = (None, self.font_size)

            textbox = HTMLScrolledText(tab, font=font)
            textbox.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

            darkback = "#002b36"
            if customtkinter.get_appearance_mode() == "Dark":
                textbox.configure(background=darkback)

            self.create_context_menu(textbox)

            entry = customtkinter.CTkEntry(
                tab, placeholder_text="Send a message", font=font
            )
            entry.grid(row=1, column=0, sticky="ew", padx=(5, 0), pady=5)
            entry.bind("<Return>", lambda event: self.send_message(tab, textbox, entry))
            entry.bind("<Up>", lambda event: self.navigate_history(tab, entry, -1))
            entry.bind("<Down>", lambda event: self.navigate_history(tab, entry, 1))

            # 1. Load the image
            from PIL import Image
            mic_image = customtkinter.CTkImage(
                light_image=Image.open("/usr/share/icons/HighContrast/24x24/devices/audio-input-microphone.png"),
                dark_image=Image.open("/usr/share/icons/HighContrast/24x24/devices/audio-input-microphone.png"),
                size=(24, 24)
            )

            # Microphone button for voice input
            mic = "\N{MICROPHONE}"
            mic_button = customtkinter.CTkButton(
                tab,
                text="",
                image=mic_image,
                width=50,
                command=lambda: self.open_voice_input(tab, entry),
                font=("Segoe UI Emoji", 18), # Font with emoji support
            )
            mic_button.grid(row=1, column=1, sticky="e", padx=5, pady=5)

            send_button = customtkinter.CTkButton(
                tab,
                text="Send",
                width=70,
                command=lambda: self.send_message(tab, textbox, entry),
            )
            send_button.grid(row=1, column=2, sticky="e", padx=5, pady=5)
            logger.info("Chat widgets created successfully")
        except Exception as e:
            logger.error(f"Error creating chat widgets: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def create_context_menu(self, widget):
        logger.info("Creating context menu...")
        try:
            context_menu = tk.Menu(widget, tearoff=0)
            context_menu.add_command(
                label="Copy", command=lambda: self.copy_selection(widget)
            )

            widget.bind(
                "<Button-3>", lambda event: self.show_context_menu(event, context_menu)
            )
            widget.bind("<Control-c>", lambda event: self.copy_selection(widget))
            logger.info("Context menu created successfully")
        except Exception as e:
            logger.error(f"Error creating context menu: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def show_context_menu(self, event, context_menu):
        logger.info("Showing context menu...")
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            logger.error(f"Error showing context menu: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def copy_selection(self, widget):
        logger.info("Copying selection...")
        try:
            try:
                selected_text = widget.selection_get()
                self.clipboard_clear()
                self.clipboard_append(selected_text)
            except tk.TclError:
                pass  # No text selected
            logger.info("Selection copied successfully")
        except Exception as e:
            logger.error(f"Error copying selection: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def navigate_history(self, tab, entry, direction):
        user_messages = [msg["content"] for msg in tab.chat_history if msg["role"] == "user"]
        if not user_messages:
            self.flash_widget(entry)
            return

        if tab.history_index is None:
            tab.history_index = len(user_messages)

        tab.history_index += direction

        if tab.history_index < 0:
            tab.history_index = 0
            self.flash_widget(entry)
        elif tab.history_index >= len(user_messages):
            tab.history_index = len(user_messages)
            entry.delete(0, "end")
            self.flash_widget(entry)
            return

        if 0 <= tab.history_index < len(user_messages):
            message_html = user_messages[tab.history_index]
            soup = BeautifulSoup(message_html, "html.parser")
            message_text = soup.get_text().replace("🧑 You: ", "")
            entry.delete(0, "end")
            entry.insert(0, message_text)

    def flash_widget(self, widget):
        original_color = widget.cget("fg_color")
        flash_color = "#ff0000"
        widget.configure(fg_color=flash_color)
        self.after(100, lambda: widget.configure(fg_color=original_color))

    def send_message(self, tab, textbox, entry):
        logger.info("Sending message...")
        try:
            message = entry.get()
            if message:
                tab.chat_history.append(
                    {"role": "user", "content": f"<p>🧑 You: {message}</p>"}
                )
                self.update_textbox_html(tab, textbox)
                entry.delete(0, "end")
                self.menu_frame.progress_bar.grid()
                self.menu_frame.progress_bar.start()

                # TODO: send the chat history to the AI
                thread = threading.Thread(
                    target=self._get_ai_response_threaded,
                    args=(tab, textbox, message, tab.model),
                )
                thread.start()
                logger.info("Message sent successfully")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _get_chat_history(self, tab):
        logger.info("Getting chat history...")
        try:
            # TODO: convert the chat history to a list of messages suitable for processing by aisuite
            return tab.chat_history
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _get_ai_response_threaded(self, tab, textbox, message, model):
        logger.info("Getting AI response...")
        try:
            anyllm = True
            chat_history = None
            ui_chat_history = self._get_chat_history(tab)
            if anyllm:
                chat_history = self.anyllm_adapter.getChatHistory(
                    ui_chat_history
                )
                # TODO: use anyllm adapter
                response = self.anyllm_adapter.completion(model, chat_history)
            else:
                # aisuite adapter
                chat_history = self.aisuite_adapter.getChatHistory(
                    ui_chat_history
                )
                response = self.aisuite_adapter.completion(model, chat_history)
            #chat_history.append({"role": "user", "content": message})

            '''
            client = ai.Client()

            base_url = None
            if "openai" in model:
                base_url = os.getenv("OPENAI_API_URL")

            response = None
            if base_url is not None:
                response = client.chat.completions.create(
                    model=model, messages=chat_history, base_url=base_url
                )
            else:
                response = client.chat.completions.create(
                    model=model, messages=chat_history
                )

            if response is not None:
                response = self.aisuite_adapter.getResponse(response)
            '''

            self.after(0, self.get_ai_response, tab, textbox, response["content"], None)
            logger.info("AI response received successfully")
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            logger.error(traceback.format_exc())
            self.after(0, self.get_ai_response, tab, textbox, None, e)

    def get_ai_response(self, tab, textbox, response_text, error):
        logger.info("Processing AI response...")
        try:
            if error:
                tab.chat_history.append(
                    {"role": "assistant", "content": f"<p>Error: {error}</p>"}
                )
            else:
                md = MarkdownIt()
                md.use(front_matter_plugin)
                html = "Unexpected Response"
                if response_text is not None:
                    html = md.render(response_text)

                tab.chat_history.append(
                    {"role": "assistant", "content": f"🤖 AI: {html}"}
                )

            self.update_textbox_html(tab, textbox)
            self.menu_frame.progress_bar.stop()
            self.menu_frame.progress_bar.grid_remove()
            logger.info("AI response processed successfully")
        except Exception as e:
            logger.error(f"Error processing AI response: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def update_textbox_html(self, tab, textbox):
        logger.info("Updating textbox HTML...")
        try:
            import pprint

            pprint.pprint(tab.chat_history)
            history_html = "".join([msg["content"] for msg in tab.chat_history])

            soup = BeautifulSoup(history_html, "html.parser")

            base_color = (
                "white" if customtkinter.get_appearance_mode() == "Dark" else "black"
            )

            darkgold = "#c09900"
            darkblue = "#2384c8"
            darkgreen = "#2aa198"
            darkred = "#a6451c"
            style_map = {
                "b": f"color: {darkgold}; font-weight: bold;",
                "strong": f"color: {darkgold}; font-weight: bold;",
                "i": f"color: {darkgreen}; font-style: italic;",
                "em": f"color: {darkblue}; font-style: italic;",
                "u": f"color: {darkblue}; text-decoration: underline;",
                "s": f"color: {darkred}; text-decoration: line-through;",
                "strike": f"color: {darkred}; text-decoration: line-through;",
                "code": f"color: {darkgreen}; font-weight: bold;",
                "h1": f"color: {darkred}; font-weight: bold;",
                "h2": f"color: {darkred}; font-weight: bold;",
                "h3": f"color: {darkred}; font-weight: bold;",
                "h4": f"color: {darkred}; font-weight: bold;",
                "h5": f"color: {darkred}; font-weight: bold;",
                "h6": f"color: {darkred}; font-weight: bold;",
            }

            for tag_name, style in style_map.items():
                for tag in soup.find_all(tag_name):
                    if tag.has_attr("style"):
                        tag["style"] += f" {style}"
                    else:
                        tag["style"] = style

            body = soup.find("body")
            if body:
                body["style"] = f"color: {base_color};"
            else:
                # If no body tag, wrap in a div
                new_soup = BeautifulSoup(
                    f'<div style="color: {base_color};"></div>', "html.parser"
                )
                new_soup.div.append(soup)
                soup = new_soup

            html_to_render = str(soup)
            textbox.set_html(html_to_render)
            textbox.config(state=tk.NORMAL)
            textbox.see(tk.END)
            logger.info("Textbox HTML updated successfully")
        except Exception as e:
            logger.error(f"Error updating textbox HTML: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def open_preferences(self):
        logger.info("Opening preferences...")
        try:
            preferences_window = PreferencesWindow(self)
            preferences_window.grab_set()
            logger.info("Preferences window opened successfully")
        except Exception as e:
            logger.error(f"Error opening preferences: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def open_voice_input(self, tab, entry):
        """Start voice input recording using external listen command."""
        logger.info("Starting voice input...")
        try:
            def on_transcription_complete(transcribed_text):
                """Callback when transcription is complete."""
                logger.info(f"Voice transcription complete: {transcribed_text}")
                # Insert transcribed text into the entry box
                self.after(0, lambda: entry.delete(0, "end"))
                self.after(0, lambda: entry.insert(0, transcribed_text))
                # Focus the entry box for user review
                self.after(0, lambda: entry.focus_set())

            # Start voice input (this will open the listen command's UI window)
            voice_input = VoiceInput(on_complete=on_transcription_complete)
            voice_input.start_recording()
            logger.info("Voice input started successfully")
        except Exception as e:
            logger.error(f"Error starting voice input: {str(e)}")
            logger.error(traceback.format_exc())
            self.show_transient_message(f"Voice input error: {e}", is_error=True)

    def apply_font_change(self):
        logger.info("Applying font change...")
        try:
            self.load_config()
            font = (None, self.font_size)
            for tab_name in self.tab_view._name_list:
                tab = self.tab_view.tab(tab_name)
                for widget in tab.winfo_children():
                    if isinstance(widget, (HTMLScrolledText, customtkinter.CTkEntry)):
                        widget.configure(font=font)
                    if (
                        isinstance(widget, HTMLScrolledText)
                        and customtkinter.get_appearance_mode() == "Dark"
                    ):
                        widget.configure(background="#2b2b2b")
            logger.info("Font change applied successfully")
        except Exception as e:
            logger.error(f"Error applying font change: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def bind_shortcuts(self):
        logger.info("Binding shortcuts...")
        try:
            self.bind("<Control-m>", self.show_menu_ctrl_m)
            self.bind("<Control-Shift-T>", lambda event: self.add_new_tab())
            self.bind("<Control-Shift-R>", lambda event: self.rename_current_tab())
            self.bind("<Control-w>", lambda event: self.close_current_tab())
            self.bind("<Control-q>", lambda event: self.destroy())
            self.bind("<Control-s>", lambda event: self.save_current_tab())
            self.bind("<Control-o>", lambda event: self.open_tab())
            self.bind("<Control-l>", lambda event: self.refresh_current_tab_history())
            self.bind("<Control-Shift-H>", lambda event: self.clear_current_tab_history())
            logger.info("Shortcuts bound successfully")
        except Exception as e:
            logger.error(f"Error binding shortcuts: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def show_menu_ctrl_m(self, event):
        logger.info("Showing menu...")
        try:
            self.menu_frame.menu.tk_popup(self.winfo_x() + 5, self.winfo_y() + 30)
        except Exception as e:
            logger.error(f"Error showing menu: {str(e)}")
            logger.error(traceback.format_exc())
            raise


def main():
    """Main entry point for the application."""
    try:
        log_environment()

        # Set display environment variables if not set
        if "DISPLAY" not in os.environ:
            os.environ["DISPLAY"] = ":0"
        if "WAYLAND_DISPLAY" not in os.environ:
            os.environ["WAYLAND_DISPLAY"] = "wayland-0"

        logger.info("Creating application instance...")
        app = App()

        logger.info("Starting main event loop...")
        app.mainloop()

        logger.info("Application exited normally")

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"\nA critical error occurred. Check the log file at: {log_file}")
        input("Press Enter to exit...")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
