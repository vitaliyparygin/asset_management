# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestAssetManagementReport(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        asset_type = cls.env['asset.management.asset.type'].create({
            'name': 'Test Report Laptop Type',
            'code': 'TEST-REPORT-LAPTOP',
        })
        employee = cls.env['hr.employee'].create({'name': 'Employee A'})
        asset = cls.env['asset.management.asset'].create({
            'name': 'MacBook Pro 14',
            'asset_type_id': asset_type.id,
            'serial_number': 'SN-REPORT-1',
        })
        cls.issue = cls.env['asset.management.issue'].create({
            'asset_id': asset.id,
            'employee_id': employee.id,
            'issue_date': fields.Date.today(),
            'state': 'issued',
        })

    def test_report_action_registered(self):
        report = self.env.ref('asset_management.action_report_asset_issue_act')
        self.assertEqual(report.model, 'asset.management.issue')
        self.assertEqual(report.report_type, 'qweb-pdf')

    def test_report_renders_html(self):
        # Rendering the QWeb template to HTML is enough to prove the
        # template is well-formed and all referenced fields resolve,
        # without requiring a wkhtmltopdf binary in the test environment.
        html = self.env['ir.actions.report']._render_qweb_html(
            'asset_management.report_asset_issue_act_document', self.issue.ids,
        )[0]
        self.assertIn(b'Asset Issue Act', html)
