from odoo import models,fields,api
from odoo.exceptions import ValidationError,UserError
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
    
    
    def action_custom_save(self):

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Record Saved Successfully!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    lead_type_id = fields.Many2one('lead.type' , string="Lead Type" ,tracking=True)
    
    is_editable_bool = fields.Boolean(tracking=True,default=False)
    
    
    def enable_editing(self):
        self.with_context(skip_write_check=True).write({
            'is_editable_bool': True,
        })
        
        
    def write(self, vals):
        if not self.env.context.get('skip_write_check'):
            vals['is_editable_bool'] = False
        return super().write(vals)

    
    school_type_id = fields.Many2one('school.type', string="School Type" ,tracking=True)
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        default=lambda self: self.env.ref('base.in', raise_if_not_found=False)
    )
    visiting_center_id = fields.Many2one('city.city',tracking=True,string="Visiting Center")
    
    lead_source = fields.Selection([
                            ('whats_app', "What's App"),
                            ('website', 'Website'),
                            ('walkin', 'Walk-in'),
                            ('ivr', 'IVR')],
                            string="Lead Source",tracking=True)
    organization_id = fields.Many2one('res.partner',tracking=True)
    
    @api.onchange('partner_id')
    def fetch_organization_id(self):
        for rec in self:
            rec.organization_id = rec.partner_id.parent_id.id
            
    other_stakeholders_ids = fields.One2many("other.stakeholder.line",'crm_lead_id',tracking=True,copy=True)
    ##POC details 
    poc_email = fields.Char(tracking=True,string="P.O.C. Email")
    poc_mobile = fields.Char(tracking=True,string="P.O.C. Mobile No.")
    poc_designation_id = fields.Many2one('stakeholder.designation',tracking=True,string="P.O.C. Designation")
    
    secondary_poc_name = fields.Char(tracking=True ,string="Secondary P.O.C. Name")
    secondary_poc_mobile = fields.Char(tracking=True ,string="Secondary P.O.C. Mobile No.")
    secondary_poc_designation_id = fields.Many2one('stakeholder.designation',tracking=True,string=" Secondary P.O.C. Designation")
    secondary_poc_email = fields.Char(tracking=True,string="Secondary P.O.C. Email")
    
    
    first_visit_datetime = fields.Datetime(tracking=True)
    students_planned_for_visit = fields.Integer(string="Students Planned For Visit",tracking=True)
    # number_of_teachers  = fields.Char()
    total_trips = fields.Integer("Total Trips", tracking=True)
    school_strength = fields.Integer("School Strength", tracking=True)
    student_per_class = fields.Integer(string="Student Per Class",tracking=True)
    average_fees = fields.Float(tracking=True)
    #remove this field in next deploy
    budget_per_student = fields.Float()
    secondary_poc_role = fields.Char()
    poc_role = fields.Char()
    
    
    @api.constrains('stage_id', 'students_planned_for_visit', 'school_strength', 'student_per_class', 'average_fees')
    def _check_fields_if_stage_one(self):
        for rec in self:
            if rec.stage_id and rec.type == 'opportunity' and rec.lead_type_id.id == 3:
                errors = []

                if rec.stage_id.name == 'Proposition' and rec.students_planned_for_visit <= 0:
                    errors.append("Students Planned For Visit")

                if rec.stage_id.id == 2:
                    if rec.school_strength <= 0:
                        errors.append("School Strength")
                    if rec.student_per_class <= 0:
                        errors.append("Student Per Class")
                    if rec.average_fees <= 0:
                        errors.append("Average Fees")

                if errors:
                    raise ValidationError(
                        "The following fields must be greater than 0:\n- " +
                        "\n- ".join(errors)
                    )
    
    ### Proposal Stage Fields 
    total_proposal_amount = fields.Float("Proposal Amount Per Head",tracking=True,compute="_compute_total_proposal_amount")
    total_deal_value = fields.Float(tracking=True,compute="_compute_deal_value")
    total_package_count = fields.Integer(tracking=True,string="Total Packages",compute='_total_package_count')
    # negotiated_amount = fields.Float()
    # discount = fields.Float()
    
    @api.depends('order_ids.order_line','order_ids.state')
    def _total_package_count(self):
        for rec in self:
            total = 0 
            for order in rec.order_ids:
                if order.state =='sale':
                    total += len(order.order_line)                
            rec.total_package_count = total
    
    @api.depends('order_ids.deal_value','order_ids.order_line.product_uom_qty','order_ids','order_ids.state')
    def _compute_deal_value(self):
        for record in self:
            total = 0.0
            for line in record.order_ids:
                if line.state == 'sale':
                    total += line.deal_value
            record.total_deal_value = total
    
    @api.depends('team_id', 'type','opportunity_trip_ids.trip_status','order_ids.state')
    def _compute_stage_id(self):
        for lead in self:
            if not lead.stage_id:
                lead.stage_id = lead._stage_find(domain=[('fold', '=', False)]).id
                
            if lead.stage_id.id >= 2:

            # Trip Status Evaluation
                trip_visited = any(trip.trip_status == 'visited' for trip in lead.opportunity_trip_ids)
                # print('   trip  visited - -----------',trip_visited )
                
                if trip_visited:
                    visited_stage = self.env['crm.stage'].search([('id', '=', 5)], limit=1)
                    if visited_stage and lead.stage_id.id != visited_stage.id:
                        lead.stage_id = visited_stage.id
                    
                    
                elif not trip_visited and lead.stage_id.id ==5 :
                    # print('ELIF entered by trip not visited')
                    lead.stage_id = 3 
                        
                # Sale Order Evaluation
                any_confirmed = any(order.state == 'sale' for order in lead.order_ids)
                stage_to_set = 3 if any_confirmed else 2

                target_stage = self.env['crm.stage'].search([('id', '=', stage_to_set)], limit=1)
                if target_stage and lead.stage_id.id != target_stage.id:
                    lead.stage_id = target_stage.id
                
    @api.depends('order_ids.deal_value','order_ids.order_line','order_ids.order_line.price_unit','order_ids.state')
    def _compute_total_proposal_amount(self):
        for record in self:
            total = 0.0
            for line in record.order_ids:
                if line.state == 'sale':
                    for order_line in line.order_line:
                        if order_line.is_primary_valuation_product:
                            total += order_line.price_unit
                        
            record.total_proposal_amount = total

    #Trip 
    
    opportunity_trip_ids = fields.One2many('opportunity.trip','lead_id',tracking=True)
    trip_count = fields.Integer(string="Trip Count", compute="_compute_trip_count")
    booked_or_not = fields.Selection([
    ('contacted_with_booking', 'Trip Booked'),
    ('contacted_but_no_booking', 'No Trip Booked Yet'),], tracking=True, default='contacted_but_no_booking')
    total_trips_revenue = fields.Float(tracking=True,compute='_compute_total_trips_revenue')
    total_visited_trips = fields.Integer(tracking=True,compute= '_compute_trip_count')
    
    @api.depends('order_ids','opportunity_trip_ids','opportunity_trip_ids.pos_amount','opportunity_trip_ids.trip_status')
    def _compute_total_trips_revenue(self):
        for record in self:
            revenue = 0.0
            for trip in record.opportunity_trip_ids:
                if trip.trip_status == 'visited':
                    revenue += trip.pos_amount
            record.total_trips_revenue = revenue
    
    @api.depends('opportunity_trip_ids','opportunity_trip_ids.trip_status')
    def _compute_trip_count(self):
        for rec in self:
            rec.trip_count = len(rec.opportunity_trip_ids)
            rec.total_visited_trips = len(rec.opportunity_trip_ids.filtered(lambda t: t.trip_status=='visited'))
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
                'default_trip_poc_id': self.env['res.partner'].search([
                    ('parent_id', '=', self.partner_id.parent_id.id),
                    ('name', '=', self.contact_name)
                ], limit=1).id,
                'default_secondary_trip_poc_id': self.env['res.partner'].search([
                    ('parent_id', '=', self.partner_id.parent_id.id),
                    ('name', '=', self.secondary_poc_name)
                ], limit=1).id,
                'default_assigned_event_manager_id':self.user_id.id,
                'default_organization_id' : self.partner_id.parent_id.id
            }
        }
    @api.constrains('phone','mobile','poc_mobile')
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
            
            if rec.poc_mobile:
                
                    try:
                        without_chars = int(rec.poc_mobile)
                        if len(str(without_chars)) != 10:
                            raise ValidationError("Please Enter 10 Digit POC Mobile Number")
                            
                    except ValueError:
                        raise ValidationError("Please Enter Valid POC Mobile Number")
                    
            if rec.secondary_poc_mobile:
                
                    try:
                        without_chars = int(rec.secondary_poc_mobile)
                        if len(str(without_chars)) != 10:
                            raise ValidationError("Please Enter 10 Digit Secondary POC Mobile Number")
                            
                    except ValueError:
                        raise ValidationError("Please Enter Valid Secondary POC Mobile Number")
            
            
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
                
            if rec.poc_email:
                valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.poc_email)
                if not valid:
                    raise ValidationError("Please Enter a Valid POC Email Handle.")
                
            if rec.secondary_poc_email:
                valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', rec.poc_email)
                if not valid:
                    raise ValidationError("Please Enter a Valid Secondary POC Email Handle.")
                
                
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
                            'mobile':record.mobile,
                            'function':record.designation_id.name,
                            'parent_id': rec.partner_id.parent_id.id,
                            'is_primary_stakeholder_bool': record.is_primary_bool,
                            'phone': None
                        }
                    )
                    
                    
    def create_poc_with_different_creds(self):
        for record in self:
            if record.contact_name and record.partner_id:
                
                contact = self.env['res.partner'].search([
                    ('id', '=', record.partner_id.id),
                    ('name', '=', record.contact_name)
                ], limit=1)

                if contact:
                    contact.write({
                        'email': record.poc_email,
                        'mobile': record.poc_mobile,
                        'function': record.poc_role,
                        'phone': None
                    })
            if record.secondary_poc_name:
                contact = self.env['res.partner'].create(
                        {
                            'company_type':'person',
                            'name':record.secondary_poc_name,
                            'email':record.secondary_poc_email,
                            'mobile':record.secondary_poc_mobile,
                            'function':record.secondary_poc_role,
                            'parent_id': record.partner_id.parent_id.id,
                            'phone': None
                        }
                    )
            if not record.organization_id:
                record.organization_id = record.partner_id.parent_id.id
            
    def action_proposal(self):
        if self.type == 'opportunity':
            self.stage_id = 2 
    
    last_activity_info = fields.Html(string="Last Activity", compute="_compute_last_activity")
    last_activity_deadline = fields.Date(string="Activity Deadline", compute="_compute_last_activity")

    @api.depends('activity_ids')
    def _compute_last_activity(self):
        for lead in self:
            # use with_context to include archived/inactive activities
            all_activities = self.env['mail.activity'].with_context(active_test=False).search([
                ('res_model', '=', 'crm.lead'),
                ('res_id', '=', lead.id),
            ], order='create_date desc', limit=1)
            if all_activities:
                act = all_activities[0]
                summary = act.activity_type_id.name or 'Activity'
                state = act.state
                color = {
                    'planned': 'orange',
                    'done': 'green',
                    'cancelled': 'grey',
                    'overdue' : 'red'
                }.get(state, 'gray')
                if state == 'planned':
                    state = 'Scheduled'
                state = state.capitalize()
                lead.last_activity_info = f"{summary} - <span style='color:{color}; font-weight:bold'>{state}</span>"
                lead.last_activity_deadline = act.date_deadline
            else:
                lead.last_activity_info = 'No Activity'
                lead.last_activity_deadline = False

                
    @api.onchange('partner_name')
    def _onchange_partner_name(self):
        for rec in self:
            rec.name = rec.partner_name

    def action_revert_to_stage_one(self):
        for lead in self:
            if lead.stage_id.id != 3:
                raise UserError("This action is only allowed when stage is 3.")
            # Find stage 1
            stage_1 = self.env['crm.stage'].search([('id', '=', 1)], limit=1)
            if not stage_1:
                raise UserError("Stage with ID 1 not found.")

            # Update stage
            lead.stage_id = stage_1

            # Move related sale orders to draft if in 'sale' state
            sale_orders = self.env['sale.order'].search([
                ('opportunity_id', '=', lead.id),
                ('state', '=', 'sale')
            ])
            for so in sale_orders:
                so.action_cancel()  # Cancel first
                so.write({'state': 'draft'})  # Then draft
                
class Lead2OpportunityPartnerInherit(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner'

    name = fields.Selection([
        ('convert', 'Convert to opportunity'),
        ('merge', 'Merge with existing opportunities')
    ], string='Conversion Action', default='convert',
    readonly=False, store=True, compute_sudo=False)

    action = fields.Selection([
        ('create', 'Create a new Contact'),
        ('exist', 'Link to an existing Contact'),
    ], string='Related Contact', compute='_compute_action', readonly=False, store=True, compute_sudo=False,tracking=True)

    
    @api.depends('lead_id')
    def _compute_action(self):
        for convert in self:
            if convert.lead_id:
                partner = convert.lead_id._find_matching_partner()
                if partner:
                    convert.action = 'exist'
                else:
                    convert.action = 'create'
            else:
                convert.action = 'create'

    def action_apply(self):
        result = super(Lead2OpportunityPartnerInherit, self).action_apply()
        if self.lead_id:
            self.lead_id.create_stakeholder_contact()
            self.lead_id.create_poc_with_different_creds()
        return result
    
