import unittest
from unittest.mock import patch, MagicMock
import os
import json
from mychatui.app import App


class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a mock for customtkinter
        self.customtkinter_patch = patch("mychatui.app.customtkinter")
        self.mock_customtkinter = self.customtkinter_patch.start()

        # Create a mock for the config file
        self.config_data = {
            "api_key": "test_key",
            "model": "test_model",
            "font_size": 14,
            "active_tabs": ["Tab 1", "Tab 2"],
            "user_models": [{"display_name": "Test Model", "full_name": "test_model"}],
        }
        self.open_patch = patch(
            "builtins.open",
            unittest.mock.mock_open(read_data=json.dumps(self.config_data)),
        )
        self.mock_open = self.open_patch.start()

        # Create a mock for App
        self.app = App()

    def tearDown(self):
        self.customtkinter_patch.stop()
        self.open_patch.stop()

    def test_load_config_creates_default_config_if_not_exists(self):
        # Given
        with patch("os.path.exists", return_value=False):
            # When
            self.app.load_config()

            # Then
            self.assertEqual(
                self.app.config,
                {
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
                },
            )

    def test_load_config_loads_existing_config(self):
        # Given
        config_data = {
            "api_key": "test_key",
            "model": "test_model",
            "font_size": 14,
            "active_tabs": ["Tab 1", "Tab 2"],
            "user_models": [{"display_name": "Test Model", "full_name": "test_model"}],
        }
        with patch("os.path.exists", return_value=True):
            with patch(
                "builtins.open",
                unittest.mock.mock_open(read_data=json.dumps(config_data)),
            ):
                # When
                self.app.load_config()

                # Then
                self.assertEqual(self.app.config, config_data)

    def test_save_config_saves_config_to_file(self):
        # Given
        self.app.config = {
            "api_key": "test_key",
            "model": "test_model",
            "font_size": 14,
            "active_tabs": ["Tab 1", "Tab 2"],
            "user_models": [{"display_name": "Test Model", "full_name": "test_model"}],
        }
        self.app.tab_view = MagicMock()
        self.app.tab_view._name_list = ["Tab 1", "Tab 2", "Tab 3"]
        mock_open = unittest.mock.mock_open()
        with patch("builtins.open", mock_open):
            # When
            self.app.save_config()

            # Then
            mock_open.assert_called_once_with(self.app.config_file, "w")
            handle = mock_open()
            written_data = "".join(call.args[0] for call in handle.write.call_args_list)
            self.assertEqual(
                json.loads(written_data),
                {
                    "api_key": "test_key",
                    "model": "test_model",
                    "font_size": 14,
                    "active_tabs": ["Tab 1", "Tab 2", "Tab 3"],
                    "user_models": [
                        {"display_name": "Test Model", "full_name": "test_model"}
                    ],
                },
            )

    def test_add_new_tab_adds_tab_with_default_model(self):
        # Given
        self.app.config = {"model": "default_model"}
        self.app.tab_view = MagicMock()
        self.app.tab_view.tab.return_value = MagicMock()

        # When
        self.app.add_new_tab("Test Tab")

        # Then
        self.app.tab_view.add.assert_called_once_with("Test Tab")
        tab = self.app.tab_view.tab.return_value
        self.assertEqual(tab.model, "default_model")

    def test_save_current_tab_saves_tab_data_to_file(self):
        # Given
        self.app.tab_view = MagicMock()
        self.app.tab_view.get.return_value = "Test Tab"
        tab = MagicMock()
        tab.model = "test_model"
        tab.chat_history = ["message1", "message2"]
        self.app.tab_view.tab.return_value = tab
        mock_open = unittest.mock.mock_open()
        with patch("builtins.open", mock_open):
            # When
            self.app.save_current_tab()

            # Then
            config_dir = os.path.dirname(self.app.config_file)
            file_path = os.path.join(config_dir, "Test Tab.json")
            mock_open.assert_called_once_with(file_path, "w")
            handle = mock_open()
            written_data = "".join(call.args[0] for call in handle.write.call_args_list)
            self.assertEqual(
                json.loads(written_data),
                {
                    "tab_name": "Test Tab",
                    "model_name": "test_model",
                    "chat_history": ["message1", "message2"],
                },
            )

    def test_open_tab_loads_tab_data_from_file(self):
        # Given
        tab_data = {
            "tab_name": "Test Tab",
            "model_name": "test_model",
            "chat_history": ["message1", "message2"],
        }
        with patch("tkinter.filedialog.askopenfilename", return_value="test_file.json"):
            with patch(
                "builtins.open", unittest.mock.mock_open(read_data=json.dumps(tab_data))
            ):
                self.app.tab_view = MagicMock()
                tab = MagicMock()
                self.app.tab_view.tab.return_value = tab
                self.app.menu_frame = MagicMock()

                # When
                self.app.open_tab()

                # Then
                self.app.tab_view.add.assert_called_once_with("Test Tab")
                self.assertEqual(tab.model, "test_model")
                self.assertEqual(tab.chat_history, ["message1", "message2"])
                self.app.menu_frame.update_model_menu.assert_called_once()


if __name__ == "__main__":
    unittest.main()
