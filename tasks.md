# Pending tasks

# Deferred Tasks

- [x] tkhtmlview does not allow the mouse to highlight text prior to the copy action. Complete this feature.


# Completed tasks

## Hamburger Menu
- [x] Ensure the hamburger menu appears in the first row of the UI. I belive you need to define it as one of the first widgets in that row.
- [x] Add a hamburger menu to the top left of the window
- [x] Move New Tab, Rename Tab, Close Tab and preferences to the hamburger menu
- [x] In the tkhtmlview render bolded text in a gold color and bold font.
- [x] In the tkhtmlview render italicized text in a green color and italic font.
- [x] In the tkhtmlview render underlined text in a blue color and underlined font.
- [x] In the tkhtmlview render strikethrough text in a red color and strikethrough font.
- [x] In the tkhtmlview render code text in a blue color and bold font.
- [x] Where possible bind a Ctrl-m shortcut to access the menu
- [x] Add a Ctrl-Shift-T shortcut to create a new tab
- [x] Add a Ctrl-Shift-R shortcut to rename the current tab
- [x] Add a Ctrl-w shortcut to close the current tab
- [x] Add a Ctrl-q shortcut to quit the application
- [x] Add a Ctrl-s shortcut to save the current tab and it's chat history
- [x] Add a Ctrl-o shortcut to open a saved tab
- [x] Add a hamburger menu item to clear the chat history for the current tab. Also add a keyboard shortcut to clear the chat history for the current tab: Ctrl-Shift-h

## Tab Management

- [x] In the ~/.config/mychatui/config.json file, the tabs config element shall be renamed to active_tabs.
- [x] On application start up, the active_tabs config element shall be read and the tabs shall be created and restored to the state they were saved in.
- [x] On the preferences dialog, the model selection drop down specifies the default model for new tabs. The model selection drop down should also specify the model for each tab. The model selection drop down should be populated with the models read from the user_models element of the config file.
- [x] Add a tab model dropdown to the right edge of the ui row that displays the tab buttons. The model dropdown should be in the same row as the tab buttons. The model dropdown should be aligned to the right edge of the row. The selected model should apply to the current tab. Each tab can be assigned a different model. The drop down choice applies to the current tab. When a new tab is selected the drop down selection shall be changed to the tab's current model. The model name for a tab should be available to the on_send method that sends the chat to the AI.
- [x] When saving a tab provide confirmation via a confirmation or failure message that fades after 5 seconds. Success messages shall be green and failure messages shall be red.
- [x] complete the tab save feature. There should be one tab save file per tab. The format of the save file shall be JSON. The tab save file should be named after the tab name. The tab save file should be saved in the same directory as the user's application data: ~/.config/mychatui/. The following information should be saved for each tab:
  1. The tab name
  2. The model name
  3. The chat history
- [x] complete the tab open feature. The tab open feature should load a tab save file and restore the tab to the state it was saved in. If the tab is already open, reload it's chat window content from the saved file.
- [x] When opening a saved tab, refresh the chat history in the UI from the tab's loaded chat history.

## General

- [x] Create tests for the new features.
- [x] Analyze README.md and write the python code to implement the features described in it

## Chat Message Text Box

- [x] In the chat message entry textbox, add a keyboard shortcuts to move to the previous message sent in the history. Up arrow  keybinding moves to the previous message. Down arrow keybinding moves to the next message. Flash when the user has navigated to the end or beginning of the history.
- [x] Write a refresh method for the chat history to refresh the chat history in the UI from the tab's chat history.
- [x] Bind a keyboard shortcut to refresh the chat history for the current tab: Ctrl-l


## Multi Model Support
- [x] Add support for multiple AI models using the python model aisuite
- [x] Available models will be read from the ~/.config/mychatui/config.json file the user_models element of the config.
