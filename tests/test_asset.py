# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError

@tagged('post_install', '-at_install')
class TestAssetManagementAsset(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.asset_type = cls.env['asset.management.asset.type'].create({
            'name': 'Test Laptop Type',
            'code': 'TEST-LAPTOP',
        })
        cls.employee_a = cls.env['hr.employee'].create({
            'name': 'Asset Test Employee A',
        })
        cls.employee_b = cls.env['hr.employee'].create({
            'name': 'Asset Test Employee B',
        })

    def _create_asset(self, **kwargs):
        vals = {
            'name': 'Test Laptop',
            'asset_type_id': self.asset_type.id,
            'serial_number': 'SN-0001',
            'inventory_number': 'INV-0001',
        }
        vals.update(kwargs)
        return self.env['asset.management.asset'].create(vals)

    def _issue(self, asset, employee, issue_date=None):
        """Helper that goes through the wizard, like a real user would."""
        wizard = self.env['asset.management.issue.wizard'].create({
            'asset_id': asset.id,
            'employee_id': employee.id,
            'issue_date': issue_date or fields.Date.today(),
        })
        wizard.action_confirm()

    def _create_asset_type(self, **kwargs):
        values = {
            'name': 'Test Equipment Type',
        }
        values.update(kwargs)
        return self.env['asset.management.asset.type'].create(values)

    # -- Creation -----------------------------------------------------
    def test_create_asset_type(self):
        self.assertEqual(self.asset_type.name, 'Test Laptop Type')
        self.assertEqual(self.asset_type.code, 'TEST-LAPTOP')
        self.assertTrue(self.asset_type.active)

    def test_create_asset_defaults(self):
        asset = self._create_asset()
        self.assertEqual(asset.serial_number, 'SN-0001')
        self.assertEqual(asset.inventory_number, 'INV-0001')
        self.assertEqual(asset.state, 'available')
        self.assertEqual(asset.company_id, self.env.company)
        self.assertFalse(asset.employee_id)

    # -- Issue ----------------------------------------------------------
    def test_issue_asset(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a)

        self.assertEqual(asset.state, 'issued')
        self.assertEqual(asset.employee_id, self.employee_a)
        self.assertTrue(asset.issue_date)

        history = asset.issue_history_ids
        self.assertEqual(len(history), 1)
        self.assertEqual(history.employee_id, self.employee_a)
        self.assertEqual(history.state, 'issued')

    def test_cannot_issue_twice(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a)

        with self.assertRaises(UserError):
            asset.action_issue()

        wizard = self.env['asset.management.issue.wizard'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_b.id,
            'issue_date': fields.Date.today(),
        })
        with self.assertRaises(UserError):
            wizard.action_confirm()

        # Employee A must still be the current holder.
        self.assertEqual(asset.employee_id, self.employee_a)
        self.assertEqual(len(asset.issue_history_ids), 1)

    # -- Return -----------------------------------------------------
    def test_return_asset(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a)
        asset.action_return()

        self.assertEqual(asset.state, 'available')
        self.assertFalse(asset.employee_id)
        self.assertFalse(asset.issue_date)

        history = asset.issue_history_ids
        self.assertEqual(history.state, 'returned')
        self.assertTrue(history.return_date)

    def test_reissue_after_return(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a)
        asset.action_return()
        self._issue(asset, self.employee_b)

        self.assertEqual(asset.state, 'issued')
        self.assertEqual(asset.employee_id, self.employee_b)
        self.assertEqual(len(asset.issue_history_ids), 2)

    def test_cannot_return_available_asset(self):
        asset = self._create_asset()
        with self.assertRaises(UserError):
            asset.action_return()

    # -- days_issued ------------------------------------------------
    def test_days_issued_active(self):
        asset = self._create_asset()
        issue_date = fields.Date.today() - timedelta(days=13)
        self._issue(asset, self.employee_a, issue_date=issue_date)
        self.assertEqual(asset.days_issued, 13)

    def test_days_issued_today(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a, issue_date=fields.Date.today())
        self.assertEqual(asset.days_issued, 0)

    def test_days_issued_not_issued(self):
        asset = self._create_asset()
        self.assertEqual(asset.days_issued, 0)

    # -- Direct-edit guard (consistency constraint) ------------------
    def test_direct_edit_employee_without_state_raises(self):
        asset = self._create_asset()
        with self.assertRaises(ValidationError):
            asset.write({'employee_id': self.employee_a.id, 'issue_date': fields.Date.today()})

    def test_asset_type_name_must_be_unique(self):
        self._create_asset_type(
            name='Unique Name Test',
            code='UNIQ-NAME-A',
        )

        with self.assertRaises(IntegrityError):
            self._create_asset_type(
                name='Unique Name Test',
                code='UNIQ-NAME-B',
            )

    def test_asset_type_code_must_be_unique(self):
        self._create_asset_type(
            name='Unique Code Test A',
            code='UNIQ-CODE-TEST',
        )

        with self.assertRaises(IntegrityError):
            self._create_asset_type(
                name='Unique Code Test B',
                code='UNIQ-CODE-TEST',
            )

    def test_asset_type_asset_count(self):
        asset_1 = self._create_asset(name='Laptop 1')
        asset_2 = self._create_asset(name='Laptop 2')

        self.asset_type.invalidate_recordset(['asset_count'])
        self.assertEqual(self.asset_type.asset_count, 2)

        asset_1.write({'active': False})

        self.asset_type.invalidate_recordset(['asset_count'])
        self.assertEqual(self.asset_type.asset_count, 2)

        asset_2.unlink()

        self.asset_type.invalidate_recordset(['asset_count'])
        self.assertEqual(self.asset_type.asset_count, 1)

    def test_asset_type_archive(self):
        self.assertTrue(self.asset_type.active)

        self.asset_type.write({'active': False})

        self.assertFalse(self.asset_type.active)

        self.asset_type.write({'active': True})

        self.assertTrue(self.asset_type.active)

    def test_issue_action_opens_wizard(self):
        asset = self._create_asset()

        action = asset.action_issue()

        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(
            action['res_model'],
            'asset.management.issue.wizard',
        )
        self.assertEqual(action['view_mode'], 'form')
        self.assertEqual(action['target'], 'new')
        self.assertEqual(action['context']['default_asset_id'], asset.id)

    def test_issue_history_count(self):
        asset = self._create_asset()

        self.assertEqual(asset.issue_history_count, 0)

        self._issue(asset, self.employee_a)

        asset.invalidate_recordset(['issue_history_count'])
        self.assertEqual(asset.issue_history_count, 1)

        asset.action_return()

        asset.invalidate_recordset(['issue_history_count'])
        self.assertEqual(asset.issue_history_count, 1)

        self._issue(asset, self.employee_b)

        asset.invalidate_recordset(['issue_history_count'])
        self.assertEqual(asset.issue_history_count, 2)

    def test_issue_history_contains_expected_data(self):
        asset = self._create_asset()

        issue_date = fields.Date.today() - timedelta(days=7)

        self._issue(
            asset,
            self.employee_a,
            issue_date=issue_date,
        )

        issue = self.env['asset.management.issue'].search(
            [('asset_id', '=', asset.id)],
            limit=1,
        )

        self.assertEqual(issue.asset_id, asset)
        self.assertEqual(issue.asset_type_id, self.asset_type)
        self.assertEqual(issue.employee_id, self.employee_a)
        self.assertEqual(issue.issue_date, issue_date)
        self.assertEqual(issue.state, 'issued')
        self.assertFalse(issue.return_date)
        self.assertEqual(issue.duration_days, 7)

    def test_return_updates_history(self):
        asset = self._create_asset()

        self._issue(asset, self.employee_a)

        issue = asset.issue_history_ids.filtered(
            lambda record: record.state == 'issued'
        )

        self.assertEqual(len(issue), 1)

        asset.action_return()

        self.assertEqual(issue.state, 'returned')
        self.assertTrue(issue.return_date)
        self.assertGreaterEqual(issue.duration_days, 0)

    def test_view_issue_history_action(self):
        asset = self._create_asset()

        action = asset.action_view_issue_history()

        self.assertEqual(
            action['res_model'],
            'asset.management.issue',
        )
        self.assertEqual(
            action['domain'],
            [('asset_id', '=', asset.id)],
        )
        self.assertEqual(
            action['context']['default_asset_id'],
            asset.id,
        )

    def test_wizard_rejects_future_issue_date(self):
        asset = self._create_asset()

        with self.assertRaises(UserError):
            self.env['asset.management.issue.wizard'].create({
                'asset_id': asset.id,
                'employee_id': self.employee_a.id,
                'issue_date': fields.Date.today() + timedelta(days=1),
            })

    def test_wizard_rejects_asset_that_became_issued(self):
        asset = self._create_asset()

        wizard = self.env['asset.management.issue.wizard'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': fields.Date.today(),
        })

        self._issue(asset, self.employee_b)

        with self.assertRaises(UserError):
            wizard.action_confirm()

        self.assertEqual(asset.employee_id, self.employee_b)
        self.assertEqual(
            asset.issue_history_ids.filtered(
                lambda issue: issue.state == 'issued'
            ).employee_id,
            self.employee_b,
        )

    def test_cannot_issue_maintenance_asset(self):
        asset = self._create_asset()
        asset.state = 'maintenance'

        with self.assertRaises(UserError):
            asset.action_issue()

    def test_cannot_issue_retired_asset(self):
        asset = self._create_asset()
        asset.state = 'retired'

        with self.assertRaises(UserError):
            asset.action_issue()

    def test_cron_refreshes_date_dependent_values(self):
        asset = self._create_asset()

        issue_date = fields.Date.today() - timedelta(days=10)

        self._issue(
            asset,
            self.employee_a,
            issue_date=issue_date,
        )

        issue = asset.issue_history_ids.filtered(
            lambda record: record.state == 'issued'
        )

        asset._cron_refresh_date_dependent_fields()

        self.assertEqual(asset.days_issued, 10)
        self.assertEqual(issue.duration_days, 10)

    def test_cannot_change_issued_asset_to_maintenance_without_return(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a)

        with self.assertRaises(ValidationError):
            asset.write({'state': 'maintenance'})

        self.assertEqual(asset.state, 'issued')
        self.assertEqual(asset.employee_id, self.employee_a)

    def test_can_change_available_asset_to_maintenance(self):
        asset = self._create_asset()

        asset.write({'state': 'maintenance'})

        self.assertEqual(asset.state, 'maintenance')

    def test_can_return_maintenance_asset_to_available(self):
        asset = self._create_asset(
            state='maintenance',
        )

        asset.write({'state': 'available'})

        self.assertEqual(asset.state, 'available')

    def test_cannot_change_issued_asset_to_retired_without_return(self):
        asset = self._create_asset()
        self._issue(asset, self.employee_a)

        with self.assertRaises(ValidationError):
            asset.write({'state': 'retired'})

        self.assertEqual(asset.state, 'issued')
        self.assertEqual(asset.employee_id, self.employee_a)