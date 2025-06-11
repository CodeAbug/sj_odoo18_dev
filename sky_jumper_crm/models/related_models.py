from odoo import models,fields,api


class City(models.Model):
    _name = 'city.city'
    _order = 'id desc'

    name = fields.Char(string="City Name", copy=False,tracking=True)

class LeadType(models.Model):
    _name = 'lead.type'
    _order = 'id desc'

    name = fields.Char(string="Lead Type", copy=False,tracking=True)


class PackageRequest(models.Model):
    _name = 'package.request'
    _order = 'id desc'

    name = fields.Char(string="Name", copy=False,tracking=True)

class IncludedActivities(models.Model):
    _name = 'included.activities'
    _order = 'id desc'

    name = fields.Char(string="Name", copy=False,tracking=True)

class OngroundrRequirements(models.Model):
    _name = 'onground.requirements'
    _order = 'id desc'

    name = fields.Char(string="Name", copy=False,tracking=True)

class ResCompany(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one('city.city', string="City" ,tracking=True)