from odoo import http
from odoo.http import request
import json
from odoo import http
from odoo.http import request
import json

class PartyEnquiryController(http.Controller):



    @http.route('/crm_lead/create_or_update', type='http', auth='public', methods=['POST'], csrf=False)
    def create_or_update_party_enquiry(self, **kwargs):
        import json

        # API Key Auth
        api_key = request.httprequest.headers.get('API-KEY')
        if not api_key:
            return json.dumps({'status': 'error', 'message': 'API key is missing in headers'})

        api_keys_model = request.env['res.users.apikeys']
        user_id = api_keys_model.sudo()._check_credentials(scope='NONE', key=api_key)
        if not user_id:
            return json.dumps({'status': 'error', 'message': 'Invalid API key'})

        user = request.env['res.users'].sudo().browse(user_id)
        if not user or not user.active:
            return json.dumps({'status': 'error', 'message': 'User not found or inactive'})

        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
        except json.JSONDecodeError:
            return json.dumps({'status': 'error', 'message': 'Invalid JSON format'})

        client_number = data.get('client_number')
        if not client_number:
            return json.dumps({'status': 'error', 'message': 'client_number is required'})
        if not data.get('client_name'):
            return json.dumps({'status': 'error', 'message': 'client_name is required'})

        model = request.env['crm.lead']
        existing = model.sudo().search([('mobile', '=', client_number)], order='id desc', limit=1)

        vals = {}
        errors = []

        # Handle lead_id
        if 'lead_id' in data:
            lead = request.env['lead.type'].sudo().search([('name', '=', data['lead_id'])], limit=1)
            if lead:
                vals['lead_type_id'] = lead.id
                # if data['lead_id'] == "Birthday Party":
                    # vals['is_birthday_party_lead'] = True
            else:
                errors.append(f"Lead Type '{data['lead_id']}' not found")
            data.pop('lead_id')

        # Handle city_name
        if 'city_name' in data:
            city = request.env['city.city'].sudo().search([('name', '=', data['city_name'])], limit=1)
            if city:
                vals['visiting_center_id'] = city.id
                # branch = request.env['res.company'].sudo().search([('city_id', '=', city.id)], limit=1)
                # vals['company_id'] = branch.id if branch else 1
            else:
                errors.append(f"City '{data['city_name']}' not found")
            data.pop('city_name')

        # Handle source_id
        if 'source_id' in data:
            source = request.env['utm.source'].sudo().search([('name', '=', data['source_id'])], limit=1)
            if source:
                vals['source_id'] = source.id
            else:
                errors.append(f"Source '{data['source_id']}' not found")
            data.pop('source_id')

        # Add remaining fields
        all_fields = model.fields_get().keys()
        for field, value in data.items():
            if field in all_fields:
                vals[field] = value

        # Ensure state
        vals['stage_id'] = False

        # Clear enquiry_handler
        vals['user_id'] = False
        
        vals['mobile'] = client_number
        # Case A: No record exists → CREATE
        if not existing:
            try:
                record = model.with_user(user).create(vals)
                return json.dumps({
                    'status': 'success',
                    'message': 'New enquiry created',
                    'id': record.id,
                    'client_number': record.mobile,
                    'warnings': errors
                })
            except Exception as e:
                return json.dumps({'status': 'error', 'message': str(e)})

        # Case B: If Record is closed or cancelled then CREATE NEW Lead
        elif existing.lost_reason_id :
            if not vals.get('client_name') and existing.mobile:
                vals['client_name'] = existing.mobile
            try:
                record = model.with_user(user).create(vals)
                return json.dumps({
                    'status': 'success',
                    'message': 'New enquiry created (previous was closed/cancelled)',
                    'id': record.id,
                    'client_number': record.mobile,
                    'warnings': errors
                })
            except Exception as e:
                return json.dumps({'status': 'error', 'message': str(e)})

        # Case C: Record is active → UPDATE
        else:
            try:
                existing.with_user(user).write(vals)
                return json.dumps({
                    'status': 'success',
                    'message': 'Existing enquiry updated',
                    'id': existing.id,
                    'client_name': existing.partner_name,
                    'client_number': existing.mobile,
                    'warnings': errors
                })
            except Exception as e:
                return json.dumps({'status': 'error', 'message': str(e)})


    @http.route('/party_enquiry_form/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_party_enquiry(self, **kwargs):
        # Step 1: Authenticate API key
        api_key = request.httprequest.headers.get('API-KEY')
        if not api_key:
            return json.dumps({'status': 'error', 'message': 'API key is missing in the request headers (API-KEY)'})

        api_keys_model = request.env['res.users.apikeys']
        user_id = api_keys_model.sudo()._check_credentials(scope='NONE', key=api_key)
        if not user_id:
            return json.dumps({'status': 'error', 'message': 'Invalid API key'})

        user = request.env['res.users'].sudo().browse(user_id)
        if not user or not user.active:
            return json.dumps({'status': 'error', 'message': 'User not found or inactive'})

        # Step 2: Parse JSON data
        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
        except json.JSONDecodeError:
            return json.dumps({'status': 'error', 'message': 'Invalid JSON format'})

        # Step 3: Validate minimal required fields
        if not data.get('client_number'):
            return json.dumps({'status': 'error', 'message': 'client_number is required'})
        if not data.get('client_name'):
            return json.dumps({'status': 'error', 'message': 'client_name is required'})

        vals = {}
        errors = []
        # client_number_data = data.get('client_number')
        # if data.get('client_number'):
        #     same_number_lead = request.env['crm.lead'].search(['client_number','=',client_number_data],order='id desc', limit=1)
            
        #     if same_number_lead.state not in ('cancelled','closed'):
                
                
            
            
        # Special handling: lead_id (name to ID)
        if 'lead_id' in data:
            lead_type = request.env['lead.type'].with_user(user).search([('name', '=', data['lead_id'])], limit=1)
            if lead_type:
                vals['lead_id'] = lead_type.id
            else:
                errors.append(f"Lead Type '{data['lead_id']}' not found")
            data.pop('lead_id')

        # Special handling: city_name to city_id and company_id
        if 'city_name' in data:
            city = request.env['city.city'].with_user(user).search([('name', '=', data['city_name'])], limit=1)
            if city:
                vals['city_id'] = city.id
                branch = request.env['res.company'].with_user(user).search([('city_id', '=', city.id)], limit=1)
                if branch:
                    vals['company_id'] = branch.id
                else:
                    vals['company_id'] = 1  # fallback to default company
            else:
                errors.append(f"City '{data['city_name']}' not found, So branch is set Default")
            data.pop('city_name')

        # Special handling: source_id (name to ID)
        if 'source_id' in data:
            source = request.env['utm.source'].with_user(user).search([('name', '=', data['source_id'])], limit=1)            
            if source:
                vals['source_id'] = source.id
            else:
                errors.append(f"Source '{data['source_id']}' not found")
            data.pop('source_id')

        # Step 4: Add other valid fields dynamically
        model = request.env['crm.lead']
        all_fields = model.fields_get().keys()
        for field, value in data.items():
            if field in all_fields:
                vals[field] = value

        # # Set default state if not provided
        vals['state'] = vals.get('state', 'inprogress')
        
        # Step 4.5: Prevent duplicates created within the last 10 minutes
        from datetime import datetime, timedelta

        ten_minutes_ago = datetime.now() - timedelta(minutes=10)
        domain = [
            ('create_date', '>=', ten_minutes_ago.strftime('%Y-%m-%d %H:%M:%S')),
            ('state', 'not in', ['closed', 'cancelled']),
            ('client_name', '=', vals.get('client_name')),
            ('client_number', '=', vals.get('client_number')),
            ('client_email', '=', vals.get('client_email')),
            ('lead_source', '=', vals.get('lead_source')),
            ('lead_id', '=', vals.get('lead_id')),
            ('city_id', '=', vals.get('city_id'))
            # ('source_id' ,'=',vals.get('source_id'))
        ]

        existing = model.with_user(user).search(domain, limit=1)
        if existing:
            return json.dumps({
                'status': 'error',
                'message': 'A similar enquiry was already created in the last 10 minutes. Record not created to avoid duplication.',
                'existing_id': existing.id,
                'existing_name' : existing.client_name,
                'existing_number' : existing.client_number
            })

        # Step 5: Create the record
        try:
            record = model.with_user(user).create(vals)
            response = {
                'status': 'success',
                'message': 'Record created successfully',
                'id': record.id,
                'client_number': record.client_number
            }
            if errors:
                response['warnings'] = errors
            return json.dumps(response)
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Failed to create record: {str(e)}'
            })

    
    @http.route('/party_enquiry_form/update', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_party_enquiry(self, **kwargs):
        # Step 1: Extract and authenticate the user via API key
        api_key = request.httprequest.headers.get('API-KEY')
        if not api_key:
            return json.dumps({
                'status': 'error',
                'message': 'API key is missing in the request headers (API-KEY)'
            })
        
        # Validate the API key using res.users.apikeys
        api_keys_model = request.env['res.users.apikeys']
        user_id = api_keys_model.sudo()._check_credentials(scope='NONE', key=api_key)
        if not user_id:
            return json.dumps({
                'status': 'error',
                'message': 'Invalid API key'
            })
        
        # Get the user associated with the API key
        user = request.env['res.users'].sudo().browse(user_id)
        if not user or not user.active:
            return json.dumps({
                'status': 'error',
                'message': 'User not found or inactive'
            })
        
        # Step 2: Parse the JSON body
        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
        except json.JSONDecodeError:
            return json.dumps({
                'status': 'error',
                'message': 'Invalid JSON format'
            })
        
        # Step 3: Find the record to update based on ID or phone number
        record_id = data.get('id')
        client_number = data.get('client_number')
        
        if not record_id and not client_number:
            return json.dumps({
                'status': 'error',
                'message': 'Either id or client_number must be provided to identify the record'
            })
        
        # Create domain to search for the record
        record = None
        if record_id:
            record = request.env['crm.lead'].with_user(user).search([('id', '=', record_id)], limit=1)
            if not record:
                return json.dumps({
                    'status': 'error',
                    'message': f'Record with ID {record_id} not found'
                })
        elif client_number:
            # Find the most recent record with this phone number
            records = request.env['crm.lead'].with_user(user).search([
                ('client_number', '=', client_number)
            ], order='id desc', limit=1)

            if not records:
                return json.dumps({
                    'status': 'error',
                    'message': f'No records found with phone number {client_number}'
                })
            
            record = records[0]

            # If record is closed or cancelled → create a new one instead
            if record.state in ['closed', 'cancelled']:
                new_vals = {}
                new_vals = data.copy()

                # Handle lead_id (convert name to ID)
                if 'lead_id' in new_vals:
                    lead_name = new_vals['lead_id']
                    lead_type = request.env['lead.type'].with_user(user).search([('name', '=', lead_name)], limit=1)
                    if lead_type:
                        new_vals['lead_id'] = lead_type.id
                    else:
                        new_vals.pop('lead_id', None)  # Remove if not valid

                # Handle city_name (convert name to ID)
                if 'city_name' in new_vals:
                    city_name = new_vals['city_name']
                    city = request.env['city.city'].with_user(user).search([('name', '=', city_name)], limit=1)
                    if city:
                        new_vals['city_id'] = city.id
                    else:
                        new_vals.pop('city_name', None)  # Remove if not valid
                    new_vals.pop('city_name', None)  # Always remove raw name key

                # If client_name is missing, fallback to previous
                if not new_vals.get('client_name') and record.client_name:
                    new_vals['client_name'] = record.client_name

                # Ensure client_number is set correctly
                new_vals['client_number'] = client_number

                # Set default state if not provided
                new_vals['state'] = new_vals.get('state', 'inprogress')

                try:
                    new_record = request.env['crm.lead'].with_user(user).create(new_vals)
                    return json.dumps({
                        'status': 'success',
                        'message': 'New enquiry created because previous one was closed or cancelled',
                        'id': new_record.id,
                        'client_number': new_record.client_number
                    })
                except Exception as e:
                    return json.dumps({
                        'status': 'error',
                        'message': f'Failed to create new record: {str(e)}'
                    })

            # Otherwise, use the existing record for updating
            record = records[0]
        # Step 4: Process special fields like city and lead_type by name
        update_vals = {}
        errors = []
        
        # Handle Package name if provided
        if 'package_request_id' in data:
            package_request_id = data.get('package_request_id')
            source = request.env['package.request'].with_user(user).search([('name', '=', package_request_id)], limit=1)
            if source:
                update_vals['package_request_id'] = package_request_id.id
            else:
                errors.append(f"Package with name '{package_request_id}' not found")
            # Remove Package from data to prevent trying to set a non-existent field
            data.pop('package_request_id')
        
        # Special handling: source_id (name to ID)
        if 'source_id' in data:
            source = request.env['utm.source'].with_user(user).search([('name', '=', data['source_id'])], limit=1)
            if source:
                update_vals['source_id'] = source.id
            else:
                errors.append(f"Source '{data['source_id']}' not found")
            data.pop('source_id')


        # Handle Source name if provided
        if 'source_id' in data:
            source_id = data.get('source_id')
            source = request.env['utm.source'].with_user(user).search([('name', '=', source_id)], limit=1)
            if source:
                update_vals['source_id'] = source.id
            else:
                errors.append(f"Source with name '{source_id}' not found")
            # Remove Source from data to prevent trying to set a non-existent field
            data.pop('source_id')
        
        # Handle city name if provided
        if 'city_name' in data:
            city_name = data.get('city_name')
            city = request.env['city.city'].with_user(user).search([('name', '=', city_name)], limit=1)
            
            if city:
                update_vals['city_id'] = city.id
                branch = request.env['res.company'].with_user(user).search([('city_id', '=', city.id)], limit=1)
                if branch:
                    update_vals['company_id'] = branch.id
                else :
                    update_vals['company_id'] = 1
            else:
                errors.append(f"City with name '{city_name}' not found, So branch is set Default")
            # Remove city_name from data to prevent trying to set a non-existent field
            data.pop('city_name')

        # if 'state' in data:
        #     state = data.get('state')
        #     if state:
        #         update_vals['state'] = state

        
        # Handle lead type name if provided
        if 'lead_id' in data:
            lead_id = data.get('lead_id')
            lead_type = request.env['lead.type'].with_user(user).search([('name', '=', lead_id)], limit=1)
            if lead_type:
                update_vals['lead_id'] = lead_type.id
                # errors.append(f"Lead type with name '{lead_id}' not found")
            # Remove lead_id from data to prevent trying to set a non-existent field
            data.pop('lead_id')
        
        # Process the rest of the fields
        for field, value in data.items():
            if field not in ['id', 'client_number']:  # Skip identification fields
                if hasattr(record, field):
                    update_vals[field] = value
        
        if not update_vals:
            return json.dumps({
                'status': 'error',
                'message': 'No valid fields to update'
            })
        
        # Step 5: Update the record with all processed fields
        try:
            record.write(update_vals)
            
            response_data = {
                'status': 'success',
                'message': 'Record updated successfully',
                'id': record.id,
                'client_number': record.client_number,
                'create_date': record.create_date.strftime('%Y-%m-%d %H:%M:%S') if record.create_date else None
            }
            
            # Add warnings if any cities or lead types were not found
            if errors:
                response_data['warnings'] = errors
                
            return json.dumps(response_data)
        except Exception as e:
            # Log the error for debugging
            # request.env['ir.logging'].sudo().create({
            #     'name': 'Party Enquiry Update Error',
            #     'type': 'server',
            #     'level': 'ERROR',
            #     'message': str(e),
            # })
            return json.dumps({
                'status': 'error',
                'message': f'Failed to update record: {str(e)}'
            })
    # @http.route('/party_enquiry_form/update/<int:record_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    # def update_party_enquiry(self, record_id, **kwargs):
    #     # Step 1: Extract and authenticate the user via API key
    #     api_key = request.httprequest.headers.get('API-KEY')
    #     if not api_key:
    #         return json.dumps({
    #             'status': 'error',
    #             'message': 'API key is missing in the request headers (API-KEY)'
    #         })
        
    #     # Validate the API key using res.users.apikeys
    #     api_keys_model = request.env['res.users.apikeys']
    #     user_id = api_keys_model.sudo()._check_credentials(scope='NONE', key=api_key)
    #     if not user_id:
    #         return json.dumps({
    #             'status': 'error',
    #             'message': 'Invalid API key'
    #         })
        
    #     # Get the user associated with the API key
    #     user = request.env['res.users'].sudo().browse(user_id)
    #     if not user or not user.active:
    #         return json.dumps({
    #             'status': 'error',
    #             'message': 'User not found or inactive'
    #         })
        
    #     # Step 2: Parse the JSON body
    #     try:
    #         body = request.httprequest.data.decode('utf-8')
    #         data = json.loads(body)
    #     except json.JSONDecodeError:
    #         return json.dumps({
    #             'status': 'error',
    #             'message': 'Invalid JSON format'
    #         })
        
    #     # Step 3: Find the record to update
    #     record = request.env['crm.lead'].with_user(user).search([('id', '=', record_id)], limit=1)
    #     if not record:
    #         return json.dumps({
    #             'status': 'error',
    #             'message': f'Record with ID {record_id} not found'
    #         })
        
    #     # Step 4: Update the record with provided fields
    #     try:
    #         # Extract only the fields that are provided in the request body
    #         update_vals = {}
    #         for field, value in data.items():
    #             if hasattr(record, field):
    #                 update_vals[field] = value
            
    #         if not update_vals:
    #             return json.dumps({
    #                 'status': 'error',
    #                 'message': 'No valid fields to update'
    #             })
            
    #         record.write(update_vals)
            
    #         return json.dumps({
    #             'status': 'success',
    #             'message': 'Record updated successfully',
    #             'id': record.id
    #         })
    #     except Exception as e:
    #         # Log the error for debugging
    #         request.env['ir.logging'].sudo().create({
    #             'name': 'Party Enquiry Update Error',
    #             'type': 'server',
    #             'level': 'ERROR',
    #             'message': str(e),
    #         })
    #         return json.dumps({
    #             'status': 'error',
    #             'message': f'Failed to update record: {str(e)}'
    #         })