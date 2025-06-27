from odoo import api,fields, models
from datetime import datetime
from odoo.exceptions import ValidationError



class OpportunityTripPackageLine(models.Model):
    _name = 'opportunity.trip.package.line'
    _description = 'Trip Package Line'

    opportunity_trip_id = fields.Many2one('opportunity.trip', string="Trip")
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_qty = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price" ,related='product_id.lst_price',readonly=False)
    price_subtotal = fields.Float(string="Subtotal", compute='_compute_price_subtotal', store=True)

    discount = fields.Float(string="Discount (%)", default=0.0)  # New discount field
    @api.depends('product_uom_qty', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            discounted_price = line.price_unit * (1 - (line.discount / 100.0))
            line.price_subtotal = line.product_uom_qty * discounted_price

class OpportunityTrip(models.Model):
    _name='opportunity.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    
    name = fields.Char(tracking=True,default=lambda self: ('New'))
    lead_id = fields.Many2one('crm.lead',tracking=True,string="Lead/Opportunity")
    lead_type_id = fields.Many2one('lead.type',tracking=True)
    package_line_ids = fields.One2many(
        'opportunity.trip.package.line',
        'opportunity_trip_id',
        string="Trip Packages",
        copy=True
    )

    partner_id = fields.Many2one('res.partner',tracking=True,string="Contact/Organization")
    organization_id = fields.Many2one('res.partner',tracking=True,string="Organization")

    visiting_center_id = fields.Many2one('city.city',tracking=True)
    
    trip_status = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('visited', 'Visited'),
        ('cancelled', 'Cancelled'),
    ], string="Trip Status", tracking=True, default='draft')

    trip_count  = fields.Char(tracking=True)
    
    planned_number_of_students = fields.Integer(tracking=True,string="Planned No. Of Students")
    planned_number_of_staff = fields.Integer(tracking=True ,help="Teachers, helpers, bus drivers",string="Planned No. Of Staff")
    
    @api.constrains('planned_number_of_students', 'planned_number_of_staff')
    def _check_non_zero_values(self):
        for record in self:
            if record.planned_number_of_students <= 0:
                raise ValidationError("Planned number of students must be greater than 0.")
            if record.planned_number_of_staff <= 0.0:
                raise ValidationError("Planned number of Staff must be greater than 0.")
    
    advance_received = fields.Float(tracking=True,help="Token payment")
            
    assigned_event_manager_id =  fields.Many2one('res.users',tracking=True)
    
    trip_planned_date = fields.Date(tracking=True)
    trip_start_time = fields.Float(tracking=True)
    trip_end_time = fields.Float(tracking=True)
    trip_duration  = fields.Float(tracking=True,compute="_compute_trip_duration")
    # Remove this field in next deployment
    # actual_trip_amount = fields.Float()
    
    
    
    @api.constrains('trip_start_time', 'trip_end_time')
    def _check_time_validity(self):
        for rec in self:
            if rec.trip_start_time <= 0:
                raise ValidationError("Trip Start Time is required.")


            if not (0 <= rec.trip_start_time <= 24):
                raise ValidationError("Trip Start Time must be between 0 and 24 hours.")
            if not (0 <= rec.trip_end_time <= 24):
                raise ValidationError("Trip End Time must be between 0 and 24 hours.")
            
    @api.depends('trip_start_time', 'trip_end_time')
    def _compute_trip_duration(self):
        for rec in self:
            start = rec.trip_start_time or 0.0
            end = rec.trip_end_time or 0.0

            # Normalize times within 0–24
            start = max(0.0, min(24.0, start))
            end = max(0.0, min(24.0, end))

            # Handle overnight case: e.g. 22 to 2 should be 4 hours
            duration = end - start
            if duration < 0:
                duration += 24

            rec.trip_duration = round(duration, 2)

    
    trip_poc_id = fields.Many2one('res.partner',string="Trip P.O.C",tracking=True)
    secondary_trip_poc_id = fields.Many2one('res.partner',string="Secondary P.O.C",tracking=True)
    
    expected_amount = fields.Float(tracking=True,compute='_compute_trip_amount',string="Contracted Amount")
    revised_amount = fields.Float(tracking=True , compute='_compute_revised_amount',readonly=False)
    
    total_package_qty = fields.Float(string="Total Quantity", compute="_compute_package_summary", store=True)
    total_package_discount_amount = fields.Float(string="Total Discount Amount", compute="_compute_package_summary", store=True)
    total_package_amount = fields.Float(string="Total Amount", compute="_compute_package_summary", store=True)

    @api.depends('package_line_ids.product_uom_qty', 'package_line_ids.price_subtotal', 'package_line_ids.discount', 'package_line_ids.price_unit')
    def _compute_package_summary(self):
        for rec in self:
            rec.total_package_qty = sum(line.product_uom_qty for line in rec.package_line_ids)
            rec.total_package_amount = sum(line.price_subtotal for line in rec.package_line_ids)

            discount_amount = 0.0
            for line in rec.package_line_ids:
                if line.discount:
                    line_total_without_discount = line.product_uom_qty * line.price_unit
                    line_discount_amt = line_total_without_discount * (line.discount / 100)
                    discount_amount += line_discount_amt
            rec.total_package_discount_amount = discount_amount
    
    #After visit fields 
    number_of_visited_students = fields.Integer(tracking=True,string="No. Of Visited Students")
    number_of_visited_staff = fields.Integer(tracking=True , help="Teachers, helpers, bus drivers",string="No. Of Visited Staff")
    actual_visit_datetime = fields.Datetime(tracking=True)
    
    
    @api.depends('package_line_ids','package_line_ids.discount','package_line_ids.price_subtotal')
    def _compute_revised_amount(self):
        for record in self:
            total = 0.0
            for line in record.package_line_ids:
                total += line.price_subtotal
                    
            record.revised_amount = total
    
    
    @api.depends('planned_number_of_staff','planned_number_of_students',
                    'number_of_visited_staff',
        'number_of_visited_students',
                'lead_id','lead_id.total_proposal_amount')
    def _compute_trip_amount(self):
        for record in self:
            expected = 0.0
            actual = 0.0
            rate = record.lead_id.total_proposal_amount
            expected = (record.planned_number_of_students + record.planned_number_of_staff) * rate
            record.expected_amount = expected



    pos_invoice_number = fields.Char(tracking=True,string="POS Invoice No.")
    pos_attachment = fields.Binary(string="POS Attachment", attachment=True)
    file_name = fields.Char(string="Filename")
    pos_amount = fields.Float(tracking=True,string="POS Amount")
    pos_datetime = fields.Datetime(tracking=True)
    
    trip_rating = fields.Selection([
    ('0', 'No Ratings'),
    ('1', 'One Star'),
    ('2', 'Two Star'),
    ('3', 'Three Start'),
    ('4', 'Four Start'),
    ('5', 'Five Start'),])

    def action_fetch_packages_from_deal(self):
        for trip in self:
            if not trip.lead_id:
                raise ValidationError("No lead linked to the trip.")
            
            quotations = self.env['sale.order'].search([
                ('opportunity_id', '=', trip.lead_id.id),
                ('state', '=', 'sale')
            ])
            
            if not quotations:
                raise ValidationError("No confirmed quotations found for this opportunity.")

            trip.package_line_ids = [(5, 0, 0)]  
            
            values = []
            for order in quotations:
                for line in order.order_line:
                    values.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                    }))
            
            trip.package_line_ids = values
            
    def _update_lead_stage_on_sale(self):
        for trip in self:
            if trip.trip_status == 'visited' and trip.lead_id:
                lead = trip.lead_id
                stage_5 = self.env['crm.stage'].search([('id', '=', 5)], limit=1)
                if stage_5 and lead.stage_id.id != 5:
                    lead.stage_id = stage_5.id
            
    @api.model
    def create(self, vals):
        date_str = datetime.today().strftime('%d%m%y')
        sequence = self.env['ir.sequence'].next_by_code('opportunity.trip') or '0001'
        vals['name'] = f"TRIP-{date_str}-{sequence}"
        
        record = super(OpportunityTrip, self).create(vals)
        record._update_lead_stage_on_sale()
        return record
    
    def write(self, vals):
        res = super().write(vals)
        self._update_lead_stage_on_sale()
        return res

    
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
        
        
    