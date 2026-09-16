# User Guide

## 1. Create an equipment type

**Asset Management > Configuration > Equipment Types > New**

Enter a name (e.g. "Laptop") and, optionally, a short code (e.g.
"LAPTOP") and description. Save.

## 2. Create an asset

**Asset Management > Assets > New**

Fill in:
* **Name** - e.g. "MacBook Pro 14".
* **Equipment Type** - pick the type created in step 1.
* **Serial Number** / **Inventory Number** - as applicable.
* **Description** - free text, optional.

Save. The new asset starts in status **Available**.

## 3. Issue the asset to an employee

Open the asset (status must be **Available**) and click **Issue** in the
header. In the wizard:
1. Select the **Employee**.
2. Confirm or change the **Issue Date** (defaults to today; cannot be in
   the future).
3. Add optional **Notes**.
4. Click **Confirm Issue**.

The asset's status becomes **Issued**, its **Current Employee** and
**Issue Date** are filled in, and a new record appears under **Issue
History**. The "Issue" button disappears - a "Return" button appears
instead.

## 4. Return the asset

Open the issued asset and click **Return** in the header (a confirmation
dialog is shown). The asset goes back to **Available**, its current
employee/issue date are cleared, and the corresponding issue-history
record is marked **Returned** with today's date.

The asset can now be issued again, to the same or a different employee.

## 5. Browse the issue history

**Asset Management > Issue History**

* **List view**: every issue/return event, with asset, employee, issue
  date, return date, duration (days) and status.
* Use the **Group By** menu to group by Asset, Employee, Status,
  Equipment Type or Company.
* Filters are available for **Currently Issued** / **Returned**, and to
  filter by issue date.

## 6. Kanban board

Switch to the **Kanban** view from Issue History to see each issue event
as a card (asset, type, employee, issue/return dates, duration, status).
Cards can be grouped the same way as the list view (e.g. group by Asset
to see every employee who has ever had a given laptop; group by Employee
to see everything currently or previously assigned to someone).

## 7. Print the Asset Issue Act

Open any record under **Issue History** (or an asset's **Issue History**
tab, then open a specific line) and use **Print > Asset Issue Act**. The
PDF includes the company name, employee (with job title/department when
available), asset details, issue/return dates, notes, and signature lines
for both the employee and the responsible person.

## 8. Filtering the asset list

**Asset Management > Assets**, using the search bar filters:
* **Available / Issued / Maintenance / Retired** - by status.
* **Issued < 7 Days** / **Issued > 30 Days** - based on how long the
  current issue has been active (compares the issue date to today, so
  it is always accurate).

## Who can do what

* **Asset User**: view assets and history; issue and return equipment.
  Cannot create/edit asset records or equipment types directly.
* **Asset Manager**: everything above, plus creating/editing assets,
  equipment types, and full access to the issue history.
