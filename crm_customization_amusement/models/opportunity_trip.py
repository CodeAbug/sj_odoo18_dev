from odoo import api,fields, models
from datetime import datetime



class OpportunityTrip(models.Model):
    _name='opportunity.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True,default=lambda self: ('New'))
    lead_id = fields.Many2one('crm.lead',tracking=True,string="Lead/Opportunity")
    lead_type_id = fields.Many2one('lead.type',tracking=True)
    
    partner_id = fields.Many2one('res.partner',tracking=True,string="Contact/Organization")
    
    visiting_center_id = fields.Many2one('city.city')
    
    trip_status = fields.Selection([
                            ('confirmed', "Confirmed"),
                            ('cancelled', 'Cancelled')],
                        
                            string="Trip Status",tracking=True)

    trip_count  = fields.Char(tracking=True)
    
    shift_time_slot = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('full_day', 'Full Day')
    ], string="Shift Time Slot", help="Morning, Afternoon, or Full Day slot for the visit")
    
    confirmed_number_of_students = fields.Integer(tracking=True)
    confirmed_number_of_staff = fields.Integer(tracking=True , help="Teachers, helpers, bus drivers")
    
    meal_plan = fields.Text(tracking=True)
    
    advance_received = fields.Float(tracking=True,help="Token payment")
    
    amount_paid = fields.Float(tracking=True)
    
    due_amount = fields.Float(tracking=True)
    
    assigned_event_manager_id =  fields.Many2one('res.users',tracking=True)
    
    
    
    trip_poc = fields.Char(string="Trip POC",tracking=True)
    trip_rating = fields.Selection([
    ('0', 'No Ratings'),
    ('1', 'One Star'),
    ('2', 'Two Star'),
    ('3', 'Three Start'),
    ('4', 'Four Start'),
    ('5', 'Five Start'),])
    @api.model
    def create(self, vals):
        date_str = datetime.today().strftime('%Y%m%d')
        sequence = self.env['ir.sequence'].next_by_code('opportunity.trip') or '0001'
        vals['name'] = f"TRIP-{date_str}-{sequence}"
        return super().create(vals)
    
    
    def action_confirm(self):
        for trip in self:
            trip.trip_status = 'confirmed'

    def action_cancel(self):
        for trip in self:
            trip.trip_status = 'cancelled'
            
            