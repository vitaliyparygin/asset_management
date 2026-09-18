# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class AssetManagementAsset(models.Model):
    """A single physical piece of company equipment.

    This model is deliberately kept separate from the issue history
    (``asset.management.issue``): the asset record is the *catalog card*
    of a physical item, while the issue model records the *facts* of it
    being handed out to and returned from employees over time.
    """

    _name = 'asset.management.asset'
    _description = 'Company Asset / Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    asset_type_id = fields.Many2one(
        'asset.management.asset.type',
        string='Equipment Type',
        required=True,
        tracking=True,
        ondelete='restrict',
    )
    serial_number = fields.Char(tracking=True)
    inventory_number = fields.Char(tracking=True)
    description = fields.Text()
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    active = fields.Boolean(default=True)

    state = fields.Selection(
        [
            ('available', 'Available'),
            ('issued', 'Issued'),
            ('maintenance', 'Maintenance'),
            ('retired', 'Retired'),
        ],
        string='Status',
        default='available',
        required=True,
        copy=False,
        tracking=True,
    )

    # Current holder. This field is intentionally readonly on the form:
    # it must only ever be changed by action_issue()/action_return() (or
    # the issue wizard), never by direct user edition, so the asset state
    # and the issue history can never drift apart. See docs/architecture.md.
    employee_id = fields.Many2one(
        'hr.employee',
        string='Current Employee',
        copy=False,
        readonly=True,
        tracking=True,
        check_company=True,
        index=True,
    )
    issue_date = fields.Date(
        string='Current Issue Date',
        copy=False,
        readonly=True,
        tracking=True,
    )
    days_issued = fields.Integer(
        string='Days Issued',
        compute='_compute_days_issued',
        store=True,
        help='Number of days since the current issue date. '
             'Zero when the asset is not currently issued.',
    )

    issue_history_ids = fields.One2many(
        'asset.management.issue', 'asset_id', string='Issue History',
    )
    issue_history_count = fields.Integer(compute='_compute_issue_history_count')

    _sql_constraints = [
        (
            'issue_consistency_check',
            "CHECK ("
            "  (state = 'issued' AND employee_id IS NOT NULL AND issue_date IS NOT NULL)"
            "  OR (state != 'issued' AND employee_id IS NULL AND issue_date IS NULL)"
            ")",
            'An asset can only have a current employee and issue date while its '
            'status is "Issued".',
        ),
    ]

    def unlink(self):
        raise UserError(
            'Assets cannot be deleted. Archive the asset instead.'
        )


    @api.depends('issue_date', 'state')
    def _compute_days_issued(self):
        today = fields.Date.context_today(self)

        for asset in self:
            if asset.state != 'issued' or not asset.issue_date:
                asset.days_issued = 0
                continue

            asset.days_issued = max(
                (today - asset.issue_date).days,
                0,
            )

    def _compute_issue_history_count(self):
        counts = self.env['asset.management.issue']._read_group(
            [('asset_id', 'in', self.ids)], ['asset_id'], ['__count'],
        )
        mapped = {asset.id: count for asset, count in counts}
        for asset in self:
            asset.issue_history_count = mapped.get(asset.id, 0)

    @api.constrains('state', 'employee_id', 'issue_date')
    def _check_state_employee_consistency(self):
        """Belt-and-braces Python check mirroring the SQL CHECK constraint,
        so a clear, translated ValidationError is raised instead of a raw
        PostgreSQL IntegrityError.
        """
        for asset in self:
            if asset.state == 'issued':
                if not asset.employee_id or not asset.issue_date:
                    raise ValidationError(_(
                        'Asset "%s" is marked as Issued but has no employee or '
                        'issue date. Use the "Issue" button instead of editing '
                        'these fields directly.', asset.name,
                    ))
            else:
                if asset.employee_id or asset.issue_date:
                    raise ValidationError(_(
                        'Asset "%s" has a current employee/issue date but its '
                        'status is not "Issued". Use the "Return" button instead '
                        'of editing these fields directly.', asset.name,
                    ))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_issue(self):
        """Open the issue wizard for a single available asset."""
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_(
                'Only assets in "Available" status can be issued. '
                '"%s" is currently "%s".', self.name, dict(
                    self._fields['state'].selection).get(self.state),
            ))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Issue Asset'),
            'res_model': 'asset.management.issue.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
            },
        }

    def action_return(self):
        """Return one or more issued assets to stock."""
        issue_model = self.env['asset.management.issue']
        for asset in self:
            if asset.state != 'issued':
                raise UserError(_(
                    'Only assets in "Issued" status can be returned. '
                    '"%s" is currently "%s".', asset.name, dict(
                        asset._fields['state'].selection).get(asset.state),
                ))
            active_issue = issue_model.search(
                [('asset_id', '=', asset.id), ('state', '=', 'issued')],
                limit=1,
            )
            if not active_issue:
                # Should not normally happen given the CHECK constraint above,
                # but guard against manual data corruption.
                raise UserError(_(
                    'No active issue record was found for asset "%s". '
                    'Please contact your administrator.', asset.name,
                ))
            # Controlled write: Asset Users only have read access on this
            # model (see security/ir.model.access.csv); sudo() lets the
            # sanctioned workflow method perform the state transition on
            # their behalf while keeping direct edition locked down.
            active_issue.sudo().write({
                'return_date': fields.Date.context_today(asset),
                'state': 'returned',
            })

            asset.sudo().write({
                'employee_id': False,
                'issue_date': False,
                'state': 'available',
            })

            self.env.flush_all()

    def _cron_refresh_date_dependent_fields(self):
        """
        Refresh stored computed fields that depend on the current date.
        """
        assets = self.search([('state', '=', 'issued')])
        assets._compute_days_issued()

        issues = self.env['asset.management.issue'].search([
            ('state', '=', 'issued'),
        ])
        issues._compute_duration_days()

        self.env.flush_all()

    def action_view_issue_history(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'asset_management.action_asset_management_issue')
        action['domain'] = [('asset_id', '=', self.id)]
        action['context'] = {'default_asset_id': self.id}
        return action
