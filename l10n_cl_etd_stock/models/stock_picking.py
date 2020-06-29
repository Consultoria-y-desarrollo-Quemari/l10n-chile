# Copyright (C) 2019 Konos
# Copyright (C) 2019 Blanco Martín & Asociados
# Copyright (C) 2019 CubicERP
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models

try:
    from io import BytesIO
except:
    _logger.warning("no se ha cargado io")
try:
    import pdf417gen
except ImportError:
    _logger.warning('Cannot import pdf417gen library')


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'etd.mixin']

    def pdf417bc(self, ted, columns=13, ratio=3):
        bc = pdf417gen.encode(
            ted,
            security_level=5,
            columns=columns,
        )
        image = pdf417gen.render_image(
            bc,
            padding=15,
            scale=1,
            ratio=ratio,
        )
        return image

    @api.multi
    def get_barcode_img(self, columns=13, ratio=3):
        barcodefile = BytesIO()
        image = self.pdf417bc(self.sii_barcode, columns, ratio)
        image.save(barcodefile, 'PNG')
        data = barcodefile.getvalue()
        return base64.b64encode(data)

    def _get_barcode_img(self):
        for r in self:
            if r.sii_barcode:
                r.sii_barcode_img = r.get_barcode_img()

    sii_barcode = fields.Char(
            copy=False,
            string=_('SII Barcode'),
            help='SII Barcode Name',
            readonly=True,
            states={'draft': [('readonly', False)]},
        )
    sii_barcode_img = fields.Binary(
            string=_('SII Barcode Image'),
            help='SII Barcode Image in PDF417 format',
            compute="_get_barcode_img",
        )

    def _compute_class_id_domain(self):
        return [('document_type', '=', 'stock_picking')]

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for rec in self:
            if self.use_documents:
                sign = rec._name in [x.model for x in rec.company_id.etd_ids]
                if sign and rec.location_dest_id.usage == 'customer':
                    rec.with_delay().document_sign()
        return res

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            # if partner and partner.invoicing_policy == 'eguide':
            sii_obj = self.env['sii.document.class']
            sii_document = sii_obj.search(
                [('code', '=', 52),
                 ('document_type', '=', 'stock_picking')], limit=1)
            vals.update({'class_id': sii_document and sii_document.id})
        return super(StockPicking, self).create(vals)
