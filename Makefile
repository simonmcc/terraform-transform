.PHONY: entr

test:
	poetry install
	poetry run python -m unittest -v
	(cd examples/terraform ; poetry run make)
	(cd examples/terragrunt ; poetry run make)

build:
	poetry build

publish: build
	# pypy-all is our internal repo, pypi-all is a group consisting of pypy-all & pypi-proxy
	poetry config repositories.nexus https://nexus.taservs.net/repository/pypy-all/
	poetry publish -r nexus

entr:
	find . -name '*.py' | entr -c poetry run python -m unittest -v

install_tools_macos:
	brew install poetry

clean:
	rm -rf .coverage .mypy_cache .pytest_cache dist poetry.lock