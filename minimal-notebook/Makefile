OWNER=digiklausur
VERSION=$(shell git rev-parse --short HEAD)
IMAGE_DEV=$(OWNER)/minimal-notebook-dev
IMAGE=$(OWNER)/minimal-notebook

build_dev:
	docker build -t $(IMAGEi_DEV):$(VERSION) .

push_dev:
	docker push $(IMAGE_DEV):$(VERSION)

build:
	docker build -t $(IMAGE):$(VERSION) .

push:
	docker push $(IMAGE):$(VERSION)

