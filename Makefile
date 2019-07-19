.PHONY: test

test:
	docker-compose run --rm --entrypoint sh app src/scripts/run_tests.sh
