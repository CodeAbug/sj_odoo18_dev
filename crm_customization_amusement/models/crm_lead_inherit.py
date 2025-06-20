from odoo import models,fields,api
from odoo.exceptions import ValidationError
import re


class ResPartnerInherit(models.Model):
    _inherit='res.partner'
    
    is_primary_stakeholder_bool = fields.Boolean('Primary Stakeholder',tracking=True)
    
    trip_count = fields.Integer(string="Trips", compute="_compute_trip_count")

    def _compute_trip_count(self):
        for partner in self:
            partner.trip_count = self.env['opportunity.trip'].search_count([('partner_id', '=', partner.id)])

    def action_view_partner_trips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Trip',
            'res_model': 'opportunity.trip',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
            'target': 'current',
        }
    
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
    
    visit = fields.Selection([('yes', 'Yes'),('no', 'No')], )
    visiting_person = fields.Char()
    other_stakeholders_ids = fields.One2many("other.stakeholder.line",'crm_lead_id',tracking=True)
    
    customer_visit_datetime = fields.Datetime(tracking=True)
    number_of_students = fields.Integer(string="No. Of Students",tracking=True)
    total_trips = fields.Integer("Total Trips", tracking=True)
    number_of_teachers = fields.Integer("Number of Teachers", tracking=True)
    school_strength = fields.Integer("School Strength", tracking=True)
    student_per_class = fields.Integer(string="Student Per Class",tracking=True)
    average_fees = fields.Float(tracking=True)
    budget_per_student = fields.Float(tracking=True)
    
    ### Proposal Stage Fields 
    total_proposal_amount = fields.Float("Proposal Amount",tracking=True,compute="_compute_total_proposal_amount")
    discount = fields.Float("Discount",tracking=True)
    negotiated_amount = fields.Float("Negotiated Amount",tracking=True,compute="_compute_total_negotiated_amount")
    
    @api.depends('order_ids.quotation_valuation_amount')
    def _compute_total_proposal_amount(self):
        for record in self:
            total = 0.0
            for line in record.order_ids:
                    total += line.quotation_valuation_amount
            record.total_proposal_amount = total
    
    @api.depends('total_proposal_amount','discount')
    def _compute_total_negotiated_amount(self):
        for record in self:
                record.negotiated_amount = record.total_proposal_amount - record.discount 
    
    
    #Trip 
    
    opportunity_trip_ids = fields.One2many('opportunity.trip','lead_id',tracking=True)
    trip_count = fields.Integer(string="Trip Count", compute="_compute_trip_count")
    booked_or_not = fields.Selection([
    ('contacted_with_booking', 'Contacted with Booking'),
    ('contacted_but_no_booking', 'Contacted but No Booking'),], tracking=True, default='contacted_but_no_booking')

    
    @api.depends('opportunity_trip_ids')
    def _compute_trip_count(self):
        for rec in self:
            rec.trip_count = len(rec.opportunity_trip_ids)
            if rec.trip_count > 0:
                rec.booked_or_not = 'contacted_with_booking'
            else:
                rec.booked_or_not = 'contacted_but_no_booking'
    
    def action_view_opportunity_trips(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Opportunity Trips',
            'res_model': 'opportunity.trip',
            'view_mode': 'list,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
            'target': 'current'
        }
        
    def open_trip_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Trip',
            'res_model': 'opportunity.trip',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_lead_type_id': self.lead_type_id.id,
                'default_visiting_center_id': self.visiting_center_id.id,
            }
        }
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
            
    def action_proposal(self):
        if self.type == 'opportunity':
            self.stage_id = 2 
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
    
