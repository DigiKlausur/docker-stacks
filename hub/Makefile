OWNER=digiklausur
IMAGE_DEV=$(OWNER)/k8s-hub-dev
IMAGE=$(OWNER)/k8s-hub

build_dev:
	docker build -t $(IMAGE_DEV):0.9.0 0.9.0
	docker build -t $(IMAGE_DEV):0.9.1 0.9.1
	docker build -t $(IMAGE_DEV):0.10.0 0.10.0
	docker build -t $(IMAGE_DEV):0.10.2 0.10.2

push_dev:
	docker push $(IMAGE_DEV):0.9.0
	docker push $(IMAGE_DEV):0.9.1
	docker push $(IMAGE_DEV):0.10.0
	docker push $(IMAGE_DEV):0.10.2

build:
	docker build -t $(IMAGE):0.9.0 0.9.0
	docker build -t $(IMAGE):0.9.1 0.9.1
	docker build -t $(IMAGE):0.10.0 0.10.0
	docker build -t $(IMAGE):0.10.2 0.10.2

push:
	docker push $(IMAGE):0.9.0
	docker push $(IMAGE):0.9.1
	docker push $(IMAGE):0.10.0
	docker push $(IMAGE):0.10.2

