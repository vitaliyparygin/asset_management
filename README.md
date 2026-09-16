# Asset Management

Odoo module for tracking company equipment given to employees.

The module can be used for laptops, phones, tools, monitors and other company equipment.

## Supported Odoo version

**Odoo 18.0 Community Edition**

## Task

The company needs to keep track of equipment given to employees.

The module should allow:

* creating and managing company equipment;
* assigning equipment to an employee;
* recording the issue date;
* showing how many days the equipment has been issued;
* keeping the full issue and return history;
* preventing the same equipment from being issued to two employees at the same time;
* using **Issue** and **Return** buttons;
* returning equipment from an employee back to the company;
* viewing issue history as a Kanban board;
* grouping issue history by equipment and employee;
* printing an **"Акт видачі ОЗ"** for a specific employee and equipment.

The module should use the **standard Odoo functionality as much as possible**.

## Main features

### Equipment

Each equipment record contains basic information such as:

* name;
* equipment type;
* serial number;
* inventory number;
* current status;
* current employee.

### Issue and Return

An available asset can be issued using the **Issue** button.

The system records the employee and issue date.

The **Return** button finishes the current issue and makes the equipment available again.

One asset can have only **one active issue** at a time.

### Issue History

The module keeps a history of all equipment issues and returns.

The history can be viewed as:

* List;
* Kanban.

Kanban records can be grouped by equipment, employee, status and other available fields.

### Days Issued

For equipment that is currently issued, the module shows the number of days since the issue date.

### Asset Issue Act

The module provides a printable PDF report:

**"Акт видачі ОЗ"**

The report contains information about the equipment and the employee who received it.

## Statuses

Equipment can have the following statuses:

* **Available**
* **Issued**
* **Maintenance**
* **Retired**

The normal workflow is:

```text
Available → Issued → Available
```

Maintenance and Retired are used when equipment is temporarily or permanently unavailable.

## Security

There are two user groups:

* **Asset User** — can view equipment and use Issue/Return.
* **Asset Manager** — can manage equipment, types and statuses.

The module also supports multiple companies.

## Installation

Copy the `asset_management` folder into an Odoo addons directory and install the module from Apps.

Or install it from the command line:

```bash
odoo-bin -c odoo.conf -d your_database -i asset_management
```

## Dependencies

The module uses standard Odoo modules:

* `base`
* `mail`
* `hr`

No additional Python packages are required.

## Documentation

More information is available in:

* `docs/user-guide.md` — how to use the module;
* `docs/architecture.md` — simple overview of the module structure;
* `docs/asset-statuses.md` — equipment statuses.
