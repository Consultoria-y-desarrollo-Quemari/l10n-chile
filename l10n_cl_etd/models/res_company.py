# Copyright (C) 2019 Konos
# Copyright (C) 2019 Blanco Martín & Asociados
# Copyright (C) 2019 CubicERP
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    dte_resolution_number = fields.Char(
            string='SII Exempt Resolution Number',
            help='''This value must be provided \
and must appear in your pdf or printed tribute document, under the electronic \
stamp to be legally valid.''',
            default='0',
    )
    dte_resolution_date = fields.Date(
            'SII Exempt Resolution Date',
    )

    @api.constrains('backend_acp_id')
    def _check_backend_acp_id(self):
        """
        Check the company backend to make sure it is not set to SII
        """
        sii = self.env.ref('l10n_cl_etd.backend_acp_sii')
        for record in self:
            if record.backend_acp_id.id == sii.id:
                raise ValidationError(_(
                    "%s does not sign documents. Please select another "
                    "provider." % sii.name))
