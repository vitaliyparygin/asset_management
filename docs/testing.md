# Testing

## Running the tests

Against a disposable database (recommended):

```bash
odoo-bin -c odoo.conf -d asset_management_test \
  -i asset_management \
  --test-enable --test-tags /asset_management \
  --stop-after-init
```

Or, against an existing database where the module is already installed,
to re-run tests on upgrade:

```bash
odoo-bin -c odoo.conf -d your_database \
  -u asset_management \
  --test-enable --test-tags /asset_management \
  --stop-after-init
```

## Test run exaample

docker compose exec odoo \
  odoo \
  -c /etc/odoo/odoo.conf \
  -d odoo18-dev \
  -u asset_management \
  --test-enable \
  --stop-after-init \
  --http-port=8071
