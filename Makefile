.PHONY: test local-test

test:
	docker-compose run --rm --entrypoint sh app src/scripts/run_tests.sh


local-test:
	cd local-test && docker-compose run --rm --entrypoint sh taxonomy_re_api src/scripts/run_local_tests.sh 

start-ui-dev:
	cd local-ui-dev && docker-compose up taxonomy_re_api && docker-compose down && docker-compose rm --force
