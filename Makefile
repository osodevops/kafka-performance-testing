NAMESPACE := osodevops
NAME := kafka_perf_testing
VERSION := $(shell grep '^version:' galaxy.yml | awk '{print $$2}')
TARBALL := $(NAMESPACE)-$(NAME)-$(VERSION).tar.gz

.PHONY: lint build publish clean install

lint:
	yamllint .
	ansible-lint

build:
	ansible-galaxy collection build --force

publish: build
	ansible-galaxy collection publish $(TARBALL) --api-key $(GALAXY_API_KEY)

clean:
	rm -f $(NAMESPACE)-$(NAME)-*.tar.gz

install: build
	ansible-galaxy collection install $(TARBALL) --force
