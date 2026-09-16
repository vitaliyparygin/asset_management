# Asset Statuses

## Overview

Each asset has a status that shows its current condition.

There are four statuses:

* **Available** — the equipment is ready to be given to an employee.
* **Issued** — the equipment is currently given to an employee.
* **Maintenance** — the equipment is temporarily unavailable because it needs repair or checking.
* **Retired** — the equipment is no longer used.

## Status changes

### Available → Issued

An available asset can be issued to an employee using the **Issue** button.

The system saves the employee, issue date and issue history.

### Issued → Available

An issued asset can be returned using the **Return** button.

The return is saved in the issue history and the asset becomes available again.

An issued asset must be returned before it can be moved to another status.

### Available → Maintenance

An Asset System Administrator can manually set an available asset to **Maintenance**.

An asset in maintenance cannot be issued.

When the work is finished, the System Administrator can change it back to **Available**.

### Available → Retired

An Asset Manager can mark an available asset as **Retired**.

A retired asset cannot be issued.

## Simple lifecycle

```text
Available
   │
   ├── Issue ──→ Issued ── Return ──→ Available
   │
   ├──→ Maintenance ──→ Available
   │
   └──→ Retired
```

The normal workflow is:

**Available → Issued → Available**

Maintenance and Retired are separate from the normal issue/return process.

## Maintenance

Maintenance is only a status at the moment.

The module does not have a separate maintenance system for:

* repair orders;
* repair history;
* costs;
* vendors;
* maintenance dates.

This can be added later if needed.

## Permissions

**Asset User** can use the normal Issue and Return workflow.

**Asset Manager** can also change asset information and statuses such as Maintenance and Retired.

## Demo data

Maintenance assets in the demo data are only examples. They are not required for the module to work.
