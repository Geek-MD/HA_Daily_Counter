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
	hassfest --integration $(PACKAGE)

ci: lint typecheck hassfest
	@echo "✅ CI pipeline completed successfully."
