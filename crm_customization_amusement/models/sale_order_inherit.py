from odoo import models,fields,api
from odoo.exceptions import ValidationError
import re

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sale', "Deal Confirmed"),
    ('cancel', "Cancelled"),
]


class SaleOrderInherit(models.Model):
    _inherit='sale.order'
    
    quotation_valuation_amount = fields.Float(tracking=True,compute='_compute_quotation_valuation_amount' ,string="Deal Value")
    
    
    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    @api.depends('order_line.price_subtotal', 'order_line.is_primary_valuation_product')
    def _compute_quotation_valuation_amount(self):
        for record in self:
            total = 0.0
            for line in record.order_line:
                if line.is_primary_valuation_product:
                    total += line.price_subtotal
            record.quotation_valuation_amount = total
            
    @api.model
    def create(self, vals):
        order = super().create(vals)
        order._update_lead_stage_on_sale()
        return order

    def write(self, vals):
        res = super().write(vals)
        self._update_lead_stage_on_sale()
        return res

    def _update_lead_stage_on_sale(self):
        for order in self:
            if order.state == 'sale' and order.opportunity_id:
                lead = order.opportunity_id
                stage_3 = self.env['crm.stage'].search([('id', '=', 3)], limit=1)
                if stage_3 and lead.stage_id.id != 3:
                    lead.stage_id = stage_3.id
# @api.depends('order_line.price_subtotal', 'order_line.is_primary_valuation_product')
#     def _compute_quotation_valuation_amount(self):
#         for record in self:
#             total = 0.0
#             for line in record.order_line:                    
#                 if line.is_primary_valuation_product:
#                     total += line.price_subtotal
#             record.quotation_valuation_amount = total


class SaleOrderLineInherit(models.Model):
    _inherit='sale.order.line'
    
    
    is_primary_valuation_product = fields.Boolean('Is Primary',tracking=True)
