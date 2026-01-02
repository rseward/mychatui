MAKEFLAGS += -S # Stop on first error
run:
	.venv/bin/python -m mychatui.app

venv:
	uv venv --system-site-packages --python /usr/bin/python3.14 .venv
	#uv venv --python /home/linuxbrew/.linuxbrew/bin/python3.13 .venv
	#uv venv --system-site-packages --python /usr/bin/python3.13 .venv # F42
	#uv venv --python python3.11 .venv
	.venv/bin/python -m ensurepip
	.venv/bin/python -m pip install -r requirements.txt

install:
	.venv/bin/python -m pip install -r requirements.txt
	#.venv/bin/python setup.py sdist bdist_wheel
	.venv/bin/python -m pip install .

lint:
	cd mychatui; ruff check
	cd mychatui; ruff format

test:
	.venv/bin/python -m pytest tests

desktop:
	# Create necessary directories
	mkdir -p ~/.local/share/icons/hicolor/128x128/apps/
	mkdir -p ~/.local/share/icons/hicolor/48x48/apps/
	mkdir -p ~/.local/share/applications/

	# Copy desktop file
	desktop-file-validate resources/mychatui.desktop
	cp resources/mychatui.desktop ~/.local/share/applications/
	chmod 755 ~/.local/share/applications/mychatui.desktop

	# Copy icons to standard XDG directories
	cp resources/jarvis128.png ~/.local/share/icons/hicolor/128x128/apps/mychatui.png
	cp resources/jarvis48.png ~/.local/share/icons/hicolor/48x48/apps/mychatui.png

	# Create symbolic links for backward compatibility
	mkdir -p ~/.local/share/mychatui.app/share/icons/hicolor/128x128/apps/
	mkdir -p ~/.local/share/mychatui.app/share/icons/hicolor/48x48/apps/
	ln -sf ~/.local/share/icons/hicolor/128x128/apps/mychatui.png ~/.local/share/mychatui.app/share/icons/hicolor/128x128/apps/jarvis128.png
	ln -sf ~/.local/share/icons/hicolor/48x48/apps/mychatui.png ~/.local/share/mychatui.app/share/icons/hicolor/48x48/apps/jarvis48.png

	# Update icon cache and desktop database
	gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor/
	update-desktop-database ~/.local/share/applications/

	@echo "Installation complete! You may need to log out and back in for all changes to take effect."
