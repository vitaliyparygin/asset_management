# Odoo 18 development commands
#
# Module: asset_management
# Database: odoo18-dev
#
# Run:
#   make help
#
# Examples:
#   make xmlcheck
#   make pycheck
#   make odoorestart
#   make logs


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

# Validate demo/demo.xml syntax using lxml.
xmlcheck:
	docker compose exec odoo python3 -c "from lxml import etree; etree.parse('/mnt/extra-addons/asset_management/demo/demo.xml'); print('XML OK')"

# Check Python syntax of the addon.
pycheck:
	docker compose exec odoo python3 -m compileall -q /mnt/extra-addons/asset_management && echo "Python OK"

# Show Makefile with visible tabs, spaces and line endings.
validmake:
	cat -vet Makefile


# ---------------------------------------------------------
# Module
# ---------------------------------------------------------

# Update asset_management and restart Odoo.
#
# Keep this as one shell command so the Odoo container is
# always started again after the update command succeeds.
odoorestart:
	docker compose stop odoo && docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo18-dev -u asset_management --stop-after-init --http-port=8071 && docker compose start odoo

# Update the module without restarting the normal Odoo container.
module-update:
	docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo18-dev -u asset_management --stop-after-init --http-port=8071

# Install the module.
module-install:
	docker compose run --rm odoo odoo -c /etc/odoo/odoo.conf -d odoo18-dev -i asset_management --stop-after-init --http-port=8071


# ---------------------------------------------------------
# Docker
# ---------------------------------------------------------

# Show running containers.
ps:
	docker compose ps

# Start Odoo.
start:
	docker compose start odoo

# Stop Odoo.
stop:
	docker compose stop odoo

# Restart Odoo.
restart:
	docker compose restart odoo

# Restart all Docker services.
restart-all:
	docker compose restart


# -------------------------------
shell:
	docker compose exec odoo odoo shell -c /etc/odoo/odoo.conf -d odoo18-dev



