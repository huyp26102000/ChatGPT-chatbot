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
#run-pynb:
#	./venv/Scripts/python.exe -m jupyter nbconvert --to python nb.ipynb

convert-resource:
	./venv/Scripts/python.exe -m PyQt5.pyrcc_main .\assets\resourcesV2.qrc -o .\source\ui\resourcesV2_rc.py

convert-main:
	./venv/Scripts/python.exe -m PyQt5.uic.pyuic -x .\ui_components\main.ui -o .\source\ui\main.py

convert-login:
	./venv/Scripts/python.exe -m PyQt5.uic.pyuic -x .\ui_components\login.ui -o .\source\ui\login.py

#sharememory
#intercommunication
#messagebasing