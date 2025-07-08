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
        # print("-----------------session user ----------",user.name)
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
            
        if 'lead_type_id' in data:
            lead = request.env['lead.type'].sudo().search([('name', '=', data['lead_type_id'])], limit=1)
            if lead:
                vals['lead_type_id'] = lead.id
                # if data['lead_type_id'] == "Birthday Party":
                    # vals['is_birthday_party_lead'] = True
            else:
                errors.append(f"Lead Type '{data['lead_type_id']}' not found")
            data.pop('lead_type_id')

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
        vals['stage_id'] = 1

        # Clear enquiry_handler
        vals['user_id'] = user.id
        
        vals['mobile'] = client_number
        vals['type'] = 'lead'
        
        
        if 'client_name' in data:
            vals['name'] = data['client_name']
            vals['partner_name'] = data['client_name']
            data.pop('client_name')
            
        if 'client_email' in data:
            vals['email_from'] = data['client_email']
            data.pop('client_email')
        
        
        # Case A: No record exists → CREATE
        if not existing:
            try:
                record = model.with_user(user).create(vals)
                return json.dumps({
                    'status': 'success',
                    'message': 'New Lead created',
                    'id': record.id,
                    'client_number': record.mobile,
                    'warnings': errors
                })
            except Exception as e:
                return json.dumps({'status': 'error', 'message': str(e)})


        # Case B: If Record is closed or lost then CREATE NEW Lead
        elif existing.lost_reason_id :
            if not vals.get('client_name') and existing.mobile:
                vals['client_name'] = existing.mobile
            try:
                record = model.with_user(user).create(vals)
                return json.dumps({
                    'status': 'success',
                    'message': 'New Lead created (previous was closed/cancelled)',
                    'id': record.id,
                    'client_number': record.mobile,
                    'warnings': errors
                })
            except Exception as e:
                return json.dumps({'status': 'error', 'message': str(e)})

        # Case C: Record is active → UPDATE
        else:
            try:
                print('-----------------entered in write upate')
                print("Before Write---------------", vals)
                existing.sudo().write(vals)
                print("After Write------------------",vals)
                # existing.sudo().write(vals)
                return json.dumps({
                    'status': 'success',
                    'message': 'Existing Lead updated',
                    'id': existing.id,
                    'client_name': existing.partner_name,
                    'client_number': existing.mobile,
                    'warnings': errors
                })
            except Exception as e:
                return json.dumps({'status': 'error', 'message': str(e)})

