db-init:
	python manage.py migrate && python manage.py init

make-migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

downgrade:
	python manage.py downgrade

run-server:
	/bin/bash scripts/start-dev.sh
	