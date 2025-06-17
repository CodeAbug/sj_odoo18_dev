from odoo import models,fields,api
from odoo.exceptions import ValidationError
import re


class ResPartnerInherit(models.Model):
    _inherit='res.partner'
    
    is_primary_stakeholder_bool = fields.Boolean('Primary Stakeholder',tracking=True)
    
class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'
    
    
    
    lead_type_id = fields.Many2one('lead.type' , string="Lead Type" ,tracking=True)
    
    school_type_id = fields.Many2one('school.type', string="School Type" ,tracking=True)
    
    visiting_center_id = fields.Many2one('city.city',tracking=True,string="Visiting Center")
    
    lead_source = fields.Selection([
                            ('whats_app', "What's App"),
                            ('website', 'Website'),
                            ('walkin', 'Walk-in'),
                            ('ivr', 'IVR')],
                            string="Lead Source",tracking=True)
    
    visit = fields.Selection(
        [
            ('yes', 'Yes'),
            ('no', 'No')
        ]
        , tracking=True
    )
    visiting_person = fields.Char(tracking=True)
    other_stakeholders_ids = fields.One2many("other.stakeholder.line",'crm_lead_id',tracking=True)
    
    customer_visit_datetime = fields.Datetime(tracking=True)
    number_of_students = fields.Integer(string="No. Of Students",tracking=True)
    student_class = fields.Char("Student's Class", tracking=True)
    total_trips = fields.Integer("Total Trips", tracking=True)
    number_of_teachers = fields.Integer("Number of Teachers", tracking=True)
    
    
    @api.constrains('phone','mobile')
    def _onchange_phone_mobile_validation(self):
        for rec in self:
            if rec.phone:
                
                    try:
                        without_chars = int(rec.phone)
                        if len(str(without_chars)) != 10:
                            raise ValidationError("Please Enter 10 Digit Phone Number")
                            
                    except ValueError:
                        raise ValidationError("Please Enter Valid Phone Number")
                    
            
            if rec.mobile:
                
                    try:
                        without_chars = int(rec.mobile)
                        if len(str(without_chars)) != 10:
                            raise ValidationError("Please Enter 10 Digit Mobile Number")
                            
                    except ValueError:
                        raise ValidationError("Please Enter Valid Mobile Number")
            
    
    @api.constrains('email_from','email_cc')
    def validate_email_fields(self):
        for rec in self:
            if rec.email_cc:
                valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.email_cc)
                if not valid:
                    raise ValidationError("Please Enter a Valid CC Email Handle.")
            if rec.email_from:
                valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.email_from)
                if not valid:
                    raise ValidationError("Please Enter a Valid Email Handle.")
                
                
    def create_stakeholder_contact(self):
        for rec in self:
            if rec.other_stakeholders_ids:
                for record in rec.other_stakeholders_ids:
                    # print("here is the value of record",record)
                    contact = self.env['res.partner'].create(
                        {
                            'company_type':'person',
                            'name':record.name,
                            'email':record.mail,
                            'phone':record.phone,
                            'function':record.designation_id.name,
                            'parent_id': rec.partner_id.parent_id.id,
                            'is_primary_stakeholder_bool': record.is_primary_bool
                        }
                    )
                    record.partner_id = contact.id
                    print("creaeted record is here - ",contact.name)

    # def write(self, values):
    #     self.create_stakeholder_contact()
    #     result = super(CrmLeadInherit, self).write(values)
    #     return result
                
class Lead2OpportunityPartnerInherit(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    action = fields.Selection([
        ('create', 'Create a new Contact'),
        ('exist', 'Link to an existing Contact'),
        ('nothing', 'Do not link to a Contact')
    ], string='Related Contact', compute='_compute_action', readonly=False, store=True, compute_sudo=False,tracking=True)

    def action_apply(self):
        result = super(Lead2OpportunityPartnerInherit, self).action_apply()
        print("Here is our lead Id = ",self.lead_id)
        if self.lead_id:
            self.lead_id.create_stakeholder_contact()
        return result
    
