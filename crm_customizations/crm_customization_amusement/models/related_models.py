from odoo import models,fields,api
from odoo.exceptions import ValidationError
import re

class City(models.Model):
    _name = 'city.city'
    _order = 'id desc'

    name = fields.Char(string="City Name", copy=False,tracking=True)

class LeadType(models.Model):
    _name = 'lead.type'
    _order = 'id desc'

    name = fields.Char(string="Lead Type", copy=False,tracking=True)


class SchoolType(models.Model):
    _name = 'school.type'
    _order = 'id desc'

    name = fields.Char(string="School Type", copy=False,tracking=True)


class StakeholderDesignation(models.Model):
    _name = 'stakeholder.designation'
    _order = 'id desc'

    name = fields.Char(copy=False,tracking=True)

    
class OtherStakeholder(models.Model):
    _name = 'other.stakeholder.line'
    _order = 'id desc'

    name = fields.Char(string="Name",tracking=True)
    crm_lead_id = fields.Many2one('crm.lead',tracking=True)
    mail = fields.Char("Mail", tracking=True)
    phone = fields.Char("Phone", tracking= True)
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
                
    @api.constrains('phone')
    def _onchange_stakeholder_phone_validation(self):
        for rec in self:
            if rec.phone:
                    try:
                        without_chars = int(rec.phone)
                        if len(str(without_chars)) != 10:
                            raise ValidationError("Please Enter 10 Digit Stakholder's Phone Number")
                            
                    except ValueError:
                        raise ValidationError("Please Enter Valid Stakholder's Phone Number")
                    
                

# class IncludedActivities(models.Model):
#     _name = 'included.activities'
#     _order = 'id desc'

#     name = fields.Char(string="Name", copy=False,tracking=True)

# class OngroundrRequirements(models.Model):
#     _name = 'onground.requirements'
#     _order = 'id desc'

#     name = fields.Char(string="Name", copy=False,tracking=True)

# class ResCompany(models.Model):
#     _inherit = 'res.company'

#     city_id = fields.Many2one('city.city', string="City" ,tracking=True)