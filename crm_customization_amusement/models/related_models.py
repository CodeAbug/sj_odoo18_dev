from odoo import models,fields,api
from odoo.exceptions import ValidationError
import re
from datetime import date,timedelta

class City(models.Model):
    _name = 'city.city'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _order = 'id desc'

    name = fields.Char(string="City Name", copy=False,tracking=True)

    center_manager_name = fields.Char(tracking=True)
    
    manager_phone_number = fields.Char('Manager Phone Number',tracking=True)
    
    center_phone = fields.Char(tracking=True)

    manager_email = fields.Char(tracking=True)
    
    address_line_1 = fields.Char('Center Address Line 1',tracking=True)
    address_line_2 = fields.Char('Center Address Line 2',tracking=True)
    city = fields.Char(tracking=True)
    state_id = fields.Many2one('res.country.state',tracking=True)
    country_id = fields.Many2one(
            'res.country',
            string='Country',
            default=lambda self: self.env.ref('base.in', raise_if_not_found=False)
        ) 
    
    center_code = fields.Char(string="Center Code", tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    capacity = fields.Integer(string="Center Capacity", tracking=True)
    notes = fields.Text(string="Additional Notes", tracking=True)
    
    
class LeadType(models.Model):
    _name = 'lead.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="Lead Type", copy=False,tracking=True)


class CrmLeadSource(models.Model):
    _name = 'crm.lead.source'
    _description = 'Lead Source'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Source Name", required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)

class SchoolType(models.Model):
    _name = 'school.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="School Type", copy=False,tracking=True)


class StakeholderDesignation(models.Model):
    _name = 'stakeholder.designation'
    _inherit = ['mail.thread', 'mail.activity.mixin']    
    _order = 'id desc'
    
    name = fields.Char(copy=False,tracking=True)

    
class OtherStakeholder(models.Model):
    _name = 'other.stakeholder.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']    
    _order = 'id desc'

    name = fields.Char(string="Name",tracking=True)
    crm_lead_id = fields.Many2one('crm.lead',tracking=True)
    mail = fields.Char("Mail", tracking=True)
    mobile = fields.Char("Mobile", tracking= True)
    designation_id = fields.Many2one('stakeholder.designation', string="Designation",tracking=True)
    is_primary_bool = fields.Boolean("Is Primary Person",tracking=True)
    partner_id = fields.Many2one('res.partner',tracking=True)

    @api.constrains('mail')
    def validate_email_fields(self):
        for rec in self:
            if rec.mail:
                valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.mail )
                if not valid:
                    raise ValidationError("Please Enter a Valid Stakeholder's Email Handle.")
                
    @api.constrains('mobile')
    def _onchange_stakeholder_mobile_validation(self):
        for rec in self:
            if rec.mobile:
                    try:
                        without_chars = int(rec.mobile)
                        if len(str(without_chars)) != 10:
                            raise ValidationError("Please Enter 10 Digit Stakholder's Mobile Number")
                            
                    except ValueError:
                        raise ValidationError("Please Enter Valid Stakholder's Mobile Number")
                    
                

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    city_center_id = fields.Many2one('city.city', string="Center" ,tracking=True)
    
    
class ResUserInherit(models.Model):
    _inherit = 'res.users'

    city_center_ids = fields.Many2many('city.city', string="Center")
    

class MailActivitySchedule(models.TransientModel):
    _inherit = 'mail.activity.schedule'

    # @api.onchange('date_dead')
    @api.onchange('date_deadline')
    def _check_date_deadline_not_too_old(self):
        for record in self:
            if record.date_deadline:
                min_allowed_date = date.today() - timedelta(days=2)
                if record.date_deadline < min_allowed_date:
                    raise ValidationError("You cannot set the deadline more than 2 days in the past.")

    
        
    
