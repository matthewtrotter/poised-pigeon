mkfile_abs_path := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))

messages:
	@echo "Compiling proto files into messages defs..."
	protoc -I. --python_out=. lnsalerts.proto
