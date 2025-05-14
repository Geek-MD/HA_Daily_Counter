.PHONY: lint typecheck hassfest clean ci

# Variables
PACKAGE=custom_components/ha_daily_counter

## -----------------------------------
## 🧹 Lint with Ruff
lint:
	@echo "🔍 Running Ruff Linter..."
	ruff check $(PACKAGE)

## -----------------------------------
## 🩺 Type checking with Mypy
typecheck:
	@echo "🔍 Running Mypy Type Checking..."
	mypy --config-file mypy.ini $(PACKAGE)

## -----------------------------------
## 🔍 Validate manifest & structure with Hassfest
hassfest:
	@echo "🔍 Running Hassfest validation..."
	@if [ ! -d "hassfest-core" ]; then \
		echo "📥 Downloading Home Assistant core repo..."; \
		git clone --depth 1 --single-branch --branch dev https://github.com/home-assistant/core hassfest-core; \
	fi
	python3 hassfest-core/script/hassfest --integration $(PACKAGE)
	@echo "🧹 Cleaning up hassfest-core..."
	rm -rf hassfest-core

## -----------------------------------
## 🗑️ Clean hassfest-core manually (if needed)
clean:
	@echo "🧹 Cleaning hassfest-core folder (if exists)..."
	rm -rf hassfest-core

## -----------------------------------
## 🧪 CI pipeline: lint + typecheck + hassfest
ci: lint typecheck hassfest
	@echo "✅ CI pipeline completed successfully."
