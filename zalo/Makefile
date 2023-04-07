# init:
# 	python -m venv venv && python -m pip install -r requirements.txt

init: # for window
	python -m venv venv && ./venv/Scripts/pip.exe install -r requirements.txt
# (cd portal-api-svc-iaas-vmw && python -m flake8 service)
install:
	./venv/Scripts/pip.exe install -r requirements.txt
update-package:
	venv\Scripts\pip.exe
run:
	venv/Scripts/python.exe .\index.py
run-dev:
	venv/Scripts/python.exe .\index_dev.py