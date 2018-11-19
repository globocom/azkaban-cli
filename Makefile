.PHONY: clean release

ROOT_PATH=$(shell pwd)

clean:
	-@rm -rf $(ROOT_PATH)/*.egg-info
	-@rm -rf $(ROOT_PATH)/dist
	-@rm -rf $(ROOT_PATH)/build

release: 
	@python setup.py sdist upload -r pypi

dist: clean
	@python setup.py sdist

test:
	@python -m unittest
