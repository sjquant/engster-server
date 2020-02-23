init-db:
	/bin/bash scripts/init-db.sh

make-migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

downgrade:
	python manage.py downgrade

run-server:
	/bin/bash scripts/start-dev.sh
	