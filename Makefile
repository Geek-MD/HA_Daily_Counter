.PHONY: lint typecheck hassfest ci

PACKAGE=custom_components/ha_daily_counter

lint:
	@echo "🔍 Running Ruff Linter..."
	ruff check $(PACKAGE)

typecheck:
	@echo "🔍 Running Mypy Type Checking..."
	mypy --config-file mypy.ini $(PACKAGE)

hassfest:
	@echo "🔍 Running Hassfest validation..."
	@if [ ! -d "hassfest-core" ]; then \
		echo "📥 Downloading Home Assistant core stable release..."; \
		git clone --depth 1 --branch 2024.5.3 https://github.com/home-assistant/core hassfest-core; \
	else \
		echo "✅ Using cached hassfest-core"; \
	fi
	cd hassfest-core && python3 -m script.hassfest --integration ../$(PACKAGE)

ci: lint typecheck hassfest
	@echo "✅ CI pipeline completed successfully."
