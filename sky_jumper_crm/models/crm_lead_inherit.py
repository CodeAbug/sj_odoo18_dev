from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime



class CrmLeadInherit(models.Model):
    
    _inherit = 'crm.lead'
    
    party_date = fields.Date('Party Date',tracking=True)
    no_of_persons = fields.Integer('No.of Persons',tracking=True)
    lead_type_id = fields.Many2one('lead.type', "Lead Type",tracking=True)
    lead_source = fields.Selection([
                            ('whats_app', "What's App"),
                            ('website', 'Website'),
                            ('walkin', 'Walk-in'),
                            ('ivr', 'IVR')],
                            string="Lead Source",tracking=True)
    
    s1_new_status = fields.Selection(
        [
            ('enquiry', 'Enquiry'),
            ('connected', 'Connected'),
            ('not_connected', 'Not Connected'),
            ('visit', 'Visit')
        ], tracking=True,
        string='New Stage Status'
    )

    s2_qualified_status = fields.Selection(
        [
            ('contacted', 'Contacted'),
            ('visited', 'Visited'),
            ('intro_email', 'Intro Email Sent'),
            ('follow_up', 'Follow Up'),
        ], tracking=True,
        string='Qualified Lead Status'
    )

    s3_proposal_status = fields.Selection(
        [
            ('given', 'Given'),
            ('resubmit', 'Resubmit'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ], tracking=True,
        string='Proposal Given Status'
    )

    s4_quotation_status = fields.Selection(
        [
            ('submitted', 'Submitted'),
            ('pending', 'Pending'),
            ('rejected', 'Rejected'),
        ], tracking=True,
        string='Quotation Accepted Status'
    )
    
    s5_contracted_status = fields.Selection(
        [
            ('advance_collected','Advance Collected'),
            ('first_trip_completed','First Trip Completed')
        ], tracking=True,
        string="Contracted Status"
    )
    
    
    
    
    
    nearest_branch_city_id = fields.Many2one('city.city',"Nearest Branch City" , tracking=True)
    session_id = fields.Char("Session Id",tracking=True)
    package_request_id = fields.Many2one('package.request', string='Package Requested', tracking=True)
    enquiry_date = fields.Date(string='Enquiry Date', default=fields.Datetime.now)
    whats_app_customer_id = fields.Char("WhatsApp Customer Id",tracking=True)
    expected_guests_count = fields.Integer("Expected Guests Count",tracking=True)
    time_slot = fields.Selection([
                                ('30_min','30 Min'),
                                ('60_min','60 Min'),
                                ('90_min','90 Min')], string="Time Slot",tracking=True)
    start_time = fields.Float(string='Party Start Time',tracking=True)
    end_time = fields.Float(string='Party End Time',tracking=True)
    total_hours = fields.Float(string='Total Hours',tracking=True)
    birthday_person_name = fields.Char("Birthday Person's Name",tracking=True)
    birthday_person_dob = fields.Date("Birthday Person's DOB",tracking=True)
    @api.constrains('birthday_person_dob')
    def _check_birthday_person_dob(self):
        for rec in self:
            if rec.birthday_person_dob and rec.birthday_person_dob > date.today():
                raise ValidationError("Birthday person's DOB cannot be a future date.")
            
    jumper = fields.Integer(string='No. of Jumper',tracking=True)
    non_jumper = fields.Integer(string='No. of Non Jumper',tracking=True)
    next_follow_up_date = fields.Datetime(string='Next Follow-Up Date',tracking=True)
    cancellation_remark = fields.Char(string='Cancellation Remark',tracking=True)
    
    birthday_person_gender = fields.Selection([
                            ('male', 'Male'),
                            ('female', 'Female'),
                            ('others', 'Others')],
                            string="Birthday Person's Gender",tracking=True)
    is_birthday_party_lead = fields.Boolean(string="Is Birthday Party Lead",compute="_compute_is_birthday_party_lead",store=True )
    @api.depends('lead_type_id', 'birthday_person_name', 'birthday_person_dob', 'birthday_person_gender',
            'source_id','lead_source')
    def _compute_is_birthday_party_lead(self):
        for rec in self:
            if rec.lead_type_id and rec.lead_type_id.name == 'Birthday Party':
                rec.is_birthday_party_lead = True
                
            else :
                rec.is_birthday_party_lead = False
                

    @api.depends('start_time', 'end_time')
    def _onchange_total_hours(self):
        for record in self:
            if record.start_time > 25 or record.start_time < 0:
                raise UserError('Please enter valid start time')
            if record.end_time > 25 or record.end_time < 0:
                raise UserError('Please enter valid end time')
            record.total_hours = record.end_time - record.start_time
    
    
    