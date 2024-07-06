all: build

build:
	cargo build --release

install: build
	install -D target/release/xylo $(HOME)/.local/bin/xylo

uninstall:
	rm -f $(HOME)/.local/bin/xylo

clean:
	cargo clean
