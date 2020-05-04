OWNER=digiklausur
VERSION=$(shell git rev-parse --short HEAD)
IMAGE=$(OWNER)/restricted-notebook

build:
	docker build -t $(IMAGE):$(VERSION) .

push:
	docker push $(IMAGE):$(VERSION)

