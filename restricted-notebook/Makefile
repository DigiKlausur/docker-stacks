VERSION=$(shell git rev-parse --short HEAD)
IMAGE=digiklausur/restricted-notebook
IMAGE_DEV=digiklausur/restricted-notebook-dev

release: VERSION=$(shell  git tag -l --points-at HEAD)

build_dev:
	docker build -t $(IMAGE_DEV):$(VERSION) .

push_dev:
	docker push $(IMAGE_DEV):$(VERSION)

build:
	docker build -t $(IMAGE):$(VERSION) .

push:
	docker push $(IMAGE):$(VERSION)

#release: build push
