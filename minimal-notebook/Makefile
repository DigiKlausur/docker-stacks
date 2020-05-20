OWNER=digiklausur
#VERSION=$(shell git rev-parse --short HEAD)
VERSION=latest
IMAGE=$(OWNER)/minimal-notebook

build:
	docker build -t $(IMAGE):$(VERSION) .

push:
	docker push $(IMAGE):$(VERSION)

