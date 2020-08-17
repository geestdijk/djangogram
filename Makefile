SRC_DIR:=./


CMD_FROM_VENV:="which $(VIRTUAL_ENV)/bin/activate"
PYTHON=$(shell "$(CMD_FROM_VENV)" "python")

# TOOLS/SCRIPTS

migrations:
	@$(PYTHON) $(SRC_DIR)/manage.py makemigrations $(app)

migrate:
	@$(PYTHON) $(SRC_DIR)/manage.py migrate $(app) $(migration)

superuser:
	@$(PYTHON) $(SRC_DIR)/manage.py createsuperuser

run:
	@$(PYTHON) $(SRC_DIR)/manage.py runserver
