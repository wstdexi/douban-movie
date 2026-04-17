PYTHON ?= .venv/bin/python
PROTO_DIR := app/transports/grpc/proto
PROTO_FILE := $(PROTO_DIR)/movie.proto
GRPC_OUT_DIR := app/transports/grpc/generated

.PHONY: grpc-generate grpc-clean

grpc-generate:
	@mkdir -p $(GRPC_OUT_DIR)
	$(PYTHON) -m grpc_tools.protoc \
		-I $(PROTO_DIR) \
		--python_out=$(GRPC_OUT_DIR) \
		--grpc_python_out=$(GRPC_OUT_DIR) \
		$(PROTO_FILE)

grpc-clean:
	rm -f $(GRPC_OUT_DIR)/movie_pb2.py $(GRPC_OUT_DIR)/movie_pb2_grpc.py
