# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AssetManagementIssueWizard(models.TransientModel):
    """Standard Odoo transient-model wizard used by the "Issue" button on
    the asset form. Kept intentionally thin: all persistent state changes
    happen on confirm, inside a single DB transaction.
    """

    _name = 'asset.management.issue.wizard'
    _description = 'Issue Asset Wizard'

    asset_id = fields.Many2one(
        'asset.management.asset', required=True, readonly=True,
    )
    company_id = fields.Many2one(related='asset_id.company_id', readonly=True)
    asset_state = fields.Selection(related='asset_id.state', readonly=True)
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        check_company=True,
    )
    issue_date = fields.Date(required=True, default=fields.Date.context_today)
    notes = fields.Text()

    @api.constrains('issue_date')
    def _check_issue_date(self):
        for wizard in self:
            if wizard.issue_date and wizard.issue_date > fields.Date.context_today(wizard):
                raise UserError(_('The issue date cannot be in the future.'))

    def action_confirm(self):
        self.ensure_one()
        asset = self.asset_id

        self.env.cr.execute(
            'SELECT id, state FROM asset_management_asset WHERE id = %s FOR UPDATE',
            (asset.id,),
        )
        row = self.env.cr.fetchone()
        if not row or row[1] != 'available':
            raise UserError(_(
                'This asset is no longer available - it may have just been '
                'issued by someone else. Please refresh and try again.',
            ))

        issue_vals = {
            'asset_id': asset.id,
            'employee_id': self.employee_id.id,
            'issue_date': self.issue_date,
            'company_id': asset.company_id.id,
            'notes': self.notes,
            'state': 'issued',
        }

        self.env['asset.management.issue'].sudo().create(issue_vals)
        asset.sudo().write({
            'employee_id': self.employee_id.id,
            'issue_date': self.issue_date,
            'state': 'issued',
        })
        return {'type': 'ir.actions.act_window_close'}
