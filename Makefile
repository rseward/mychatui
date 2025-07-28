run:
	.venv/bin/python -m mychatui.app

venv:
	uv venv --system-site-packages --python /usr/bin/python3.13 .venv
	#uv venv --python python3.11 .venv
	.venv/bin/python -m ensurepip
	.venv/bin/python -m pip install -r requirements.txt

install:
	.venv/bin/python -m pip install -r requirements.txt
	#.venv/bin/python setup.py sdist bdist_wheel
	.venv/bin/python -m pip install .
