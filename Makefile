.PHONY: entr

test:
	poetry run python -m unittest -v
	(cd examples/terraform ; make)

build:
	poetry build

publish:
	poetry publish -r nexus

entr:
	find . -name '*.py' | entr -c poetry run python -m unittest -v

install_tools_macos:
	brew install poetry

clean:
	rm -rf .coverage .mypy_cache .pytest_cache dist poetry.lock
