VERSION=$(shell git rev-parse --short HEAD)
IMAGE_DEV=digiklausur/ngshare-dev
IMAGE=digiklausur/ngshare

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
