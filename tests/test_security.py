# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo import fields

@tagged('post_install', '-at_install')
class TestAssetManagementSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.asset_model = cls.env['asset.management.asset']
        cls.asset_type_model = cls.env['asset.management.asset.type']
        cls.issue_model = cls.env['asset.management.issue']

        cls.company_a = cls.env.company

        cls.company_b = cls.env['res.company'].create({
            'name': 'Asset Management Test Company B',
        })

        cls.asset_user_group = cls.env.ref(
            'asset_management.group_asset_user'
        )
        cls.asset_manager_group = cls.env.ref(
            'asset_management.group_asset_manager'
        )

        cls.asset_user = cls.env['res.users'].create({
            'name': 'Asset Test User',
            'login': 'asset_test_user',
            'email': 'asset_test_user@example.com',
            'groups_id': [
                (6, 0, [
                    cls.env.ref('base.group_user').id,
                    cls.asset_user_group.id,
                ]),
            ],
            'company_id': cls.company_a.id,
            'company_ids': [
                (6, 0, [cls.company_a.id]),
            ],
        })

        cls.asset_manager = cls.env['res.users'].create({
            'name': 'Asset Test Manager',
            'login': 'asset_test_manager',
            'email': 'asset_test_manager@example.com',
            'groups_id': [
                (6, 0, [
                    cls.env.ref('base.group_user').id,
                    cls.asset_manager_group.id,
                ]),
            ],
            'company_id': cls.company_a.id,
            'company_ids': [
                (6, 0, [cls.company_a.id, cls.company_b.id]),
            ],
        })

        cls.asset_type_a = cls.asset_type_model.create({
            'name': 'Security Test Laptop',
            'code': 'SEC-LAPTOP',
        })

        cls.asset_a = cls.asset_model.create({
            'name': 'Company A Laptop',
            'asset_type_id': cls.asset_type_a.id,
            'company_id': cls.company_a.id,
        })

        cls.asset_type_b = cls.asset_type_model.create({
            'name': 'Company B Laptop',
            'code': 'SEC-LAPTOP-B',
        })

        cls.asset_b = cls.asset_model.with_company(
            cls.company_b
        ).create({
            'name': 'Company B Laptop',
            'asset_type_id': cls.asset_type_b.id,
            'company_id': cls.company_b.id,
        })

    def test_admin_is_asset_manager_by_default(self):
        admin = self.env.ref('base.user_admin')

        self.assertTrue(
            admin.has_group('asset_management.group_asset_manager')
        )
        self.assertTrue(
            admin.has_group('asset_management.group_asset_user')
        )

    def test_asset_user_can_read_asset(self):
        asset = self.asset_a.with_user(self.asset_user)

        self.assertEqual(asset.name, 'Company A Laptop')

    def test_asset_user_cannot_create_asset(self):
        with self.assertRaises(AccessError):
            self.asset_model.with_user(self.asset_user).create({
                'name': 'User Created Laptop',
                'asset_type_id': self.asset_type_a.id,
                'company_id': self.company_a.id,
            })

    def test_asset_user_cannot_write_asset(self):
        with self.assertRaises(AccessError):
            self.asset_a.with_user(self.asset_user).write({
                'name': 'Modified by User',
            })

    def test_asset_user_cannot_unlink_asset(self):
        asset = self.env['asset.management.asset'].create({
            'name': 'Test Asset',
            'asset_type_id': self.asset_type_a.id,
        })

        with self.assertRaises(UserError):
            asset.with_user(self.asset_user).unlink()

        self.assertTrue(asset.exists())

    def test_asset_manager_can_create_asset(self):
        asset = self.asset_model.with_user(self.asset_manager).create({
            'name': 'Manager Created Laptop',
            'asset_type_id': self.asset_type_a.id,
            'company_id': self.company_a.id,
        })

        self.assertTrue(asset)
        self.assertEqual(asset.name, 'Manager Created Laptop')

    def test_asset_manager_can_write_asset(self):
        asset = self.asset_a.with_user(self.asset_manager)

        asset.write({
            'description': 'Updated by manager',
        })

        self.assertEqual(asset.description, 'Updated by manager')

    def test_asset_manager_cannot_unlink_asset(self):
        asset = self.env['asset.management.asset'].create({
            'name': 'Test Asset',
            'asset_type_id': self.asset_type_a.id,
        })

        with self.assertRaises(UserError):
            asset.with_user(self.asset_manager).unlink()

        self.assertTrue(asset.exists())

    def test_asset_user_cannot_create_equipment_type(self):
        with self.assertRaises(AccessError):
            self.asset_type_model.with_user(self.asset_user).create({
                'name': 'User Created Type',
                'code': 'USER-TYPE',
            })

    def test_asset_user_cannot_write_equipment_type(self):
        with self.assertRaises(AccessError):
            self.asset_type_a.with_user(self.asset_user).write({
                'description': 'User modification',
            })

    def test_asset_manager_can_create_equipment_type(self):
        asset_type = self.asset_type_model.with_user(
            self.asset_manager
        ).create({
            'name': 'Manager Created Type',
            'code': 'MANAGER-TYPE',
        })

        self.assertTrue(asset_type)

    def test_asset_manager_can_write_equipment_type(self):
        self.asset_type_a.with_user(self.asset_manager).write({
            'description': 'Manager modification',
        })

        self.assertEqual(
            self.asset_type_a.description,
            'Manager modification',
        )

    def test_asset_user_can_create_issue(self):
        employee = self.env['hr.employee'].create({
            'name': 'Security Test Employee',
            'company_id': self.company_a.id,
        })

        issue = self.issue_model.with_user(self.asset_user).create({
            'asset_id': self.asset_a.id,
            'employee_id': employee.id,
            'issue_date': fields.Date.context_today(self.env.user),
            'company_id': self.company_a.id,
            'state': 'returned',
            'return_date': fields.Date.context_today(self.env.user),
        })

        self.assertTrue(issue)

    def test_user_cannot_see_other_company_asset(self):
        assets = self.asset_model.with_user(
            self.asset_user
        ).search([])

        self.assertIn(self.asset_a, assets)
        self.assertNotIn(self.asset_b, assets)

    def test_user_cannot_read_other_company_asset_directly(self):
        with self.assertRaises(AccessError):
            self.asset_b.with_user(self.asset_user).read(['name'])

    def test_user_cannot_see_other_company_issue(self):
        employee_a = self.env['hr.employee'].create({
            'name': 'Company A Issue Employee',
            'company_id': self.company_a.id,
        })

        employee_b = self.env['hr.employee'].with_company(
            self.company_b
        ).create({
            'name': 'Company B Issue Employee',
            'company_id': self.company_b.id,
        })

        issue_a = self.issue_model.create({
            'asset_id': self.asset_a.id,
            'employee_id': employee_a.id,
            'issue_date': fields.Date.context_today(self.env.user),
            'company_id': self.company_a.id,
            'state': 'returned',
            'return_date': fields.Date.context_today(self.env.user),
        })

        issue_b = self.issue_model.with_company(
            self.company_b
        ).create({
            'asset_id': self.asset_b.id,
            'employee_id': employee_b.id,
            'issue_date': fields.Date.context_today(self.env.user),
            'company_id': self.company_b.id,
            'state': 'returned',
            'return_date': fields.Date.context_today(self.env.user),
        })

        issues = self.issue_model.with_user(self.asset_user).search([])

        self.assertIn(issue_a, issues)
        self.assertNotIn(issue_b, issues)

    def test_manager_can_see_assets_from_all_allowed_companies(self):
        assets = self.asset_model.with_user(
            self.asset_manager
        ).search([])

        self.assertIn(self.asset_a, assets)
        self.assertIn(self.asset_b, assets)

    def test_manager_can_switch_current_company(self):
        manager_company_b = self.asset_manager.with_company(
            self.company_b
        )

        self.assertEqual(
            manager_company_b.env.company,
            self.company_b,
        )

        assets = self.asset_model.with_user(
            manager_company_b
        ).search([])

        self.assertIn(self.asset_a, assets)
        self.assertIn(self.asset_b, assets)

    def test_manager_can_switch_current_company(self):
        manager_company_b = self.asset_manager.with_company(
            self.company_b
        )

        self.assertEqual(
            manager_company_b.env.company,
            self.company_b,
        )

        assets = self.asset_model.with_user(
            manager_company_b
        ).search([])

        self.assertIn(self.asset_a, assets)
        self.assertIn(self.asset_b, assets)

    def test_asset_user_is_limited_to_allowed_company(self):
        assets = self.asset_model.with_user(
            self.asset_user
        ).search([])

        self.assertIn(self.asset_a, assets)
        self.assertNotIn(self.asset_b, assets)