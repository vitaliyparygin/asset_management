# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from psycopg2 import IntegrityError

@tagged('post_install', '-at_install')
class TestAssetManagementIssue(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.asset_type = cls.env['asset.management.asset.type'].create({
            'name': 'Test Tool Type',
            'code': 'TEST-TOOL',
        })
        cls.employee_a = cls.env['hr.employee'].create({'name': 'Employee A'})
        cls.employee_b = cls.env['hr.employee'].create({'name': 'Employee B'})
        cls.asset = cls.env['asset.management.asset'].create({
            'name': 'Drill',
            'asset_type_id': cls.asset_type.id,
        })

    def _create_asset(self, name='Test Drill'):
        return self.env['asset.management.asset'].create({
            'name': name,
            'asset_type_id': self.asset_type.id,
        })

    def test_duration_days_active(self):
        issue = self.env['asset.management.issue'].create({
            'asset_id': self.asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': fields.Date.today() - timedelta(days=5),
            'state': 'issued',
        })
        self.assertEqual(issue.duration_days, 5)

    def test_duration_days_returned(self):
        issue = self.env['asset.management.issue'].create({
            'asset_id': self.asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': fields.Date.today() - timedelta(days=10),
            'return_date': fields.Date.today() - timedelta(days=2),
            'state': 'returned',
        })
        self.assertEqual(issue.duration_days, 8)

    def test_duration_days_future_issue_date(self):
        issue = self.env['asset.management.issue'].create({
            'asset_id': self.asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': fields.Date.today() + timedelta(days=1),
            'state': 'issued',
        })
        self.assertEqual(issue.duration_days, 0)

    def test_cannot_create_two_active_issues_orm(self):
        asset = self._create_asset('ORM Unique Drill')

        self.env['asset.management.issue'].create({
            'asset_id': asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': fields.Date.today(),
            'state': 'issued',
        })

        with self.assertRaises(ValidationError):
            self.env['asset.management.issue'].create({
                'asset_id': asset.id,
                'employee_id': self.employee_b.id,
                'issue_date': fields.Date.today(),
                'state': 'issued',
            })

    def test_partial_unique_index_exists(self):
        """The database-level guarantee must exist regardless of any ORM
        bypass (e.g. raw SQL, another codebase touching the same DB)."""
        self.env.cr.execute("""
            SELECT indexname FROM pg_indexes
            WHERE indexname = 'asset_management_issue_unique_active_idx'
        """)
        self.assertTrue(self.env.cr.fetchone(), 'Partial unique index was not created')

    def test_return_date_before_issue_date_rejected_by_database_constraint(self):
        with self.assertRaises(Exception):
            self.env['asset.management.issue'].create({
                'asset_id': self.asset.id,
                'employee_id': self.employee_a.id,
                'issue_date': fields.Date.today(),
                'return_date': fields.Date.today() - timedelta(days=1),
                'state': 'returned',
            })

    def test_active_issue_duration_uses_today_without_setting_return_date(self):
        issue_date = fields.Date.today() - timedelta(days=5)

        issue = self.env['asset.management.issue'].create({
            'asset_id': self.asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': issue_date,
            'company_id': self.env.company.id,
            'state': 'issued',
        })

        self.assertFalse(issue.return_date)
        self.assertEqual(issue.duration_days, 5)

    def test_returned_issue_duration_uses_return_date(self):
        issue_date = fields.Date.today() - timedelta(days=10)
        return_date = fields.Date.today() - timedelta(days=3)

        issue = self.env['asset.management.issue'].create({
            'asset_id': self.asset.id,
            'employee_id': self.employee_a.id,
            'issue_date': issue_date,
            'return_date': return_date,
            'company_id': self.env.company.id,
            'state': 'returned',
        })

        self.assertEqual(issue.duration_days, 7)
