import logging

import requests
from odoo import fields, models, _
from odoo import http
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'crm.lead'

    # adding pipedrive fields
    pd_deals_id = fields.Integer("Pipedrive  Deals ID", readonly=True, copy=False)
    pd_deal_value = fields.Integer("Pipedrive deals Value")

    def create_deals(self, caller):
        _logger.info("*********EXPORTING FROM ODOO***************")
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        _logger.info("********URI CALLER*******".format(uri_caller))
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
                search_stage = self.env['crm.stage'].search([('id', '=', rec.stage_id.id)])
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/x-www-form-urlencoded'
                state = 'New'
                reason = self.env['crm.lost.reason'].search([('id', '=', rec.lost_reason_id.id)])
                if rec.lost_reason_id:
                    state = 'lost'
                elif rec.stage_id.name == 'Won':
                    state = 'won'
                else:
                    state = 'open'
                payload = {
                    'title': rec.name,
                    'person_id': rec.contact_name,
                    'org_id': rec.partner_id.id,
                    'value': rec.expected_revenue,
                    'stage_id': search_stage.pd_id,
                    'probability': rec.probability,
                    'status': state,
                    'lost_reason': reason.name
                }
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))
                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                if response:
                    data = response.json()
                    _logger.info("**************55 {}".format(data))
                    rec.write({'pd_deals_id': data.get('data').get('id')})
                    self.export_activities()

    def unlink(self):
        return super(ResCompany, self).unlink()

    def export_activities(self):
        '''
        This function will export activities from odoo to pipedrive
        :return:
        '''
        _logger.info("EXPORT ACTIVITIES")
        search_activity = self.env['mail.activity'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', self.id)])
        if search_activity:
            for rec in search_activity:
                if rec.pd_activity_id:
                    # This activity is been imported from pipedrive
                    return_val = self.check_activity_exists(rec.pd_activity_id)
                    if return_val:
                        # #Need to update the activity i.e send odoo dict to pipedrive
                        updated_data = self.odoo_update_activity(rec)
                    else:
                        # Need to create the activity in pipedrive
                        exp_data = self.create_activities(rec)
                else:
                    # This activity is been created from odoo which needs
                    # to be imported to pipedrive'''
                    self.create_activities(rec)

    def activities_filter(self):
        '''
        This function will filter deals and then send to pipedrive
        :return:
        '''
        rec = self.env['crm.lead'].search([])
        for fetch in rec:
            _logger.info("FETCHING DEALS FROM ODOO TO PIPEDIRVE")
            _logger.warning("No of records fetched are {}".format(len(rec)))
            fetch.export_activities()

    def create_activities(self, rec):
        '''This function will create an activity
        '''
        for fetch in rec:
            domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')

            uri = '{0}activities'
            uri_caller = uri.format(domain)
            _logger.info("******URI CALLER********* {}".format(uri_caller))
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
                search_type = self.env['mail.activity.type'].search([('id', '=', fetch.activity_type_id.id)])
                headers = {}
                payload = {
                    'subject': fetch.summary,
                    'type': search_type.name,
                    'deal_id': self.pd_deals_id,
                    'due_date': fetch.date_deadline,
                    'note': fetch.note
                }
                headers['Authorization'] = "Bearer " + company_id.access_token
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                headers['content-type'] = 'application/x-www-form-urlencoded'
                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
                _logger.info("**************66 {}".format(data))
                rec.write({'pd_activity_id': data.get('data').get('id')})

    def odoo_update_activity(self, rec):
        '''
        This function will update an activity
        :param pd_id:
        :return: updated data
        '''
        for fetch in rec:

            domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
            uri = '{0}activities/%s' % (fetch.pd_activity_id)
            uri_caller = uri.format(domain)

            format_date = fetch.date_deadline

            _logger.info("******URI CALLER**odoo******* {}".format(uri_caller))
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
                search_type = self.env['mail.activity.type'].search([('id', '=', fetch.activity_type_id.id)])
                headers = {}
                payload = {
                    'subject': fetch.summary,
                    'type': search_type.name,
                    'deal_id': self.pd_deals_id,
                    'due_date': fetch.date_deadline,
                    'note': fetch.note

                }
                headers['Authorization'] = "Bearer " + company_id.access_token
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                headers['content-type'] = 'application/x-www-form-urlencoded'
                response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
            return data

    def check_activity_exists(self, pd_activity_id):
        '''
        This function will check if activity_record exists in pipedrive
        :return:True if exists else False
        '''
        _logger.info("CHECKING IF ACTIVITY EXISTS!!!!!")

        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')

        uri = "{0}activities/%s" % (pd_activity_id)
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

            headers = {}

            headers['Authorization'] = "Bearer " + company_id.access_token
            headers['content-type'] = 'application/x-www-form-urlencoded'
            headers['Accept'] = 'application/json'
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))
            response = requests.get(url=uri_caller, headers=headers, verify=False)
            activity_data = response.json()
            _logger.info("**************88 {}".format(activity_data))
            if activity_data:
                res = activity_data.get('data')
                if res:
                    if res.get('active_flag') == True:
                        _logger.info("This activity exists in pipedrive")
                        return True

                    else:
                        _logger.warning("This activity does not exists in pipedrive")
                        return False

    def odoo_update_deals(self, pd_deals_id):
        '''
        This function will update the deals details in pipedrive
        :return: updates deals data
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = "{0}deals/%s" % (pd_deals_id)
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

                search_stage = self.env['crm.stage'].search([('id', '=', rec.stage_id.id)])
                headers = {}
                headers['Authorization'] = "Bearer " + company_id.access_token
                headers['content-type'] = 'application/x-www-form-urlencoded'
                state = False
                # status_lost = self.env['crm.lead.lost'].search([])
                reason = self.env['crm.lost.reason'].search([('id', '=', rec.lost_reason_id.id)])
                if rec.lost_reason_id:
                    state = 'lost'

                elif rec.stage_id.name == 'Won':
                    state = 'won'

                else:
                    state = 'open'
                payload = {
                    'id': rec.pd_deals_id,
                    'title': rec.name,
                    'person_id': rec.contact_name,
                    'org_id': rec.partner_id.pd_id,
                    'value': rec.expected_revenue,
                    # 'stage_id': search_stage.pd_id,
                    'probability': rec.probability,
                    'status': state,
                    'lost_reason': reason.name
                }

                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                data = response.json()
                _logger.info("**************99 {}".format(data))
                self.export_activities()

    def check_deals_exists(self, pd_deals_id):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = "{0}deals/%s" % (pd_deals_id)
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
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            headers['content-type'] = 'application/x-www-form-urlencoded'
            headers['Accept'] = 'application/json'
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))

            response = requests.get(url=uri_caller, headers=headers, verify=False)
            deals_data = response.json()
            _logger.info("**************12 {}".format(deals_data))
            if deals_data:
                res = deals_data.get('data')
                if res:
                    if res['active'] == True:
                        _logger.info("This deal exists in pipedrive")
                        return True

                    else:
                        _logger.warning("This deal does not exists in pipedrive")
                        return False

    def export_odoo_deals(self):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri_caller = "{0}deals".format(domain)
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
                headers['Accept'] = 'application/json'
                payload = {
                    'title': rec.name,
                    'person_id': rec.contact_name
                }
                if company_id.access_token:
                    _logger.info("Access token Found")
                else:
                    raise UserError(_("Access Token not found!!!"))

                response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                deals_data = response.json()
                _logger.info("**************13 {}".format(deals_data))

    def filter_deals(self):
        '''
        This function will filter deals and then send to pipedrive
        :return:
        '''
        rec = self.env['crm.lead'].search([])
        for fetch in rec:
            _logger.info("FETCHING DEALS FROM ODOO TO PIPEDIRVE")
            _logger.warning("No of records fetched are {}".format(len(rec)))
            fetch.export_deals()

    def export_deals(self):
        '''
        This function will export deals from odoo to pipedrive
        :return: exported deals data
        '''
        for rec in self:
            if rec.pd_deals_id:
                # This deal is been created form pipedrive
                return_val = self.check_deals_exists(rec.pd_deals_id)
                if return_val == True:
                    # Need to update the deal i.e send odoo dict to pipedrive
                    updated_data = self.odoo_update_deals(rec.pd_deals_id)
                else:
                    # Need to create the deal in pipedrive
                    exp_data = self.create_deals("deals")
            else:
                # This deal is been created from odoo which needs
                # to be imported to pipedrive'''
                self.create_deals("deals")
