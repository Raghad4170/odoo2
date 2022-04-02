# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website.controllers.main import Website
import numpy as np
import re

class CustomerPortal(CustomerPortal):
     
    # ------------------------------------------------------------
    # My commitment
    # ------------------------------------------------------------
    def _commitment_get_page_view_values(self, commitment, access_token, **kwargs):
        values = {
            'page_name': 'برنامج الالتزام',
            'commitment': commitment,
        }
        return self._get_page_view_values(commitment, access_token, values, 'my_commitments_history', False, **kwargs)

    @http.route(['/my/commitments', '/my/commitments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_commitments(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        commitment = request.env['company.commitments']
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
        # commitment count
        commitment_count = commitment.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/commitments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=commitment_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        commitments = commitment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_commitments_history'] = commitments.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'commitments': commitments,
            'page_name': 'commitment',
            'default_url': '/my/commitments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("commitments.portal_my_commitments", values)

    @http.route(['/my/commitment/<int:commitment_id>'], type='http', auth="public", website=True)
    def portal_my_commitment(self, commitment_id=None, access_token=None, **kw):
        try:
            commitment_sudo = self._document_check_access('company.commitments', commitment_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._commitment_get_page_view_values(commitment_sudo, access_token, **kw)
        return request.render("commitments.portal_my_commitment", values)



    @http.route(['/commitments_print/<int:commitment_id>'], type='http', auth="public", website=True)
    def print_commitment_xml(self, commitment_id=None, report_type=None, access_token=None, message=False, download=False, **kw):
        commitments_sudo = self._document_check_access('company.commitments', commitment_id, access_token=access_token)
        if report_type in ('html', 'pdf', 'text'):
            template = 'commitments.action_report_commitments'
            return self._show_report(model=commitments_sudo, report_type=report_type, report_ref=template, download=download)

     
    @http.route('/commitments_submit_two', type='http',csrf=False, auth='public', website=True)       
    def get_total_page_info(self,commitment_id):
        commitment_obj = request.env['company.commitments']
        commitment_line_obj = request.env['commitments.line']
        commitment_data_obj = commitment_obj.browse(int(commitment_id))
        page_no=0
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.display_type == 'line_section':
                page_no+=1
        return page_no

    
    @http.route('/commitments_submit/<list_commitment>/<int:commitment_id>/<int:page_no>',csrf=False, type='http', auth='public', website=True)
    def commitments_submit(self,list_commitment,commitment_id,page_no, **kwargs):
        commitment_obj = request.env['company.commitments']
        commitment_line_obj = request.env['commitments.line']
        commitment_list=[]
        main_commitment_id=int(commitment_id)

        commitment_data_obj = commitment_obj.browse(int(commitment_id))
        total_page_no=self.get_total_page_info(commitment_id)
        page_no+=1
        request.session["page_no"]=page_no

        continue_list=[]
        for commitment_id in commitment_data_obj.commitments_line:
            continue_list.append(commitment_id.id)

        for rec_dic in kwargs:
            rec_dic_agr=rec_dic
            if rec_dic.find('_container')!=-1:

                rec_dic=rec_dic.split('ans_')[1]
                new_rec=rec_dic.split('_container')[0]
                rec_dic=int(new_rec)
                text_box=True

            else:
                text_box=False
                if rec_dic.find('ans_')!=-1:
                    rec_dic=int(rec_dic.split('ans_')[1])

                else:
                    rec_dic=int(rec_dic)


            commitment_data = commitment_line_obj.browse(int(rec_dic))
            if text_box:
                if kwargs[rec_dic_agr]:
                    commitment_data.write({'name':kwargs[rec_dic_agr],'is_answered':True})
            else:
                if kwargs[rec_dic_agr] == 'ملتزم':
                    commitment_data.write({'commitment_type':kwargs[rec_dic_agr],'name':' ','is_answered':True})
            
                else:
                    commitment_data.write({'commitment_type':kwargs[rec_dic_agr],'is_answered':True})

            if commitment_data.commitment_type == 'ملتزم':
                    commitment_data.write({'name':' '})


        cnt=0
        first_blog=False
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.id not in request.session['commitment_list']:
                if commitment_id.display_type != 'line_section':

                    if cnt == 0:
                        first_blog=commitment_id.questions_id.organization_type.system_id.name
                    commitment_list.append(commitment_id.id)
                if commitment_id.display_type == 'line_section':
                    
                    cnt+=1

                    if cnt == 2:
                        break
                    commitment_list.append(commitment_id.id)

        if not len(commitment_list):
             return request.redirect('/my/commitments')
             
        request.session['commitment_list'] = commitment_list + list(request.session['commitment_list'])
        #get next commitment for button
        next_commitment_list=[]
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.id not in request.session['commitment_list']:
                if commitment_id.display_type != 'line_section':

                    next_commitment_list.append(commitment_id.id)

        if not len(next_commitment_list):
                submit_button = True
        else:
                submit_button=False

        current=''
        commitment_list_data=[]
        for commitment_id in commitment_list :
            commitment_data = commitment_line_obj.browse(int(commitment_id))
            if commitment_data.display_type == 'line_section':

                if commitment_data.name:
                    current=commitment_data.name
            commitment_list_data.append(commitment_data)


        commitment_division=''
        all_ids=[]
        cnt=0
        nlist=[]
        mlist=''
        a = {}
        var =False
        filled=False
        commitment_list_div=[]
        cname=''
        new_list=[]
        nadd=0
        madd=0
        for m in re.findall('\d+', list_commitment ):
            new_list.append(int(m))
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.display_type != 'line_section':
                cnt+=1
                nlist.append(commitment_id.id)
                mlist+=str(commitment_id.id)+','
                  
            if commitment_id.display_type == 'line_section':
                cnt+=1

                unanswered=''
                if len(nlist):
                    unanswered='style='''
                    for res in nlist:
                            re_data=commitment_line_obj.browse(res)

                            if not re_data.is_answered:
                                unanswered='style=color:#0b5394;'

                    if nadd==1:
                         unanswered='style=color:#000000;'
                         nadd+=1
                    m="<a "+unanswered+" tabindex='1' href=/commitments_submit_division/"+mlist+"/"+str(main_commitment_id)+"/"+pname.replace(' ','_')+">"
                    commitment_division+=m+pname+"</a>/"
                    if current == commitment_id.name:
                       nadd+=1
                       unanswered='style='''

                    if len(nlist):
                        nlist=[]
                        mlist=''
                      
                pname=commitment_id.name
                cname=commitment_id.name
        if len(nlist):
                unanswered='style='''
                for res in nlist:
                        re_data=commitment_line_obj.browse(res)
                        if not re_data.is_answered:
                            unanswered='style=color:#0b5394;'
                if current == cname:
                        madd+=1
                if madd==1:
                     unanswered='style=color:#000000;'
                m="<a  "+unanswered+"   tabindex='1' href=/commitments_submit_division/"+mlist+"/"+str(main_commitment_id)+"/"+cname.replace(' ','_')+">"
   
                if cname:
                     commitment_division+=m+cname+"</a>"
        return request.render('commitments.question_container_commitments_main',{'commitment_division':"<div class='lin'>"+commitment_division+"</div>",'first_blog':first_blog,'page_no':page_no,'total_page_no':total_page_no,'submit_button':submit_button,'commitment_list':commitment_list,'commitment':commitment_data_obj,'questions':commitment_list_data})
    
    
    
    @http.route('/commitments_submit_division/<string:commitment_list>/<int:commitment_id>/<string:div_name>', type='http', auth='public', website=True)
    def commitment_submit_div(self,commitment_list, commitment_id,div_name,**post):
        new_list=[]
        for m in commitment_list.split(',')[:-1]:
           if m not in [',',']','[']:
                new_list.append(int(m))
            
        commitment_obj = request.env['company.commitments']
        commitment_line_obj = request.env['commitments.line']
        main_commitment_id=int(commitment_id)
        commitment_data_obj = commitment_obj.browse(int(commitment_id))
        total_page_no=self.get_total_page_info(commitment_id)

        commitment_division=''
        all_ids=[]
        cnt=0
        nlist=[]
        mlist=''
        a = {}
        var =False
        filled=False
        commitment_list_div=[]
        cname=''
        style=''
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.display_type != 'line_section':
                cnt+=1
                nlist.append(commitment_id.id)
                mlist+=str(commitment_id.id)+','
                  
            if commitment_id.display_type == 'line_section':
                cnt+=1

                unanswered=''
                if len(nlist):
                    style='style='''
                    for re in nlist:
                            re_data=commitment_line_obj.browse(re)
                            if not re_data.is_answered:
                                style='style=color:#0b5394;'
                       

                    if div_name.replace('_',' ')==pname:
                        style='style=color:#000000;'
                    m="<a "+style+"  tabindex='1'  href=/commitments_submit_division/"+mlist+"/"+str(main_commitment_id)+"/"+pname.replace(' ','_')+">"
                    commitment_division+=m+pname+"</a>/"
                    if len(nlist):
                        nlist=[]
                        mlist=''
                 
                pname=commitment_id.name
                cname=commitment_id.name
        if len(nlist):
                style='style='''
                for re in nlist:
                        re_data=commitment_line_obj.browse(re)

                        if not re_data.is_answered:
                            style='style=color:#0b5394;'
                if div_name.replace('_',' ')==cname:
                        style='style=color:#000000;'
                m="<a "+style+"  tabindex='1' href=/commitments_submit_division/"+mlist+"/"+str(main_commitment_id)+"/"+cname.replace(' ','_')+">"
                if cname:
                     commitment_division+=m+cname+"</a>"


        commitment_list_data=[]
        for cid in new_list :
            commitment_data = commitment_line_obj.browse(int(cid))

            commitment_list_data.append(commitment_data)

        request.session["page_no"]=request.session["page_no"]
        return request.render('commitments.question_container_commitments_main',{'commitment_division':"<div class='lin'>"+commitment_division+"</div>",'first_blog':False,'total_page_no':total_page_no,'page_no':-1,'submit_button':False,'commitment_list':commitment_list,'commitment':commitment_data_obj,'questions':commitment_list_data})




    @http.route('/company_commitments/<int:commitment_id>', type='http', auth='public', website=True)
    def commitment_test(self,commitment_id, **post):
        commitment_obj = request.env['company.commitments']
        commitment_line_obj = request.env['commitments.line']
        main_commitment=int(commitment_id)
        commitment_data_obj = commitment_obj.browse(int(commitment_id))
        total_page_no=self.get_total_page_info(commitment_id)
        commitment_division=''
        all_ids=[]
        cnt=0
        ncnt=0
        nlist=[]
        mlist=''
        a = {}
        var =False
        filled=False
        commitment_list_div=[]
        cname=''
        index=0
        unanswered='style='''
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.display_type != 'line_section':
                cnt+=1
                nlist.append(commitment_id.id)
                mlist+=str(commitment_id.id)+','
            if commitment_id.display_type == 'line_section':
                if len(nlist):
                    unanswered='style='''
                    for re in nlist:
                            re_data=commitment_line_obj.browse(re)
                            if not re_data.is_answered:
                                unanswered='style=color:#0b5394;'                       
                    if ncnt ==0:
                         unanswered='style=color:#000000;'
                    m="<a "+unanswered+" tabindex='1' href=/commitments_submit_division/"+mlist+'/'+str(main_commitment)+"/"+pname.replace(' ','_')+">"
                    commitment_division+=m+pname+"</a>/"
                    ncnt+=1
                    if len(nlist):
                        nlist=[]
                        mlist=''
                        
                pname=commitment_id.name
                cname=commitment_id.name
        if len(nlist):
                unanswered='style='''
                for re in nlist:
                        re_data=commitment_line_obj.browse(re)
                        if not re_data.is_answered:
                            unanswered='style=color:#0b5394;'
                m="<a   "+unanswered+"  tabindex='1' href=/commitments_submit_division/"+mlist+'/'+str(main_commitment)+"/"+cname.replace(' ','_')+">"

                commitment_division+=m+cname+"</a>"
        commitment_list=[]
        cnt=0
        for commitment_id in commitment_data_obj.commitments_line:
            if commitment_id.display_type != 'line_section':
                commitment_list.append(commitment_id.id)
               
            if commitment_id.display_type == 'line_section':
                cnt+=1
                if cnt == 2:
                    break
                commitment_list.append(commitment_id.id)
           
        request.session['commitment_list'] = commitment_list
        commitment_list_data=[]
        for commitment_id in commitment_list :
            commitment_data = commitment_line_obj.browse(int(commitment_id))
            commitment_list_data.append(commitment_data)

        request.session["page_no"]=0
        return request.render('commitments.question_container_commitments_main',{'commitment_division':"<div class='lin'>"+commitment_division+"</div>",'first_blog':False,'total_page_no':total_page_no,'page_no':0,'submit_button':False,'commitment_list':commitment_list,'commitment':commitment_data_obj,'questions':commitment_list_data})

