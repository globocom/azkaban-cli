.PHONY: clean release

ROOT_PATH=$(shell pwd)

clean:
	-@rm -rf $(ROOT_PATH)/*.egg-info
	-@rm -rf $(ROOT_PATH)/dist
	-@rm -rf $(ROOT_PATH)/build

test:
	@python -m unittest

check-sec:
	@echo "Installing Bandit..."
	@pip install bandit
	@echo "Running Bandit..."
	@bandit -r .