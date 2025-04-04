import logging

import requests
from odoo import fields, models, _
from odoo import http
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.partner'

    # adding pipedrive fields
    pd_id = fields.Integer("Pipedrive ID", readonly=True, copy=False)

    def check_contact_exists(self, pd_id):
        '''
        This function will check if contact_record exists in pipedrive
        :return:True if exists else False
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')

        uri = "{0}persons/%s" % (pd_id)
        uri_caller = uri.format(domain)

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            headers['content-type'] = 'application/x-www-form-urlencoded'
            headers['Accept'] = 'application/json'
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))
            response = requests.get(url=uri_caller, headers=headers, verify=False)
            contact_data = response.json()
            _logger.info("**************contact1 {}".format(contact_data))
            if contact_data:
                res = contact_data.get('data')
                if res:
                    if res.get('active_flag') == True:
                        _logger.info("This contact exists in pipedrive")
                        return True

                    else:
                        _logger.warning("This contact does not exists in pipedrive")
                        return False

    def check_organization_exists(self, pd_id):
        '''
        This function will check if organization_record exists in pipedrive
        :return:True if exists else False
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')

        uri = "{0}organizations/%s" % (pd_id)
        uri_caller = uri.format(domain)

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            headers['content-type'] = 'application/x-www-form-urlencoded'
            headers['Accept'] = 'application/json'
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))
            response = requests.get(url=uri_caller, headers=headers, verify=False)
            contact_data = response.json()
            _logger.info("**************contact_data2 {}".format(contact_data))
            if contact_data:
                res = contact_data.get('data')
                if res:
                    if res.get('active_flag'):
                        _logger.info("This organization exists in pipedrive")
                        return True

                    else:
                        _logger.warning("This organization does not exists in pipedrive")
                        return False

    def create_organizations(self, caller):
        '''
        THis function will create an organization.
        :param caller:
        :return:
        '''

        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])

        for user in user_id:
            for company in user.company_ids:
                if company.access_token and company.refresh_token:
                    company_id = company
                    break
            if company_id:
                break
        # for company_id in user_id.company_ids:
        #     if company_id.access_token and company_id.refresh_token:
        #         company_id = company_id
        if company_id:
            for rec in self:
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/x-www-form-urlencoded'

                payload = {
                    'name': rec.name,
                    'owner_id': rec.id
                }
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
                _logger.info("**************data1 {}".format(data))
                if data.get('data').get('id'):
                    rec.write({'pd_id': data.get('data').get('id')})
                return data

    def odoo_update_organizations(self, pd_id):
        '''
        This function will update the organization details in pipedrive
        :return: updates organizations data
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = "{0}organizations/%s" % (pd_id)
        uri_caller = uri.format(domain)

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:

            for rec in self:
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/x-www-form-urlencoded'
                payload = {
                    'id': rec.pd_id,
                    'name': rec.name,
                    'owner_id': rec.id,
                }

                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
                _logger.info("**************update1 {}".format(data))

    def create_contacts(self, caller):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for user in user_id:
            for company in user.company_ids:
                if company.access_token and company.refresh_token:
                    company_id = company
                    break
            if company_id:
                break

        # for company_id in user_id.company_ids:
        #     if company_id.access_token and company_id.refresh_token:
        #         company_id = company_id
        if company_id:

            for rec in self:
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/x-www-form-urlencoded'

                payload = {
                    'name': rec.name,
                    'email': rec.email,
                    'phone': rec.mobile,
                    'owner_id': rec.id
                }
                if rec.parent_id.pd_id:
                    payload.update({'org_id': rec.parent_id.pd_id})
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
                _logger.info("**************contact_create1 {}".format(data))
                if data.get('data'):
                    if data.get('data').get('id'):
                        rec.write({'pd_id': data.get('data').get('id')})
                    return data

    def odoo_update_contacts(self, pd_id):
        '''
        This function will update the contact details in pipedrive
        :return: updates contact data
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = "{0}persons/%s" % (pd_id)
        uri_caller = uri.format(domain)

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:

            for rec in self:
                if rec.parent_id:
                    headers = {}
                    headers['Authorization'] = "Bearer " + company_id.access_token
                    headers['content-type'] = 'application/x-www-form-urlencoded'
                    search_org = self.env['res.partner'].search([('parent_id', '=', rec.parent_id.id)])
                    payload = {
                        'id': rec.pd_id,
                        'name': rec.name,
                        'phone': rec.mobile,
                        'owner_id': rec.id,
                    }

                    if rec.parent_id.pd_id:
                        payload.update({'org_id': rec.parent_id.pd_id})
                    if company_id.access_token:
                        _logger.info("Access token Found")
                    else:
                        raise UserError(_("Access Token not found!!!"))

                    response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                    data = response.json()
                    _logger.info("**************contact_update1 {}".format(data))
                    return data
                else:
                    headers = {}
                    headers['Authorization'] = "Bearer " + company_id.access_token
                    headers['content-type'] = 'application/x-www-form-urlencoded'
                    payload = {
                        'id': rec.pd_id,
                        'name': rec.name,
                    }

                    if company_id.access_token:
                        _logger.info("Access token Found")
                    else:
                        raise UserError(_("Access Token not found!!!"))

                    response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                    data = response.json()
                    _logger.info("**************1 {}".format(data))

                    if data.get('data').get('id'):
                        _logger.info("data coming-----------------")

    # def contacts_filter(self):
    #     '''
    #     THis function will get all records and then send to scheduler
    #     :return:
    #     '''
    #     rec = self.env['res.partner'].search([])
    #     for fetch in rec:
    #         _logger.info("FETCHING RECORDS FROM ODOO TO PIPEDIRVE")
    #         _logger.warning("No of records fetched are {}".format(len(rec)))
    #         fetch.export_contacts()
    #

    def contacts_filter(self):
        '''
        THis function will get all records and then send to scheduler
        :return:
        '''
        rec = self.env['res.partner'].search([])
        for fetch in rec:
            _logger.info("FETCHING RECORDS FROM ODOO TO PIPEDIRVE")
            _logger.warning("No of records fetched are {}".format(len(rec)))
            fetch.export_contacts()

    def export_contacts(self):
        '''
        This function exports contacts from odoo to piepdrive
        :return: contacts_data
        '''
        for rec in self:
            if rec.company_type == 'person':
                # this is individual record
                if rec.pd_id:
                    # if record is of pipedrive
                    return_val = self.check_contact_exists(rec.pd_id)
                    if return_val:
                        # Need to update the contact i.e send odoo dict to pipedrive
                        updated_data = self.odoo_update_contacts(rec.pd_id)
                    else:
                        # Need to create contact in pipedrive
                        exp_data = self.create_contacts("persons")
                else:
                    # This organization is been created from odoo which needs
                    # to be imported to pipedrive'''
                    self.create_contacts("persons")
            else:
                if rec.pd_id:
                    # if record is of pipedrive
                    return_val = self.check_organization_exists(rec.pd_id)
                    if return_val:
                        # Need to update the organization i.e send odoo dict to pipedrive
                        updated_data = self.odoo_update_organizations(rec.pd_id)
                    else:
                        # Need to create organization in pipedrive
                        exp_data = self.create_organizations("organizations")
                else:
                    # This organization is been created from odoo which needs
                    # to be imported to pipedrive'''
                    self.create_organizations("organizations")
