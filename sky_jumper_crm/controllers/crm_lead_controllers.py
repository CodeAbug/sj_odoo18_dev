from odoo import http
from odoo.http import request
import json
from odoo.exceptions import ValidationError, UserError

class CrmLeadAPI(http.Controller):

    @http.route('/crm_lead/create_or_update', type='json', auth='public', methods=['POST'], csrf=False)
    def create_or_update_crm_lead(self, **kwargs):
        # Step 1: API Key Auth
        api_key = request.httprequest.headers.get('API-KEY')
        if not api_key:
            return {'status': 'error', 'message': 'API key is missing in headers'}

        api_keys_model = request.env['res.users.apikeys']
        user_id = api_keys_model.sudo()._check_credentials(scope='NONE', key=api_key)
        if not user_id:
            return {'status': 'error', 'message': 'Invalid API key'}

        user = request.env['res.users'].sudo().browse(user_id)
        if not user or not user.active:
            return {'status': 'error', 'message': 'User not found or inactive'}

        # Step 2: Parse JSON
        try:
            body = request.httprequest.data.decode('utf-8')
            data = json.loads(body)
        except Exception:
            return {'status': 'error', 'message': 'Invalid JSON format'}

        # Step 3: Validate phone
        phone = data.get('phone')
        if not phone:
            return {'status': 'error', 'message': 'phone is required'}
        if not data.get('partner_id'):
            return {'status': 'error', 'message': 'partner_id is required'}

        model = request.env['crm.lead']
        existing = model.sudo().search([('phone', '=', phone)], order='id desc', limit=1)

        # Step 4: Dynamic field preparation
        vals = {}
        errors = []

        # Handle Many2one fields by name search
        many2one_fields_map = {
            'lead_type_id': 'lead.type',
            'package_request_id': 'package.request',
            'source_id': 'utm.source',
            'partner_id': 'res.partner', 
        }

        for field, model_name in many2one_fields_map.items():
            if field in data:
                record = request.env[model_name].sudo().search([('name', '=', data[field])], limit=1)
                if record:
                    vals[field] = record.id
                else:
                    if field == 'partner_id':
                        # Create partner if not found
                        partner_name = data[field]
                        new_partner = request.env['res.partner'].with_user(user).create({
                            'name': partner_name
                        })
                        vals[field] = new_partner.id
                        errors.append(f"Partner '{partner_name}' was not found and has been created.")
                    else:
                        errors.append(f"{field} '{data[field]}' not found")
                data.pop(field)
        # Add remaining direct fields dynamically
        all_fields = model.fields_get().keys()
        for field, value in data.items():
            if field in all_fields:
                vals[field] = value

        # Determine if it's a birthday party lead
        if vals.get('lead_type_id'):
            lead_type = request.env['lead.type'].sudo().browse(vals['lead_type_id'])
            if lead_type and lead_type.name == 'Birthday Party':
                vals['is_birthday_party_lead'] = True

        if vals.get('partner_id'):
            vals['name'] = vals.get('partner_id')
            
        # Step 5: Create or update logic
        try:
            if not existing:
                new_record = model.with_user(user).create(vals)
                return {
                    'status': 'success',
                    'message': 'New CRM lead created',
                    'id': new_record.id,
                    'phone': new_record.phone,
                    'warnings': errors
                }
            else:
                existing.with_user(user).write(vals)
                return {
                    'status': 'success',
                    'message': 'Existing CRM lead updated',
                    'id': existing.id,
                    'phone': existing.phone,
                    'warnings': errors
                }
        except (ValidationError, UserError) as e:
            return {'status': 'error', 'message': str(e)}
        except Exception as e:
            return {'status': 'error', 'message': f'Unexpected error: {str(e)}'}
