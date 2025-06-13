from odoo import models,fields,api




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
    
    other_stakeholders_ids = fields.One2many("other.stakeholder.line",'crm_lead_id',tracking=True)
    
    customer_visit_datetime = fields.Datetime(tracking=True)
    number_of_students = fields.Integer(string="No. Of Students",tracking=True)
    student_class = fields.Char("Student's Class", tracking=True)
    total_trips = fields.Integer("Total Trips", tracking=True)
    number_of_teachers = fields.Integer("Number of Teachers", tracking=True)
    
    
    
    
    
    

class Lead2OpportunityPartnerInherit(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    action = fields.Selection([
        ('create', 'Create a new Contact'),
        ('exist', 'Link to an existing Contact'),
        ('nothing', 'Do not link to a Contact')
    ], string='Related Contact', compute='_compute_action', readonly=False, store=True, compute_sudo=False,tracking=True)

