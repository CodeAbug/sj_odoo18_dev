from odoo import api,fields, models
from datetime import datetime
from odoo.exceptions import ValidationError


class OpportunityTrip(models.Model):
    _name='opportunity.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True,default=lambda self: ('New'))
    lead_id = fields.Many2one('crm.lead',tracking=True,string="Lead/Opportunity")
    lead_type_id = fields.Many2one('lead.type',tracking=True)
    
    partner_id = fields.Many2one('res.partner',tracking=True,string="Contact/Organization")
    
    visiting_center_id = fields.Many2one('city.city')
    
    trip_status = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('visited', 'Visited'),
        ('cancelled', 'Cancelled'),
    ], string="Trip Status", tracking=True, default='draft')

    trip_count  = fields.Char(tracking=True)
    
    shift_time_slot = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('full_day', 'Full Day')
    ], string="Shift Time Slot", help="Morning, Afternoon, or Full Day slot for the visit")
    
    planned_number_of_students = fields.Integer(tracking=True,string="Planned No. Of Students")
    planned_number_of_staff = fields.Integer(tracking=True ,help="Teachers, helpers, bus drivers",string="Planned No. Of Staff")
    
    advance_received = fields.Float(tracking=True,help="Token payment")
    
    amount_paid = fields.Float(tracking=True)
    
    due_amount = fields.Float(tracking=True)
    
    assigned_event_manager_id =  fields.Many2one('res.users',tracking=True)
    
    trip_planned_datetime = fields.Datetime(tracking=True)
    
    trip_poc = fields.Char(string="Trip P.O.C",tracking=True)
    
    
    @api.constrains('planned_number_of_students', 'planned_number_of_staff')
    def _check_non_zero_values(self):
        for record in self:
            if record.planned_number_of_students <= 0:
                raise ValidationError("Planned number of students must be greater than 0.")
            if record.planned_number_of_staff <= 0.0:
                raise ValidationError("Planned number of Staff must be greater than 0.")
    
    #After visit fields 
    number_of_visited_students = fields.Integer(tracking=True,string="No. Of Visited Students")
    number_of_visited_staff = fields.Integer(tracking=True , help="Teachers, helpers, bus drivers",string="No. Of Visited Staff")
    actual_visit_datetime = fields.Datetime(tracking=True)
    meal_plan = fields.Selection([('yes', 'Yes'),('no', 'No')],tracking=True,string="Meal Plan(Yes/No)")
    trampoline_park = fields.Selection([('yes', 'Yes'),('no', 'No')],tracking=True ,string="Trampoline Park(Yes/No)")
    laser_tag = fields.Selection([('yes', 'Yes'),('no', 'No')],tracking=True ,string="Laser Tag(Yes/No)")
    soft_play = fields.Selection([('yes', 'Yes'),('no', 'No')],tracking=True,string="Soft Play(Yes/No)")
    pos_invoice_number = fields.Char(tracking=True,string="POS Invoice No.")
    pos_amount = fields.Float(tracking=True,string="POS Amount")
    pos_datetime = fields.Datetime(tracking=True)
    
    
    trip_rating = fields.Selection([
    ('0', 'No Ratings'),
    ('1', 'One Star'),
    ('2', 'Two Star'),
    ('3', 'Three Start'),
    ('4', 'Four Start'),
    ('5', 'Five Start'),])
    @api.model
    def create(self, vals):
        date_str = datetime.today().strftime('%d%m%y')
        sequence = self.env['ir.sequence'].next_by_code('opportunity.trip') or '0001'
        vals['name'] = f"TRIP-{date_str}-{sequence}"
        return super().create(vals)
    
    
    def action_plan(self):
        for trip in self:
            trip.trip_status = 'planned'
        
    
    def action_visited(self):
        for trip in self:
            trip.trip_status = 'visited'
        
            
    def action_cancel(self):
        for trip in self:
            trip.trip_status = 'cancelled'
            
    def action_reset_draft(self):
        for trip in self:
            trip.trip_status = 'draft'
        