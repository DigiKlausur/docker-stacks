ifeq ($(CONTAINER_REG_OWNER),)
$(info ERROR! container regisrty and owner is not set)
$(info example for docker hub registry/owner)
$(info CONTAINER_REG_OWNER=registry.hub.docker.com/digiklausur)
$(error CONTAINER_REG_OWNER is not set)
endif

ifeq ($(IMAGE),)
$(info ERROR!)
$(info Specify image, e.g. notebook, minimal-notebook)
$(error IMAGE is not set)
endif

ifeq ($(VERSION),)
$(info VERSION is not set)
VERSION=$(shell git rev-parse --short HEAD)
$(info using verison --> $(VERSION))
else
$(info using version --> $(VERSION))
endif

build:
	docker build -t $(CONTAINER_REG_OWNER)/$(IMAGE):$(VERSION) $(IMAGE)

push:
	docker push $(CONTAINER_REG_OWNER)/$(IMAGE):$(VERSION) $(IMAGE)

