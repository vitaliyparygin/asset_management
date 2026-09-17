# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError

class AssetManagementIssue(models.Model):
    """One record of a physical asset being handed out to (and, later,
    returned by) an employee.

    Business rule (see docs/architecture.md for full discussion): for a
    given ``asset_id`` there can be at most one record with
    ``state = 'issued'`` at any time. This is enforced twice:

    * ``_check_unique_active_issue`` - an ORM constraint giving a clear,
      translated error in the normal UI/RPC flow.
    * A PostgreSQL **partial unique index** created in ``init()`` - the
      authoritative, race-condition-proof guarantee at the database level,
      since ``_sql_constraints`` cannot express a partial (``WHERE``)
      unique constraint.
    """

    _name = 'asset.management.issue'
    _description = 'Asset Issue History'
    _order = 'issue_date desc, id desc'

    asset_id = fields.Many2one(
        'asset.management.asset',
        string='Asset',
        required=True,
        ondelete='cascade',
        index=True,
    )
    asset_type_id = fields.Many2one(
        related='asset_id.asset_type_id',
        string='Equipment Type',
        store=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        check_company=True,
        index=True,
    )
    issue_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
    )
    return_date = fields.Date()
    state = fields.Selection(
        [
            ('issued', 'Issued'),
            ('returned', 'Returned'),
        ],
        default='issued',
        required=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    notes = fields.Text()
    duration_days = fields.Integer(
        string='Duration (days)',
        compute='_compute_duration_days',
        store=True,
        help='Days between issue date and return date (or today, while still issued).',
    )

    _sql_constraints = [
        (
            'return_date_after_issue_date',
            'CHECK (return_date IS NULL OR return_date >= issue_date)',
            'The return date cannot be earlier than the issue date.',
        ),
        (
            'state_return_date_consistency',
            "CHECK (NOT (state = 'issued' AND return_date IS NOT NULL))",
            'A record still marked as "Issued" cannot have a return date.',
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        try:
            with self.env.cr.savepoint():
                return super().create(vals_list)
        except IntegrityError as exc:
            if (
                    getattr(exc, 'diag', None)
                    and exc.diag.constraint_name
                    == 'asset_management_issue_unique_active_idx'
            ):
                raise ValidationError(_(
                    'This asset already has an active issue record. '
                    'It must be returned before it can be issued again.'
                )) from exc
            raise

    @api.depends('issue_date', 'return_date', 'state')
    def _compute_duration_days(self):
        today = fields.Date.context_today(self)

        for issue in self:
            if not issue.issue_date:
                issue.duration_days = 0
                continue

            end_date = issue.return_date or today

            issue.duration_days = max(
                (end_date - issue.issue_date).days,
                0,
            )

    @api.constrains('asset_id', 'state')
    def _check_unique_active_issue(self):
        for issue in self:
            if issue.state != 'issued':
                continue

            count = self.search_count([
                ('asset_id', '=', issue.asset_id.id),
                ('state', '=', 'issued'),
                ('id', '!=', issue.id),
            ])

            if count:
                raise ValidationError(
                    _('This asset is already issued to an employee.')
                )


    def init(self):
        """Create a partial unique index guaranteeing, at the database
        level, that a given asset can never have two concurrently active
        (``state = 'issued'``) issue records - even under concurrent
        requests that would race past the Python-level constraint above.
        """
        self.env.cr.execute("""
            SELECT indexname FROM pg_indexes
            WHERE indexname = 'asset_management_issue_unique_active_idx'
        """)
        if not self.env.cr.fetchone():
            self.env.cr.execute("""
                CREATE UNIQUE INDEX asset_management_issue_unique_active_idx
                ON asset_management_issue (asset_id)
                WHERE state = 'issued'
            """)
