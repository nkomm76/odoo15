import base64
import json
import logging

import requests
from odoo import fields, models, _
from odoo import http
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    def check_credentials(self):
        '''
        This function will check if access token is retrieved or not
        :return:raises warning if not available
        '''
        if self.access_token:
            _logger.info("Access Token available")
        else:
            raise UserError(_("Access token not available"))

    def pipeline_caller(self, caller):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        _logger.info("******URI CALLER********* {}".format(uri_caller))
        company_id = None
        user_id = self.env['res.users'].search([('active', '=', True)])
        # for company in user_id.company_ids:
        #     if company.access_token and company.refresh_token:
        #         company_id = company
        #         for user in user_id:

        for user in user_id:
            for company in user.company_ids:
                if company.access_token and company.refresh_token:
                    company_id = company
                    break
            if company_id:
                break

        data = False
        if company_id:
            # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
            headers = {}
            if not company_id.access_token:
                raise UserError(_("Please check the access token for %s" % company_id.name))
            headers['Authorization'] = "Bearer " + company_id.access_token
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))

            headers['content-type'] = 'application/x-www-form-urlencoded'
            more_items_in_collection = True
            check_token_req = requests.get(url=uri_caller, headers=headers, verify=False)
            check_token = check_token_req.json()
            if 'error' or 'errorCode' in check_token.keys():
                error_msg = check_token.get('error')
                if error_msg:
                    raise UserError(_(error_msg))
            start = 0
            while more_items_in_collection:
                responses = requests.get(url=uri_caller, headers=headers, verify=False,
                                         params={'start': start, 'limit': '100'})
                datas = responses.json()
                if datas:
                    additional_data = datas.get('additional_data')
                    if additional_data:
                        pagination = additional_data.get('pagination')
                        if pagination:
                            start = pagination.get('next_start')
                            more_items_in_collection = pagination.get('more_items_in_collection')
                        else:
                            more_items_in_collection = False
                if not data:
                    data = responses.json()
                else:
                    json_data = data.get('data')
                    if json_data:
                        json_data.extend(datas.get('data'))
        _logger.info("**************---------- {}".format(data))
        return data

    def pipeline_caller_id(self, caller):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        _logger.info("******URI CALLER********* {}".format(uri_caller))
        company_id = None
        user_id = self.env['res.users'].search([('active', '=', True)])
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
            # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))

            headers['content-type'] = 'application/x-www-form-urlencoded'

            response = requests.get(url=uri_caller, headers=headers, verify=False, params={'limit': '500'})
            data = response.json()
            _logger.info("**************==== {}".format(data))
            return data

    def pipeline_caller_id2(self, caller):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % (caller)
        uri_caller = uri.format(domain)
        _logger.info("******URI CALLER********* {}".format(uri_caller))
        company_id = None
        user_id = self.env['res.users'].search([('active', '=', True)])
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
            # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))

            headers['content-type'] = 'application/x-www-form-urlencoded'
            response = requests.get(url=uri_caller, headers=headers, verify=False)
            data = response.json()
            _logger.info("**************=====------ {}".format(data))
            return data

    def get_odoo_partner_id(self, pd_id):
        '''

        This function returns odoo id from pd_id

        :param : pd_id(int)
        :return: odoo_id(int) if found else False
        '''
        partner_id = self.env['res.partner'].search([('pd_id', '=', pd_id)])
        if partner_id:
            return partner_id.id
        return False

        # partner_id = self.env['res.partner'].search([('pd_id', '=', pd_id)])
        # if partner_id:
        #     for each in partner_id:
        #         if each.company_type == 'company':
        #             return each.id
        # return False

    def get_odoo_partner_deals_id(self, pd_deals_id):
        '''

            This function returns odoo id from pd_deals_id

        :param : pd_deals_id(int)
        :return: odoo_id(int) if found else False
        '''
        partner_id = self.env['res.partner'].search([('pd_id', '=', pd_deals_id)])
        # if partner_id:
        # 	return partner_id.id
        return False

    def import_stages(self):
        '''
        This function will import stages from pipedirve to odoo
        :return: stages_data
        '''
        self.check_credentials()
        _logger.info("*****IMPORT STAGES****")
        first_stage = self.pipeline_caller_id("stages/2")
        _logger.info("******FIRST STAGE DATA********** {}".format(first_stage))
        stage_data_list = []
        if first_stage.get('data'):
            stage_data_dict = {}
            if first_stage.get('data').get('id'):
                stage_data_dict['pd_id'] = first_stage.get('data').get('id')
            if first_stage.get('data').get('name'):
                stage_data_dict['name'] = first_stage.get('data').get('name')
            # if first_stage.get('data').get('deal_probability'):
            # 	stage_data_dict['probability'] = first_stage.get('data').get('deal_probability')
            if stage_data_dict:
                stage_data_list.append(stage_data_dict)

            _logger.info("STAGE DATA LST {}".format(stage_data_list))

            for stage_rec in stage_data_list:
                existing_record = self.env['crm.stage'].search([('pd_id', '=', stage_rec.get('pd_id'))])
                if not existing_record:
                    # Create the stage
                    stage_id = self.env['crm.stage'].create(stage_rec)
                else:
                    # Update the stage
                    existing_record.write(stage_rec)
        second_stage = self.pipeline_caller_id("stages/4")
        _logger.info("******SECOND STAGE DATA********** {}".format(second_stage))
        stage_data_list2 = []
        if second_stage.get('data'):
            stage_data_dict2 = {}
            if second_stage.get('data').get('id'):
                stage_data_dict2['pd_id'] = second_stage.get('data').get('id')
            if second_stage.get('data').get('name'):
                stage_data_dict2['name'] = second_stage.get('data').get('name')
            # if second_stage.get('data').get('deal_probability'):
            # 	stage_data_dict2['probability'] = second_stage.get('data').get('deal_probability')
            if stage_data_dict2:
                stage_data_list2.append(stage_data_dict2)
            _logger.info("SECOND STAGE DATA LST {}".format(stage_data_list2))
            for second_stage_rec in stage_data_list2:
                existing_record = self.env['crm.stage'].search([('pd_id', '=', second_stage_rec.get('pd_id'))])
                if not existing_record:
                    # Create the stage
                    stage_id = self.env['crm.stage'].create(second_stage_rec)
                else:
                    # Update the stage
                    existing_record.write(second_stage_rec)

    def import_organization(self):
        '''
        This function will get contacts from pipedrive app
        :return: contact details from piedrive
        '''
        # self.check_credentials()
        _logger.info("*****IMPORT ORGANIZATION****")
        orgs_data = self.pipeline_caller("organizations")
        _logger.info("******ORG DATA********** {}".format(orgs_data))
        organization_data_lst = []
        if orgs_data.get('data'):
            for org in orgs_data.get('data'):
                org_data_dict = {}
                if org.get('name'):
                    org_data_dict['name'] = org.get('name')
                if org.get('id'):
                    org_data_dict['pd_id'] = org.get('id')
                if org.get('address'):
                    org_data_dict['street'] = org.get('address')
                if org.get('address_locality'):
                    org_data_dict['city'] = org.get('address_locality')
                if org.get('address_postal_code'):
                    org_data_dict['zip'] = org.get('address_postal_code')
                if org_data_dict:
                    organization_data_lst.append(org_data_dict)
        _logger.info("ORGANIZATION DATA LST {}".format(organization_data_lst))
        for org_rec in organization_data_lst:
            # Since record which we will create is of company #type
            # org_rec['company_type'] = 'company'
            org_rec['is_company'] = True

            existing_record = self.env['res.partner'].search(
                [('pd_id', '=', org_rec.get('pd_id')), ('id', '!=', org_rec.get('pd_id'))])
            if not existing_record:
                # Then create
                org_id = self.env['res.partner'].create(org_rec)
            else:
                # Update the record
                existing_record.write(org_rec)

    def ImportOrganizationById(self, organization_id):
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}%s' % ('caller')
        uri_caller = domain + 'organizations/' + str(organization_id)
        _logger.info("******URI CALLER********* {}".format(uri_caller))
        company_id = None
        user_id = self.env['res.users'].search([('active', '=', True)])
        _logger.info("******user_id********* {}".format(user_id))
        for user_company_id in user_id.company_ids:
            if user_company_id.access_token and user_company_id.refresh_token:
                company_id = user_company_id
        _logger.info("******user_id********* {}".format(user_id))
        if company_id:
            # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
            headers = {}
            headers['Authorization'] = "Bearer " + company_id.access_token
            if company_id.access_token:
                _logger.info("Access token Found")
            else:
                raise UserError(_("Access Token not found!!!"))

            response = requests.get(url=uri_caller, headers=headers, verify=False)
            data = response.json()

            _logger.info("In createOrganizationById **************---------- {}".format(data))
            return data

    def createOrganizationById(self, organization_id):
        _logger.info("*****createOrganizationById****")
        orgs_data = self.ImportOrganizationById(organization_id)
        _logger.info("*************ORGANIZATION DATA BY ID**********".format(orgs_data))
        organization_data_lst = []

        if orgs_data.get('data'):
            # for org in orgs_data.get('data'):
            org_data_dict = {}
            if orgs_data['data']['name']:
                org_data_dict['name'] = orgs_data['data']['name']
            if orgs_data['data']['id']:
                org_data_dict['pd_id'] = orgs_data['data']['id']
            if orgs_data['data']['address']:
                org_data_dict['street'] = orgs_data['data']['address']
            if orgs_data['data']['address_locality']:
                org_data_dict['city'] = orgs_data['data']['address_locality']
            if orgs_data['data']['address_postal_code']:
                org_data_dict['zip'] = orgs_data['data']['address_postal_code']
            if org_data_dict:
                organization_data_lst.append(org_data_dict)

        _logger.info("ORGANIZATION DATA LST BY ID {}".format(organization_data_lst))
        org_id = False
        for org_rec in organization_data_lst:
            # Since record which we will create is of company #type
            # org_rec['company_type'] = 'company'
            org_rec['is_company'] = True
            existing_record = self.env['res.partner'].search(
                [('pd_id', '=', org_rec.get('pd_id'))])
            if not existing_record:
                # Then create
                org_id = self.env['res.partner'].create(org_rec)
            else:
                # Update the record
                existing_record.write(org_rec)

        return org_id

    def import_contacts(self):
        '''
        This function will get contacts from pipedrive app
        :return: contact details from piedrive
        '''
        # self.check_credentials()
        _logger.info("*****IMPORT CONTACTS****")
        contacts_data = self.pipeline_caller("persons")
        _logger.info("*************CONTACTS DATA**********".format(contacts_data))
        # Iterate in data key
        # This will go to create in odoo
        contacts_data_lst = []
        if contacts_data.get('data'):
            for contacts in contacts_data.get('data'):
                contacts_data_dict = {}

                if contacts.get('name'):
                    contacts_data_dict['name'] = contacts.get('name')

                if contacts.get('email'):
                    for mail in contacts.get('email'):
                        if mail.get('value'):
                            contacts_data_dict['email'] = mail.get('value')

                if contacts.get('phone'):
                    for get_contact in contacts.get('phone'):
                        if get_contact.get('value'):
                            contacts_data_dict['phone'] = get_contact.get('value')

                if contacts.get('id'):
                    contacts_data_dict['pd_id'] = contacts.get('id')

                if contacts.get('org_id'):
                    if isinstance(contacts.get('org_id'), dict):
                        if contacts.get('org_id').get('value'):
                            search_partner_id = self.env['res.partner'].search(
                                [('pd_id', '=', contacts.get('org_id').get('value')),
                                 ('id', '!=', contacts.get('org_id').get('value')), ('is_company', '=', True)])
                            for each in search_partner_id:
                                if each.is_company:
                                    if search_partner_id:
                                        contacts_data_dict['parent_id'] = each.id
                                    else:
                                        company_id = self.createOrganizationById(contacts.get('org_id').get('value'))
                                        contacts_data_dict['parent_id'] = company_id.id

                            # if search_partner_id:
                            #     contacts_data_dict['parent_id'] = search_partner_id.id
                            # else:
                            #     company_id = self.createOrganizationById(contacts.get('org_id').get('value'))
                            #     contacts_data_dict['parent_id'] = company_id.id
                if contacts_data_dict:
                    contacts_data_lst.append(contacts_data_dict)

        _logger.info("---------------------------CONTACTS DATA LST -------------------------".format(contacts_data_lst))
        for contacts_rec in contacts_data_lst:
            # Since record which we will create is of individual type
            contacts_rec['is_company'] = False

            existing_record = self.env['res.partner'].search(
                [('pd_id', '=', contacts_rec.get('pd_id')), ('id', '!=', contacts_rec.get('pd_id')),
                 ('is_company', '=', False), ('name', '=', contacts_rec.get('name')), ])
            if not existing_record:
                self.env['res.partner'].create(contacts_rec)
            else:
                for each in existing_record:
                    if 'parent_id' in contacts_rec:
                        if each.id == contacts_rec['parent_id']:
                            continue
                        else:
                            each.write(contacts_rec)
                    else:
                        each.write(contacts_rec)

            # for each in existing_record:
            #     if not existing_record:
            #         self.env['res.partner'].create(contacts_rec)
            #     elif 'parent_id' in contacts_rec:
            #         if each.id == contacts_rec['parent_id']:
            #             continue
            #         else:
            #             each.write(contacts_rec)
            #     else:
            #         each.write(contacts_rec)

    def import_products(self):
        '''
        This function will import products from pipedrive app
        :return: product data
        '''
        # self.check_credentials()
        _logger.info("*****IMPORT PRODUCTS****")
        prod_data = self.pipeline_caller("products")
        product_data_lst = []
        update_data_lst = []
        if prod_data.get('data'):
            for products in prod_data.get('data'):
                product_data_dict = {}
                if products.get('name'):
                    product_data_dict['name'] = products.get('name')
                if products.get('id'):
                    product_data_dict['pd_prod_id'] = products.get('id')
                if products.get('code'):
                    product_data_dict['default_code'] = products.get('code')
                if products.get('prices'):
                    for fetch in products.get('prices'):
                        if fetch.get('price'):
                            product_data_dict['lst_price'] = fetch.get('price')
                        if fetch.get('cost'):
                            product_data_dict['standard_price'] = fetch.get('cost')
                        if fetch.get('overhead_cost'):
                            product_data_dict['pd_direct_code'] = fetch.get('overhead_cost')
                        if fetch.get('currency'):
                            product_data_dict['pd_currency'] = fetch.get('currency')
                            pricelist = self.env['product.pricelist'].search(
                                [('currency_id.name', '=', fetch.get('currency'))], limit=1).browse(0)

                            if pricelist:
                                update_pricelist = self.env['product.pricelist.item'].search(
                                    [('pricelist_id', '=', pricelist.id)])
                                update = {}
                                browse_prod = self.env['product.product'].search(
                                    [('pd_prod_id', '=', product_data_dict['pd_prod_id'])])
                                if browse_prod:
                                    update['product_id'] = browse_prod.id
                                    update['pricelist_id'] = pricelist.id
                                    update['fixed_price'] = fetch.get('price')
                                    update_data_lst.append(update)
                                    if pricelist.id:
                                        # search if pipedrive's currency exists in odoo
                                        for update_rec in update_data_lst:
                                            creation = self.env['product.pricelist.item'].create(update_rec)
                                    else:
                                        pass

                if product_data_dict:
                    product_data_lst.append(product_data_dict)

        for prod_rec in product_data_lst:
            existing_record = self.env['product.product'].search([('pd_prod_id', '=', prod_rec.get('pd_prod_id'))])
            if not existing_record:
                # Then create
                products_id = self.env['product.product'].create(prod_rec)
            else:
                # Update the record
                existing_record.write(prod_rec)

        else:
            return None

    def lost_deals(self):
        _logger.info("*****IMPORT LOST DEALS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!****")
        deals_data = self.pipeline_caller("deals")
        deals_lost_lst = []
        if deals_data.get('data'):
            for deals in deals_data.get('data'):
                _logger.info("DEALS ARE:{}".format(deals))
                deals_lost_dict = {}
                if deals.get('status') == 'lost':
                    if deals.get('title'):
                        deals_lost_dict['name'] = deals.get('title')
                    if deals.get('id'):
                        deals_lost_dict['pd_deals_id'] = deals.get('id')
                    if deals.get('value'):
                        deals_lost_dict['expected_revenue'] = deals.get('value')
                    if deals.get('probability'):
                        deals_lost_dict['probability'] = deals.get('probability')
                    if deals.get('stage_id'):
                        search_stage = self.env['crm.stage'].search([('pd_id', '=', deals.get('stage_id'))])
                        deals_lost_dict['stage_id'] = search_stage.id

                    if deals.get('org_name'):
                        deals_lost_dict['partner_name'] = deals.get('org_name')

                    if deals.get('person_name'):
                        deals_lost_dict['contact_name'] = deals.get('person_name')

                    if deals.get('org_id'):
                        if deals.get('org_id').get('value'):
                            parent_id = self.get_odoo_partner_deals_id(deals.get('org_id').get('value'))
                            if parent_id:
                                deals_lost_dict['partner_id'] = parent_id
                            else:
                                _logger.info("------------------NO parent_id------------------------")

                    if deals.get('person_id'):
                        if deals.get('person_id').get('email'):
                            for fetch in deals.get('person_id').get('email'):
                                deals_lost_dict['email_from'] = fetch.get('value')

                        if deals.get('person_id').get('phone'):
                            for fetch in deals.get('person_id').get('phone'):
                                deals_lost_dict['phone'] = fetch.get('value')

                    # if deals.get('person_id').get('value'):
                    # 	deals_lost_dict['pd_parent_deals_id'] = deals.get('person_id').get('value')

                    if deals.get('org_id'):
                        if deals.get('org_id').get('address'):
                            deals_lost_dict['street'] = deals.get('org_id').get('address')

                    if deals.get('expected_close_date'):
                        deals_lost_dict['date_deadline'] = deals.get('expected_close_date')

                    if deals_lost_dict:
                        deals_lost_lst.append(deals_lost_dict)

                _logger.info("DEALS Lost LST {} ".format(deals_lost_lst))

        for deals_rec in deals_lost_lst:
            existing_record = self.env['crm.lead'].search([('pd_deals_id', '=', deals_rec.get('pd_deals_id')),
                                                           ('active', '=', False), ])

            # search([('pd_deals_id', '=', deals_rec.get('pd_deals_id')),('probability','=',0))])
            if not existing_record:
                # Then create
                partner_id = self.env['crm.lead'].create(deals_rec)
                if partner_id:
                    partner_id.action_set_lost()

                # Attach name
                if deals_rec.get('pd_deals_id'):
                    parent_id = self.get_odoo_partner_id(deals_rec.get('pd_deals_id'))
                    # if parent_id:
                    #     partner_id.write({
                    #         'parent_id': parent_id
                    #     })

            else:
                # Update the record
                # parent_id = self.get_odoo_partner_id(deals_rec.get('pd_parent_deals_id'))
                existing_record.write(deals_rec)
                existing_record.action_set_lost()

    def import_other_deals(self):
        '''
        This function will get deals from pipedrive app
        :return deals from piedrive
        '''

        _logger.info("*****IMPORT OTHER DEALS****")
        deals_data = self.pipeline_caller("deals")

        # Iterate in data key
        # This will go to create in odoo
        deals_data_lst = []
        if deals_data.get('data'):
            for deals in deals_data.get('data'):
                _logger.info("DEALS ARE:{}".format(deals))
                deals_data_dict = {}
                if deals.get('deleted') == False:
                    if deals.get('status') == 'lost':
                        self.lost_deals()
                    if deals.get('status') == 'won':
                        deals_data_dict['stage_id'] = 4
                        if deals.get('title'):
                            deals_data_dict['name'] = deals.get('title')
                        if deals.get('id'):
                            deals_data_dict['pd_deals_id'] = deals.get('id')
                        if deals.get('value'):
                            deals_data_dict['expected_revenue'] = deals.get('value')
                        if deals.get('probability'):
                            deals_data_dict['probability'] = deals.get('probability')
                        # if deals.get('stage_id'):
                        # 	search_stage = self.env['crm.stage'].search([('pd_id', '=', deals.get('stage_id'))])
                        # 	deals_data_dict['stage_id'] = search_stage.id

                        if deals.get('org_name'):
                            deals_data_dict['partner_name'] = deals.get('org_name')

                        if deals.get('person_name'):
                            deals_data_dict['contact_name'] = deals.get('person_name')

                        if deals.get('org_id'):
                            if deals.get('org_id').get('value'):
                                parent_id = self.get_odoo_partner_deals_id(deals.get('org_id').get('value'))
                                if parent_id:
                                    deals_data_dict['partner_id'] = parent_id
                                else:
                                    _logger.info("------------------NO parent_id------------------------")

                        if deals.get('person_id'):
                            if deals.get('person_id').get('email'):
                                for fetch in deals.get('person_id').get('email'):
                                    deals_data_dict['email_from'] = fetch.get('value')

                            if deals.get('person_id').get('phone'):
                                for fetch in deals.get('person_id').get('phone'):
                                    deals_data_dict['phone'] = fetch.get('value')

                        # if deals.get('person_id').get('value'):
                        # 	deals_data_dict['pd_parent_deals_id'] = deals.get('person_id').get('value')

                        if deals.get('org_id'):
                            if deals.get('org_id').get('address'):
                                deals_data_dict['street'] = deals.get('org_id').get('address')

                        if deals.get('expected_close_date'):
                            deals_data_dict['date_deadline'] = deals.get('expected_close_date')

                        if deals_data_dict:
                            deals_data_lst.append(deals_data_dict)

                        if deals.get('status') == 'won':
                            deals_data_dict['stage_id'] = 4
                        if deals.get('title'):
                            deals_data_dict['name'] = deals.get('title')
                        if deals.get('id'):
                            deals_data_dict['pd_deals_id'] = deals.get('id')
                        if deals.get('value'):
                            deals_data_dict['expected_revenue'] = deals.get('value')
                        if deals.get('probability'):
                            deals_data_dict['probability'] = deals.get('probability')
                        # if deals.get('stage_id'):
                        # 	search_stage = self.env['crm.stage'].search([('pd_id', '=', deals.get('stage_id'))])
                        # 	deals_data_dict['stage_id'] = search_stage.id

                        if deals.get('org_name'):
                            deals_data_dict['partner_name'] = deals.get('org_name')

                        if deals.get('person_name'):
                            deals_data_dict['contact_name'] = deals.get('person_name')

                        if deals.get('org_id'):
                            if deals.get('org_id').get('value'):
                                parent_id = self.get_odoo_partner_deals_id(deals.get('org_id').get('value'))
                                if parent_id:
                                    deals_data_dict['partner_id'] = parent_id
                                else:
                                    _logger.info("------------------NO parent_id------------------------")

                        if deals.get('person_id'):
                            if deals.get('person_id').get('email'):
                                for fetch in deals.get('person_id').get('email'):
                                    deals_data_dict['email_from'] = fetch.get('value')

                            if deals.get('person_id').get('phone'):
                                for fetch in deals.get('person_id').get('phone'):
                                    deals_data_dict['phone'] = fetch.get('value')

                        # if deals.get('person_id').get('value'):
                        # 	deals_data_dict['pd_parent_deals_id'] = deals.get('person_id').get('value')

                        if deals.get('org_id'):
                            if deals.get('org_id').get('address'):
                                deals_data_dict['street'] = deals.get('org_id').get('address')

                        if deals.get('expected_close_date'):
                            deals_data_dict['date_deadline'] = deals.get('expected_close_date')

                        if deals_data_dict:
                            deals_data_lst.append(deals_data_dict)

        # _logger.info("DEALS DATA LST {} ".format(deals_data_lst))

        for deals_rec in deals_data_lst:
            existing_record = self.env['crm.lead'].search([('pd_deals_id', '=', deals_rec.get('pd_deals_id'))])
            if not existing_record and deals_rec:
                # Then create

                partner_id = self.env['crm.lead'].create(deals_rec)
                if partner_id:
                    # SET RAINBOWMAN
                    partner_id.action_set_won_rainbowman()
                # Attach name
                if deals_rec.get('pd_deals_id'):
                    parent_id = self.get_odoo_partner_id(deals_rec.get('pd_deals_id'))
                    # if parent_id:
                    # partner_id.write({
                    # 	'parent_id': parent_id
                    # })

            else:
                # Update the record
                # parent_id = self.get_odoo_partner_id(deals_rec.get('pd_parent_deals_id'))

                existing_record.write(deals_rec)
                existing_record.action_set_won_rainbowman()

    def import_deals(self):
        '''
        This function will get deals from pipedrive app
        :return deals from piedrive
        '''
        # self.check_credentials()
        _logger.info("*****IMPORT DEALS****")
        deals_data = self.pipeline_caller("deals")

        # Iterate in data key
        # This will go to create in odoo
        deals_data_lst = []
        if deals_data.get('data'):

            for deals in deals_data.get('data'):
                _logger.info("DEALS ARE:{}".format(deals))
                deals_data_dict = {}
                if deals.get('active') == True:
                    if deals.get('title'):
                        deals_data_dict['name'] = deals.get('title')
                    if deals.get('id'):
                        deals_data_dict['pd_deals_id'] = deals.get('id')
                    if deals.get('value'):
                        deals_data_dict['expected_revenue'] = deals.get('value')
                    if deals.get('probability'):
                        deals_data_dict['probability'] = deals.get('probability')
                    if deals.get('stage_id'):
                        search_stage = self.env['crm.stage'].search([('pd_id', '=', deals.get('stage_id'))])
                        deals_data_dict['stage_id'] = search_stage.id

                    if deals.get('org_name'):
                        deals_data_dict['partner_name'] = deals.get('org_name')

                    if deals.get('person_name'):
                        deals_data_dict['contact_name'] = deals.get('person_name')

                    if deals.get('org_id'):
                        if deals.get('org_id').get('value'):
                            parent_id = self.get_odoo_partner_deals_id(deals.get('org_id').get('value'))
                            if parent_id:
                                deals_data_dict['partner_id'] = parent_id
                            else:
                                _logger.info("------------------NO parent_id------------------------")

                    if deals.get('person_id'):
                        if deals.get('person_id').get('email'):
                            for fetch in deals.get('person_id').get('email'):
                                deals_data_dict['email_from'] = fetch.get('value')

                        if deals.get('person_id').get('phone'):
                            for fetch in deals.get('person_id').get('phone'):
                                deals_data_dict['phone'] = fetch.get('value')

                    # if deals.get('person_id').get('value'):
                    # 	deals_data_dict['pd_parent_deals_id'] = deals.get('person_id').get('value')

                    if deals.get('org_id'):
                        if deals.get('org_id').get('address'):
                            deals_data_dict['street'] = deals.get('org_id').get('address')

                    if deals.get('expected_close_date'):
                        deals_data_dict['date_deadline'] = deals.get('expected_close_date')

                    if deals_data_dict:
                        deals_data_lst.append(deals_data_dict)

        _logger.info("DEALS DATA LST {} ".format(deals_data_lst))

        for deals_rec in deals_data_lst:
            existing_record = self.env['crm.lead'].search([('pd_deals_id', '=', deals_rec.get('pd_deals_id'))])
            if not existing_record:
                # Then create
                partner_id = self.env['crm.lead'].create(deals_rec)
                # Attach name
                if deals_rec.get('pd_deals_id'):
                    parent_id = self.get_odoo_partner_id(deals_rec.get('pd_deals_id'))
                    # if parent_id:
                    # partner_id.write({
                    # 	'parent_id': parent_id
                    # })

            else:
                # Update the record
                # parent_id = self.get_odoo_partner_id(deals_rec.get('pd_parent_deals_id'))

                existing_record.write(deals_rec)

    def import_activities(self):
        '''
        This function will import activities from pipedrive app
        :return: activity data
        '''
        # self.check_credentials()
        _logger.info("*****IMPORT ACTIVITIES****")
        activity_data = self.pipeline_caller("activities")
        activity_data_lst = []
        mark_done = False
        if activity_data.get('data'):
            for activity in activity_data.get('data'):
                deal_search = self.env['crm.lead'].search([('name', '=', activity.get('deal_title'))])
                if deal_search:
                    activity_data_dict = {}

                    # if activity.get('done') == True:# this activity is done

                    if activity.get('id'):
                        activity_data_dict['pd_activity_id'] = activity.get('id')

                    if activity.get('type'):
                        if activity.get('type') in ['call', 'Call']:
                            # Map with Existing Call activity
                            call_activity_id = self.env.ref('mail.mail_activity_data_call')
                            activity_data_dict['activity_type_id'] = call_activity_id.id

                        if activity.get('type') in ['meeting', 'Meeting']:
                            # Map with Existing Meeting activity
                            meeting_activity_id = self.env.ref('mail.mail_activity_data_meeting')
                            activity_data_dict['activity_type_id'] = meeting_activity_id.id

                        if activity.get('type') in ['email', 'Email']:
                            # Map with Existing Email activity
                            mail_activity_id = self.env.ref('mail.mail_activity_data_email')
                            activity_data_dict['activity_type_id'] = mail_activity_id.id

                        if activity.get('type') in ['task', 'Task']:
                            # Map with Existing Task activity
                            mail_task_id = self.env.ref('mail.mail_activity_data_todo')
                            activity_data_dict['activity_type_id'] = mail_task_id.id

                    if activity.get('due_date'):
                        activity_data_dict['date_deadline'] = activity.get('due_date')
                    if activity.get('subject'):
                        activity_data_dict['summary'] = activity.get('subject')

                        # Search for user
                        search_user = self.env['res.users'].search([])
                    # activity_data_dict['user_id'] = search_user.id

                    # In pipedrive if we delete a record it still comes in API, but its id is False
                    if not activity.get('deal_id'):
                        _logger.info("WE SKIP THIS RECORD")
                        continue

                    if activity.get('deal_id'):
                        # search for deal_id
                        search_deal_id = self.env['crm.lead'].search([('pd_deals_id', '=', activity.get('deal_id'))])
                        # if not search_deal_id :
                        activity_data_dict['res_id'] = search_deal_id.id

                        # search for model_id
                        search_res_model = self.env['ir.model'].search([('model', '=', 'crm.lead')])
                        activity_data_dict['res_model_id'] = search_res_model.id

                    if activity_data_dict:
                        activity_data_lst.append(activity_data_dict)

        # _logger.info("***************LIST IS*************{}".format(activity_data_lst))

        for activity_rec in activity_data_lst:
            if not activity_rec.get('res_id'):
                continue
            existing_record = self.env['mail.activity'].search(
                [('pd_activity_id', '=', activity_rec.get('pd_activity_id'))])

            if not existing_record:
                activity_id = self.env['mail.activity'].create(activity_rec)
                if activity_id:
                    activity_id._cr.commit()
                # existing_record.action_feedback()
                # existing_record._action_done()


            else:
                # pass
                # Update the record
                res_act_rec = existing_record.write(activity_rec)
                # existing_record.action_feedback()
                rec_mail = existing_record._action_done()

                # activity_id._cr.commit()

    def import_notes(self):
        '''
        This function returns all the notes from pipedrive to odoo
        :return: notes_data
        '''
        # self.check_credentials()
        _logger.info("*****IMPORT NOTES****")
        notes_data = self.pipeline_caller("notes")
        _logger.info("*****NOTES DATA****{}".format(notes_data))

        notes_data_lst = []

        if notes_data.get('data'):

            for notes in notes_data.get('data'):
                notes_data_dict = {}

                if notes.get('content'):
                    notes_data_dict['body'] = notes.get('content')

                if notes.get('id'):
                    notes_data_dict['pd_notes_id'] = notes.get('id')

                if notes.get('deal_id'):
                    notes_data_dict['pd_deal_id'] = notes.get('deal_id')

                rec = self.env['crm.lead'].search([('pd_deals_id', '=', notes.get('deal_id'))])
                if rec:

                    notes_data_dict['res_id'] = rec.id
                else:
                    _logger.info("record does not exists")

                notes_data_dict['message_type'] = "comment"

                notes_data_dict['model'] = 'crm.lead'

                if notes_data_dict:
                    notes_data_lst.append(notes_data_dict)

                _logger.info("NOTES DATA LIST IS %s:---------------------", notes_data_dict)
                mail_message_obj = self.env['mail.message']
                if notes_data_dict.get('deal_id') and notes_data_dict.get('pd_notes_id'):
                    recs = mail_message_obj.search([('pd_deal_id', '=', notes_data_dict.get('deal_id')),
                                                    ('pd_notes_id', '=', notes_data_dict.get('pd_notes_id'))])

                    if recs:
                        # for notes_rec in notes_data_lst:
                        notes_id = self.env['mail.message'].write(notes_data_dict)



                    else:
                        if notes_data_lst:
                            # for notes_rec in notes_data_lst:
                            #     # self.env['mail.message'].search([]).unlink()
                            #     # notes_rec.unlink()

                            notes_id = mail_message_obj.create(notes_data_dict)
                            if notes_id:
                                notes_id._cr.commit()

    def create_notes(self):
        '''
        THis function will create notes in pipedrive
        :param note_id:
        :return:
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = '{0}notes'
        uri_caller = uri.format(domain)
        _logger.info("******URI CALLER********* {}".format(uri_caller))
        company_id = None
        user_id = self.env['res.users'].search([('active', '=', True)])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:
            # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
            headers = {}
            browse_deals = self.env['crm.lead'].search([])
            # for record in browse_deals:
            browse_notes = self.env['mail.message'].search([])
            for rec in browse_notes:
                # if rec.body:
                for record in browse_deals:

                    payload = {
                        'content': rec.body,
                        'deal_id': record.pd_deals_id

                    }
                    headers['Authorization'] = "Bearer " + company_id.access_token
                    if company_id.access_token:
                        _logger.info("Access token Found")
                    else:
                        raise UserError(_("Access Token not found!!!"))

                    headers['content-type'] = 'application/x-www-form-urlencoded'
                    response = requests.post(url=uri_caller, data=payload, headers=headers, verify=False)
                    data = response.json()
                    _logger.info("**************33 {}".format(data))
                    rec.write({'pd_id': data.get('data').get('id')})

    def update_notes(self, note_id):
        '''
        THis function will update the note in pipedrive
        :param note_id:
        :return: updated data
        '''
        domain = self.env['ir.config_parameter'].sudo().get_param('pragmatic_pipedrive_connector.pd_api_url')
        uri = "{0}notes/%s" % (note_id)
        uri_caller = uri.format(domain)
        browse_note = self.env['mail.message'].search([])
        for rec in browse_note:
            if rec.body:
                company_id = None
                user_id = self.env['res.users'].search([('active', '=', True)])
                for company_id in user_id.company_ids:
                    if company_id.access_token and company_id.refresh_token:
                        company_id = company_id
                if company_id:
                    # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
                    headers = {}
                    payload = {
                        'id': note_id,
                        'content': rec.body
                    }
                    headers['Authorization'] = "Bearer " + company_id.access_token
                    headers['content-type'] = 'application/x-www-form-urlencoded'
                    headers['Accept'] = 'application/json'
                    if company_id.access_token:
                        _logger.info("Access token Found")
                    else:
                        raise UserError(_("Access Token not found!!!"))
                    response = requests.put(url=uri_caller, data=payload, headers=headers, verify=False)
                    data = response.json()
                    _logger.info("**************44 {}".format(data))

    # fields
    access_token = fields.Char("Access Token")
    refresh_token = fields.Char("Refresh Token")
    token_type = fields.Char("Token Type")
    expires_in = fields.Char("Expires")
    scope = fields.Char("Scope")
    client_id = fields.Char("Client ID", required=False)
    client_secret = fields.Char("Client Secret", required=False)
    redirect_uri = fields.Char("Redirect URI", required=False)
    caller = fields.Char("Caller")

    def sanitize_pipedrive_fields(self, field_value):
        '''
            This function will remove the spaces from input
        '''
        return field_value.strip()

    def authenticate(self):
        '''
            This function will sanitize and validate the data for pipedrive
            and redirects to pipedrive authorize flow for getting started with Oauth2.0 flow
        '''

        pd_authorize_url = self.env['ir.config_parameter'].sudo().get_param(
            'pragmatic_pipedrive_connector.pd_authorize_url')
        if not pd_authorize_url:
            raise UserError(_("Please set authorize URL from General Settings"))
        if not self.client_id:
            raise UserError(_("Please enter Client ID"))
        if not self.redirect_uri:
            raise UserError(_("Please enter redirect Uri"))

        client_id = self.sanitize_pipedrive_fields(self.client_id)
        redirect_uri = self.sanitize_pipedrive_fields(self.redirect_uri)

        return {
            'type': 'ir.actions.act_url',
            'url': pd_authorize_url + "?client_id={}&redirect_uri={}".format(client_id, redirect_uri),
            'target': 'new'
        }

    def refresh(self):
        '''
            This function will provide access to pipedrive using refresh token
            once access token has been expired.
        '''

        # company_id = http.request.env['res.users'].sudo().search([('id', '=', http.request.uid)]).company_id
        company_id = None
        user_id = self.env['res.users'].search([('active', '=', True)])
        for company_id in user_id.company_ids:
            if company_id.access_token and company_id.refresh_token:
                company_id = company_id
        if company_id:
            client_id = company_id.client_id
            client_secret = company_id.client_secret

            pd_token_url = self.env['ir.config_parameter'].sudo().get_param(
                'pragmatic_pipedrive_connector.pd_token_url')
            if not pd_token_url:
                raise UserError(_("Please set Token URL from General Settings"))
            headers = {}
            combined_key = str(client_id) + ":" + str(client_secret)
            encoded_key = base64.b64encode(bytes(combined_key, 'utf-8'))
            headers['Authorization'] = "Basic " + encoded_key.decode('utf-8')
            headers['content-type'] = 'application/x-www-form-urlencoded'
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': company_id.refresh_token,
            }
            refresh_token_req = requests.post(pd_token_url, data=payload, headers=headers, verify=False)
            if refresh_token_req:
                refresh_token_response = json.loads(refresh_token_req.text)
                _logger.info("REFRESH TOKEN RESPONSE FROM CONTROLLER IS {}".format(refresh_token_response))
                if refresh_token_response.get('refresh_token'):
                    company_id.refresh_token = refresh_token_response.get('refresh_token')
                    company_id.access_token = refresh_token_response.get('access_token')


class mail_followers(models.Model):
    _inherit = 'mail.followers'

    def create(self, vals):
        if 'res_model' in vals and 'partner_id' in vals and 'res_id' in vals:
            exist = self.search([('res_model', '=', vals['res_model']),
                                 ('partner_id', '=', vals['partner_id']),
                                 ('res_id', '=', vals['res_id'])])
            if exist:
                return exist
            else:
                return super(mail_followers, self).create(vals)
