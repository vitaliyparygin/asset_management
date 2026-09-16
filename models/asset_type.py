# -*- coding: utf-8 -*-
from odoo import fields, models


class AssetManagementAssetType(models.Model):
    """Reference list of equipment types (Laptop, Monitor, Phone, Tool, ...).

    Kept as a lightweight, extensible ``Many2one`` target instead of a
    hardcoded ``Selection`` on the asset itself, so that new equipment
    categories can be added by an Asset Manager without touching code.
    """

    _name = 'asset.management.asset.type'
    _description = 'Equipment Type'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        index=True,
    )
    code = fields.Char(
        help='Short internal code, e.g. LAPTOP, PHONE, TOOL.',
    )
    description = fields.Text()
    active = fields.Boolean(default=True)
    asset_count = fields.Integer(compute='_compute_asset_count')

    _sql_constraints = [
        (
            'name_uniq',
            'unique(name)',
            'An equipment type with this name already exists.',
        ),
        (
            'code_uniq',
            'unique(code)',
            'An equipment type with this code already exists.',
        ),
    ]

    def _compute_asset_count(self):
        counts = self.env['asset.management.asset'].with_context(active_test=False)._read_group(
            [('asset_type_id', 'in', self.ids)],
            ['asset_type_id'],
            ['__count'],
        )
        mapped = {asset_type.id: count for asset_type, count in counts}
        for asset_type in self:
            asset_type.asset_count = mapped.get(asset_type.id, 0)
