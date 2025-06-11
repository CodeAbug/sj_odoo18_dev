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

    s2_qualification_status = fields.Selection(
        [
            ('contacted', 'Contacted'),
            ('visited', 'Visited'),
            ('intro_email', 'Intro Email Sent'),
            ('follow_up', 'Follow Up'),
        ], tracking=True,
        string='Qualification Lead Status'
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
    
    ####### School Booking Qualification Stage fields ############

    type_of_school = fields.Char("Type Of School", help="Type of the school, e.g., Pre-school, Primary, Secondary, Higher Secondary, or College")
    preferred_date_of_visit = fields.Date("Preferred Date Of Visit", help="Preferred date or week for the school’s visit")
    purpose_of_visit = fields.Selection([
        ('field_trip', 'Field Trip'),
        ('annual_day', 'Annual Day Outing'),
        ('sports_week', 'Sports Week'),
        ('reward_program', 'Reward Program'),
    ], string="Purpose of Visit", help="Purpose of visit to the SkyJumper park")
    student_per_class = fields.Integer(
        string='Student Per Class',
        help="Number of students per class visiting the park"
    )
    free_teacher_visit_bool = fields.Boolean("Free Visits for Teachers?", help="Indicates whether free entry for teachers/staff is included based on group size")
    average_fees = fields.Float("Average Fees", help="Average fees charged per student at the school")
    budget_per_student = fields.Float("Budget per Student", help="Estimated budget range per student as shared by the school")
    total_trips_planned = fields.Integer("Total Trips Planned", help="Total number of trips planned by the school for the academic year")

    ########## School Booking - Proposition state Fields ##############

    included_activities_ids = fields.Many2many(
        'included.activities', 
        string="Included Activities",
        help="Activities included in the chosen package (trampoline, games, lunch, team-building, etc.)"
    )
    addons_pack = fields.Text("Add-ons Pack", help="Additional items or services like certificates, snacks, group photo, gift packs")
    quotation_sent_date  = fields.Date("Quotation Sent Date", help="Date on which the proposal/quotation was shared with the school")
    onground_requirements_ids = fields.Many2many(
        'onground.requirements', 
        string="On-ground Requirements",
        help="On-ground resources needed for the visit (first aid, security, lunch tables, audio system, etc.)"
    )
    quotation_amount = fields.Float("Quotation Amount", help="Total estimated cost of the visit, including students and staff")
    quotation_valid_till = fields.Date("Quotation Valid Till", help="Validity date for the quotation provided to the school")

    ################### Negotiation Stage fields ##############

    discount_percentage = fields.Float("Discount %", help="Discount percentage offered to the school during negotiation")
    negotiated_price =  fields.Float("Negotiated Price", help="Final negotiated price after applying discounts")
    buy_some_get_some_free = fields.Text("Buy some Get Some free", help="Special offer like buy one, get one free on certain items/services")
    book_five_get_one_free = fields.Text("Book for 5, Get 1 Free", help="Special offer where a group of 6 pays for only 5 entries")
    free_meal_coupon_bool = fields.Boolean("Free Meal Coupon", help="Indicates whether free meal coupons are included in the deal")
    happy_hour_bool = fields.Boolean("Happy Hour", help="Indicates whether happy hour discounts apply to the booking")

    
    ########## School Booking - Converted Stage Fields  ##############
    ############# this status will be added later after the discussions ###############
    # booking_status = fields.Selection([
    #     ('confirmed', 'Confirmed'),
    #     ('tentative', 'Tentative'),
    #     ('cancelled', 'Cancelled')
    # ], string="Booking Status", help="Final booking status: Confirmed, Tentative, or Cancelled")

    planned_vs_current_trips = fields.Char(string="Planned vs Current Trips", help="Example: 2/10 - number of planned trips vs current confirmed trips")

    shift_time_slot = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('full_day', 'Full Day')
    ], string="Shift Time Slot", help="Morning, Afternoon, or Full Day slot for the visit")

    confirmed_number_of_students = fields.Integer(string="Confirmed Number of Students", help="Final confirmed number of participating students")

    confirmed_number_of_staff = fields.Integer(string="Confirmed Number of Staff", help="Teachers, helpers, bus drivers, etc. accompanying students")

    meal_plan_details = fields.Text(string="Meal Plan (if applicable)", help="Meal details or attached menu for the event")

    advance_received = fields.Float(string="Advance Received", help="Token payment received from the client")

    final_payment_due = fields.Float(string="Final Payment Due", help="Remaining amount to be paid")

    invoice_number = fields.Char(string="Invoice Number", help="Auto-generated invoice number, integrated with POS system")

    booking_id = fields.Char(string="Booking ID", help="Unique ID for tracking the booking")

    assigned_event_manager = fields.Char(string="Assigned Event Manager", help="SkyJumper event coordinator assigned to the client")

    
    ##################### Re-engagement fields ###########
    # Added to Mailing List
    added_to_mailing_list = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Added to Mailing List")
    corporate_discount_code = fields.Char(string="Corporate Discount Code", help="Unique discount code for repeat events")
    anniversary_festival_offers = fields.Text(string="Anniversary / Festival Offers", help="Shared via email campaigns")
    last_visit_date = fields.Date(string="Last Visit Date", help="For reactivation")
    client_category = fields.Selection([
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver')
    ], string="Client Category", help="Corporate Client Category")


    ########## School Booking - Re-engagement Fields  ##############
    added_to_mailing_list = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Added to Mailing List", help="Whether the client has been added to the mailing list")

    discount_code = fields.Char(string="Discount Code", help="Unique discount code for repeat events or re-engagement offers")

    teacher_referral = fields.Boolean(string="Teacher Referral", help="Indicates if a teacher/staff has referred another school")

    last_visit_date = fields.Date(string="Last Visit Date", help="Last visit date, useful for planning follow-ups for the next academic cycle")

    
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
    
    
    