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

        # Lock the asset row for the rest of this transaction so that two
        # concurrent "Issue" requests for the same asset are serialized:
        # the second request blocks here until the first one commits (or
        # rolls back), after which it re-reads a fresh, up-to-date state.
        # This is the standard PostgreSQL/Odoo pattern for this kind of
        # race condition; it complements (and does not replace) the
        # partial unique index on asset.management.issue.
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
        # See asset.action_return() for why sudo() is used here: Asset
        # Users only get read access to asset.management.asset directly,
        # and create/write access to asset.management.issue is limited to
        # what this sanctioned wizard needs.
        self.env['asset.management.issue'].sudo().create(issue_vals)
        asset.sudo().write({
            'employee_id': self.employee_id.id,
            'issue_date': self.issue_date,
            'state': 'issued',
        })
        return {'type': 'ir.actions.act_window_close'}
