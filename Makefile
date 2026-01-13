PREFIX ?= /usr/local

.PHONY: install uninstall

install:
	@echo "Installing compress-pdf to $(PREFIX)/bin..."
	@mkdir -p $(PREFIX)/bin
	@cp compress-pdf $(PREFIX)/bin/compress-pdf
	@chmod +x $(PREFIX)/bin/compress-pdf
	@echo "Done. Run 'compress-pdf --help' to get started."

uninstall:
	@echo "Removing compress-pdf from $(PREFIX)/bin..."
	@rm -f $(PREFIX)/bin/compress-pdf
	@echo "Done."
