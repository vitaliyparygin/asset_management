# Architecture

## Overview

The module is used to keep track of company equipment given to employees.

There are three main models:

* `asset.management.asset` — information about the equipment.
* `asset.management.issue` — history of equipment issues and returns.
* `asset.management.asset.type` — equipment types, for example Laptop, Phone, Monitor.

There is also a small wizard used when equipment is issued to an employee.

## How it works

An asset can have one of these main states:

* **Available** — the equipment is not given to anyone.
* **Issued** — the equipment is currently given to an employee.
* **Maintenance** — the equipment is being repaired.
* **Retired** — the equipment is no longer in use.

When an asset is issued:

1. The user clicks **Issue**.
2. A small form asks for the employee and issue date.
3. A new issue record is created.
4. The asset changes to **Issued**.

When the asset is returned:

1. The user clicks **Return**.
2. The current issue is closed.
3. The return date is saved.
4. The asset changes back to **Available**.

The issue records keep the history, so we can see who used the equipment and when.

## Main models

| Model                           | Purpose                                  |
| ------------------------------- | ---------------------------------------- |
| `asset.management.asset.type`   | Equipment types                          |
| `asset.management.asset`        | Equipment information and current status |
| `asset.management.issue`        | Issue and return history                 |
| `asset.management.issue.wizard` | Form used to issue equipment             |

## Important rule

One asset can only be issued to **one employee at a time**.

The system checks this when issuing an asset, so it is not possible to have two active issues for the same equipment.

## Days issued

The asset shows how many days it has been issued.

The issue history also stores the number of days between the issue and return dates.

## Security

There are two user groups:

* **Asset User** — can view equipment and use the Issue/Return actions.
* **Asset Manager** — has full access to equipment, types and issue history.

Users can only work with assets from their company.

## Report

The module includes a PDF report **"Акт видачі ОЗ"**.

It can be printed from an equipment issue record and contains the basic information about the equipment, employee and issue.
