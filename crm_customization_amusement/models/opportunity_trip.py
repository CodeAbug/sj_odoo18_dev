from odoo import api,fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
import re



class OpportunityTripPackageLine(models.Model):
    _name = 'opportunity.trip.package.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    center_manager = fields.Char(related='visiting_center_id.center_manager_name')
    
    trip_status = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('visited', 'Visited'),
        ('cancelled', 'Cancelled'),
    ], string="Trip Status", tracking=True, default='draft')

    trip_cycle = fields.Char(
        string="Trip Number",
        compute="_compute_trip_cycle",
        store=True
    )

    @api.depends('lead_id')
    def _compute_trip_cycle(self):
        for record in self:
            raw_lead_id = record.lead_id.id

            lead_id = 0

            # Extract only digits from lead_id using regex
            match = re.search(r'\d+', str(raw_lead_id))
            # print('Match---------,',match)
            if match:
                lead_id = int(match.group())
            if lead_id:
                # Count all existing trips for this cleaned lead_id
                existing_trips = self.search_count([('lead_id', '=', lead_id)])
                # print('--------the lead id here = ', lead_id)
                # print('--------the existing trips here = ', existing_trips)
                # +1 if it's a new record
                sequence = existing_trips + (0 if record.id else 1)
                suffix = self._get_ordinal_suffix(sequence)
                record.trip_cycle = f"{sequence}{suffix} Trip"
            else:
                record.trip_cycle = "Trip"

    def _get_ordinal_suffix(self, number):
        if 10 <= number % 100 <= 20:
            return 'th'
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
    
    @api.onchange('lead_id')
    def _onchange_trip_cycle(self):
        self._compute_trip_cycle()
        
    planned_number_of_students = fields.Integer(tracking=True,string="Planned No. Of Students")
    planned_number_of_staff = fields.Integer(tracking=True ,help="Teachers, helpers, bus drivers",string="Planned No. Of Staff")
    expected_guests = fields.Integer(tracking=True)
    @api.constrains('planned_number_of_students', 'planned_number_of_staff','expected_guests')
    def _check_non_zero_values(self):
        for record in self:
            
            if record.planned_number_of_students <= 0 and record.lead_type_id.id == 3:
                raise ValidationError("Planned number of students must be greater than 0.")
            if record.planned_number_of_staff <= 0.0 and record.lead_type_id.id in (2,3):
                raise ValidationError("Planned number of Staff must be greater than 0.")
            elif record.expected_guests <= 0.0 and record.lead_type_id.id not in (2,3):
                raise ValidationError("Planned number of Expected Guests must be greater than 0.")
            
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
    linked_in_profile_link = fields.Char(tracking=True,readonly=False)
    secondary_trip_poc_id = fields.Many2one('res.partner',string="Secondary P.O.C",tracking=True)
    # expected_amount = fields.Float(tracking=True,compute='_compute_trip_amount',string="Contracted Amount")
    
    #  Remove this field in next deployment
    expected_amount = fields.Float(string="Contracted Amount")
    
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
    number_of_visited_staff = fields.Integer(tracking=True , string="No. Of Visited Staff")
    final_guests = fields.Integer(tracking=True)
    actual_visit_datetime = fields.Datetime(tracking=True)
    
    
    @api.depends('package_line_ids','package_line_ids.discount','package_line_ids.price_subtotal')
    def _compute_revised_amount(self):
        for record in self:
            total = 0.0
            for line in record.package_line_ids:
                total += line.price_subtotal
                    
            record.revised_amount = total
    
    
    # @api.depends('planned_number_of_staff','planned_number_of_students',
    #                 'number_of_visited_staff',
    #     'number_of_visited_students',
    #             'lead_id','lead_id.total_proposal_amount')
    # def _compute_trip_amount(self):
    #     for record in self:
    #         expected = 0.0
    #         actual = 0.0
    #         rate = record.lead_id.proposal_amount_perhead
    #         expected = (record.planned_number_of_students + record.planned_number_of_staff) * rate
    #         record.expected_amount = expected



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


    last_trip_rating = fields.Selection([
    ('0', 'No Ratings'),
    ('1', 'One Star'),
    ('2', 'Two Star'),
    ('3', 'Three Star'),
    ('4', 'Four Star'),
    ('5', 'Five Star'),
    ], string="Last Trip Rating", compute="_compute_last_trip_rating", store=False)
        
    @api.depends('organization_id', 'trip_planned_date')
    def _compute_last_trip_rating(self):
        for rec in self:
            rec.last_trip_rating = False
            if not rec.organization_id:
                continue
            last_trip = self.env['opportunity.trip'].search([
                ('organization_id', '=', rec.organization_id.id),
                ('id', '!=', rec.id),
                ('trip_planned_date', '<', rec.trip_planned_date),
            ], order='trip_planned_date desc', limit=1)
            if last_trip:
                rec.last_trip_rating = last_trip.trip_rating

        
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
        # Saving link to website in contact respartner
        trip_poc_id = vals.get('trip_poc_id')
        linked_in_link = vals.get('linked_in_profile_link')
        if trip_poc_id and linked_in_link:
            # print('---------self.trip_poc id ----',self.env['res.partner'].browse(trip_poc_id))
            self.env['res.partner'].browse(trip_poc_id).write({
                'website': linked_in_link
            })
            # print("===-----------------==Trip POC function",self.trip_poc_id.function)
        
        record = super(OpportunityTrip, self).create(vals)
        record._update_lead_stage_on_sale()
        return record
    
    def write(self, vals):
        res = super().write(vals)

        linked_in_link = vals.get('linked_in_profile_link')
        trip_poc_id = vals.get('trip_poc_id') or self.trip_poc_id.id  # fallback to current

        if trip_poc_id and linked_in_link:
            self.env['res.partner'].browse(trip_poc_id).write({
                'website': linked_in_link
            })
            # print("===-----------------==Trip POC function----",self.trip_poc_id.function)

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
        
        
    