# Development Guide

This document describes the development commands provided by the project `Makefile`.

The project uses:

* **Odoo 18**
* **Docker Compose**
* **PostgreSQL**
* Module: `asset_management`
* Database: `odoo18-dev`

Run commands from the `asset_management` directory.

---

## Quick Reference

| Command               | Purpose                          |
| --------------------- | -------------------------------- |
| `make help`           | Show available Makefile commands |
| `make xmlcheck`       | Validate demo XML syntax         |
| `make pycheck`        | Check Python syntax              |
| `make validmake`      | Display Makefile whitespace      |
| `make odoorestart`    | Update module and restart Odoo   |
| `make module-update`  | Update the module                |
| `make module-install` | Install the module               |
| `make ps`             | Show Docker containers           |
| `make start`          | Start Odoo                       |
| `make stop`           | Stop Odoo                        |
| `make restart`        | Restart Odoo                     |
| `make restart-all`    | Restart all Docker services      |

---

# Validation

## `make xmlcheck`

Validates the syntax of:

```text
demo/demo.xml
```

using `lxml`.

Run:

```bash
make xmlcheck
```

The command checks that the XML file can be parsed successfully.

Expected output:

```text
XML OK
```

### Important

This checks **XML syntax only**.

It does not validate:

* Odoo models;
* external IDs;
* field names;
* XML references;
* access rights;
* Odoo-specific XML structure.

---

## `make pycheck`

Checks Python syntax for the entire addon.

Run:

```bash
make pycheck
```

The command uses Python's `compileall`:

```bash
python3 -m compileall
```

and scans:

```text
/mnt/extra-addons/asset_management
```

inside the Odoo container.

Expected output:

```text
Python OK
```

This is a syntax check only. It does not execute the module code or run Odoo tests.

---

## `make validmake`

Displays the Makefile with invisible characters visible.

Run:

```bash
make validmake
```

Internally it uses:

```bash
cat -vet Makefile
```

This is especially useful for debugging Makefile errors such as:

```text
missing separator
```

The most common cause is using spaces instead of a TAB before a command.

For example, a Makefile recipe must use a TAB:

```makefile
xmlcheck:
<TAB>docker compose ...
```

`make validmake` makes the TAB visible as:

```text
^I
```

---

# Module Management

## `make odoorestart`

This is the main development command for updating the module.

Run:

```bash
make odoorestart
```

It performs the following sequence:

```text
1. Stop the normal Odoo container
2. Start a temporary Odoo container
3. Update asset_management
4. Stop the temporary container
5. Start the normal Odoo container
```

The actual Odoo update uses:

```text
-u asset_management
```

and:

```text
--stop-after-init
```

The temporary Odoo process uses port `8071` so it does not conflict with the normal Odoo server.

### Use this after

* changing Python models;
* changing fields;
* changing constraints;
* changing XML views;
* changing security;
* changing reports;
* changing demo data;
* changing module configuration.

### Example

```bash
make pycheck
make odoorestart
```

---

## `make module-update`

Updates the `asset_management` module without explicitly stopping and starting the normal Odoo container.

Run:

```bash
make module-update
```

The command executes:

```text
-u asset_management
```

with:

```text
--stop-after-init
```

This command is useful when the normal Odoo container is already stopped.

For the normal development workflow, `make odoorestart` is generally more convenient because it also starts the regular Odoo container again.

---

##
