OWNER=digiklausur
IMAGE=$(OWNER)/k8s-hub

build:
	docker build -t $(IMAGE):0.9.0 0.9.0
	docker build -t $(IMAGE):0.9.1 0.9.1

push:
	docker push $(IMAGE):0.9.0
	docker push $(IMAGE):0.9.1

