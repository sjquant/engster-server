# Inside container
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

# Outside container
dev-shell:
	docker-compose -f docker-compose.dev.yml run engster_server /bin/bash
dev-up:
	docker-compose -f docker-compose.dev.yml up --build
dev-down:
	docker-compose -f docker-compose.dev.yml down $(args)
dev-init-db:
	docker-compose -f docker-compose.dev.yml run --rm engster_server /bin/bash scripts/init-db.sh
dev-migrations:
	docker-compose -f docker-compose.dev.yml run --rm engster_server /bin/bash -c "python manage.py make-migrations"
dev-migrate:
	docker-compose -f docker-compose.dev.yml run --rm engster_server /bin/bash -c "python manage.py migrate"

clean:
	rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./out ./*/out ./.mypy_cache ./*/.mypy_cache */.pytest_cache .pytest_cache