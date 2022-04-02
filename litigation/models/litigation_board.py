import ast
from datetime import timedelta, datetime
from random import randint
import uuid
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning
from odoo.tools.misc import format_date, get_lang
from odoo.osv.expression import OR
from werkzeug import urls
import json
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime,date



class LitigationBoard(models.Model):
    _name = 'litigation.board'
    _description = 'لوحة معلومات القضايا'

    name = fields.Char("Name")
    color = fields.Integer('Color Index')
    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    nearest_date = fields.Datetime(compute='_nearest_date')
    nearest_date_one = fields.Datetime(compute='_nearest_date')
    nearest_date_two = fields.Datetime(compute='_nearest_date')
    nearest_date_name = fields.Char(compute='_nearest_date')
    nearest_date_one_name = fields.Char(compute='_nearest_date')
    nearest_date_two_name = fields.Char(compute='_nearest_date')
    no_count = fields.Integer(compute='_total_count')
    group_ids = fields.Many2many('res.groups', 'group_board_rel', string='Group ID')

    def _total_count(self):
        for cnt in self:
            data = []
            project_task_obj =self.env['project.task']
            litigation_obj =self.env['litigation.litigation']
            attorney_obj =self.env['attorney.attorney']
            consulting_obj =self.env['consulting.consulting']
            contra_consulting_obj = self.env['contractconsulting.contractconsulting']
            litigaton_report_obj = self.env['litigation.report']
            keyword=''
            User = self.env.user
            cnt.no_count=0
            today = fields.Datetime.now(self)

            if cnt.name=="المشاريع":
                new_lit_ids=self.env['project.project'].search(['|',('user_id','=',self.env.user.id),('allowed_internal_user_ids','in',[self.env.user.id])]).ids
                User = self.env.user
                if User.user_has_groups('litigation.group_law_lawyer_manager'):
                        new_lit_ids=self.env['project.project'].search([]).ids
                cnt.no_count = len(new_lit_ids)
                
            if cnt.name == 'تقارير الجلسات':
                if User.user_has_groups('litigation.group_law_lawyer_manager'):
                
                    consulting_ids=len(litigaton_report_obj.sudo().search([]))
                    consulting_ids_one=0

                else:

                    consulting_ids=len(litigaton_report_obj.sudo().search([('user_id','=',self.env.user.id)]))
                    consulting_ids_one=[]
                    if  consulting_ids  == 0:
                        consulting_ids_one=len(litigaton_report_obj.sudo().search([('helper_ids','in',[self.env.user.id])]))
                    if isinstance(consulting_ids_one, list):
                        consulting_ids_one=0
                cnt.no_count=int(consulting_ids+consulting_ids_one)
          
            if cnt.name == 'استشارات العقود':

                if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    consulting_ids=len(contra_consulting_obj.sudo().search([]))
                    consulting_ids_one=0
                else:
                    consulting_ids=len(contra_consulting_obj.sudo().search([('user_id','=',self.env.user.id)]))
                    consulting_ids_one=[]
                    if  consulting_ids  == 0:
                            consulting_ids_one=len(contra_consulting_obj.sudo().search([('helper_ids','in',[self.env.user.id])]))
                
                    if isinstance(consulting_ids_one, list):
                        consulting_ids_one=0
                cnt.no_count=int(consulting_ids+consulting_ids_one)


            if cnt.name == 'الاستشارات':

                if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    consulting_ids=len(consulting_obj.sudo().search([]))
                    consulting_ids_one=0
                else:
                    consulting_ids=len(consulting_obj.sudo().search([('user_id','=',self.env.user.id)]))
                    consulting_ids_one=[]
                    if  consulting_ids  == 0:
                        consulting_ids_one=len(consulting_obj.sudo().search([('helper_ids','in',[self.env.user.id])]))
                    if isinstance(consulting_ids_one, list):
                        consulting_ids_one=0
                cnt.no_count=int(consulting_ids+consulting_ids_one)

            
            if cnt.name == 'الوكالات':
                new_att_ids=len(attorney_obj.search([]))
                cnt.no_count=int(new_att_ids)

              
            if cnt.name == 'القضايا':
                if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    new_lit_ids=len(litigation_obj.sudo().search([]))
                    consulting_ids_one=0
                else:
                    new_lit_ids=len(litigation_obj.sudo().search([('user_id','=',self.env.user.id)]))
                    consulting_ids_one=[]
                    if  new_lit_ids  == 0:
                        consulting_ids_one=len(litigation_obj.sudo().search([('helper_ids','in',[self.env.user.id])]))
                    if isinstance(consulting_ids_one, list):
                        consulting_ids_one=0
                cnt.no_count=int(new_lit_ids+consulting_ids_one)

          
            if cnt.name == 'المهام':
                new_lit_ids=len(self.env['project.task'].search([('user_ids','=',self.env.user.id)]))
                User = self.env.user
                if User.user_has_groups('litigation.group_law_lawyer_manager'):
                        new_lit_ids=len(self.env['project.task'].search([]).ids)
                cnt.no_count=int(new_lit_ids)
                
            return [{'values': data, 'title': 'test', 'key': keyword, 'is_sample_data':True}]



    def _nearest_date(self):
        litigation_obj=self.env['litigation.litigation']
        test_date_list=[]
        test_name_list=[]
        for rec in self:
            rec.nearest_date = False
            rec.nearest_date_one = False
            rec.nearest_date_two = False
            rec.nearest_date_name = False
            rec.nearest_date_one_name = False
            rec.nearest_date_two_name = False

            if rec.name == 'القضايا':
                if self.env.user.user_has_groups('litigation.group_law_lawyer_manager'):
                    lit_ids = litigation_obj.search([])
                else:
                    lit_ids = litigation_obj.search(['|',('user_id','=',self.env.user.id),('helper_ids','in',[self.env.user.id])])
                for lit in lit_ids:
                    if lit.next_court_date:
                        if lit.next_court_date >= datetime.now():
                             test_date_list.append(lit.next_court_date)
                     
                if len(test_date_list):
                            
                    test_date = datetime.now()

                    res = min(test_date_list, key=lambda sub: abs(sub - test_date))
                    res_name = litigation_obj.search([('next_court_date','=', res)], limit=1).name

                    print("Nearest date from list : " + str(res.date()))
                    rec.nearest_date = res
                    rec.nearest_date_name = res_name + ": "
                    test_date_list.remove(res)

                if len(test_date_list):

                    print("The original list is : " + str(test_date_list))                    
                    test_date = datetime.now()
                    print("The test_date : " + str(test_date))

                    res = min(test_date_list, key=lambda sub: abs(sub - test_date))
                    res_name = litigation_obj.search([('next_court_date','=', res)], order='next_court_date desc', limit=1).name

                    print("Nearest date from list : " + str(res.date()))
                    rec.nearest_date_one = res
                    rec.nearest_date_one_name = res_name + ": "
                    test_date_list.remove(res)

                if len(test_date_list):

                            
                    print("The original list is : " + str(test_date_list))
                    
                    test_date = datetime.now()
                    print("The test_date : " + str(test_date))

                    res = min(test_date_list, key=lambda sub: abs(sub - test_date))
                    res_name = litigation_obj.search([('next_court_date','=', res)], order='next_court_date desc', limit=1).name

                    print("Nearest date from list : =======================" + str(res.date()))
                    rec.nearest_date_two = res
                    rec.nearest_date_two_name = res_name + ": "
                    test_date_list.remove(res)

                 




    def _kanban_dashboard_graph(self):
        for rec in self:
            rec.kanban_dashboard_graph = json.dumps(rec.get_bar_graph_datas())

                
                
    def get_bar_graph_datas(self):
        data = []
        project_obj =self.env['project.project']
        project_task_obj =self.env['project.task']
        litigation_obj =self.env['litigation.litigation']
        attorney_obj =self.env['attorney.attorney']
        consulting_obj =self.env['consulting.consulting']
        contra_consulting_obj = self.env['contractconsulting.contractconsulting']
        litigaton_report_obj = self.env['litigation.report']
        keyword = 'عددها'
        User = self.env.user
        today = fields.Datetime.now(self)        
        if self.name == 'تقارير الجلسات':
            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','close')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(litigaton_report_obj.search([('state','=','close'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=len(litigaton_report_obj.search([('state','=','close'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مغلقة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='future'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','Approve')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(litigaton_report_obj.search([('state','=','Approve'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(litigaton_report_obj.search([('state','=','Approve'),('helper_ids','in',[self.env.user.id])]))
            if isinstance(consulting_ids_one, list):
                consulting_ids_one=0
            m['label']='لدى العميل'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='لدى العميل'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','suspended')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','suspended'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(litigaton_report_obj.sudo().search([('state','=','suspended'),('helper_ids','in',[self.env.user.id])]))
            if isinstance(consulting_ids_one, list):
                consulting_ids_one=0
            m['label']='معلقة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','Refuse')]))
                consulting_ids_one=0
            else:

                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','Refuse'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(litigaton_report_obj.search([('state','=','Refuse'),('helper_ids','in',[self.env.user.id])]))
            
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مرفوضة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','confirm')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','confirm'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(litigaton_report_obj.sudo().search([('state','=','confirm'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='بإنتظار موافقة المدير'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='بإنتظار موافقة المدير'
            data.append(m)
            
            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','draft')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(litigaton_report_obj.sudo().search([('state','=','draft'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(litigaton_report_obj.sudo().search([('state','=','draft'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مسودة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='مسودة'
            data.append(m)


        if self.name == 'استشارات العقود':
            
            m={}
            if User.user_has_groups('litigation.group_law_contractconsulting_manager'):
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','close')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','close'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(contra_consulting_obj.sudo().search([('state','=','close'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مغلقة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='future'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_contractconsulting_manager'):
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','Approve')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','Approve'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(contra_consulting_obj.sudo().search([('state','=','Approve'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='لدى العميل'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='لدى العميل'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_contractconsulting_manager'):
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','suspended')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','suspended'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(contra_consulting_obj.sudo().search([('state','=','suspended'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='معلقة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_contractconsulting_manager'):
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','Refuse')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','Refuse'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(contra_consulting_obj.sudo().search([('state','=','Refuse'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مرفوضة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)
            
            m={}
            if User.user_has_groups('litigation.group_law_contractconsulting_manager'):
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','confirm')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','confirm'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(contra_consulting_obj.sudo().search([('state','=','confirm'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='بإنتظار موافقة المدير'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='بإنتظار موافقة المدير'
            data.append(m)
            
            m={}
            if User.user_has_groups('litigation.group_law_contractconsulting_manager'):
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','draft')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(contra_consulting_obj.sudo().search([('state','=','draft'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                        consulting_ids_one=len(contra_consulting_obj.sudo().search([('state','=','draft'),('helper_ids','in',[self.env.user.id])]))
            
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مسودة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='مسودة'
            data.append(m)


        if self.name == 'الاستشارات':            
            m={}
            if User.user_has_groups('litigation.group_law_consultant_manager'):
                consulting_ids=len(consulting_obj.sudo().search([('state','=','close')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(consulting_obj.sudo().search([('state','=','close'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(consulting_obj.sudo().search([('state','=','close'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مغلقة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='future'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_consultant_manager'):
                consulting_ids=len(consulting_obj.sudo().search([('state','=','Approve')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(consulting_obj.search([('state','=','Approve'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(consulting_obj.sudo().search([('state','=','Approve'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='لدى العميل'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='لدى العميل'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_consultant_manager'):
                consulting_ids=len(consulting_obj.sudo().search([('state','=','suspended')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(consulting_obj.search([('state','=','suspended'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(consulting_obj.sudo().search([('state','=','suspended'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='معلقة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)
            
            m={}
            if User.user_has_groups('litigation.group_law_consultant_manager'):
                consulting_ids=len(consulting_obj.sudo().search([('state','=','Refuse')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(consulting_obj.search([('state','=','Refuse'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(consulting_obj.sudo().search([('state','=','Refuse'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مرفوضة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_consultant_manager'):
                consulting_ids=len(consulting_obj.sudo().search([('state','=','confirm')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(consulting_obj.search([('state','=','confirm'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(consulting_obj.sudo().search([('state','=','confirm'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='بإنتظار موافقة المدير'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='بإنتظار موافقة المدير'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_consultant_manager'):
                consulting_ids=len(consulting_obj.sudo().search([('state','=','draft')]))
                consulting_ids_one=0
            else:
                consulting_ids=len(consulting_obj.sudo().search([('state','=','draft'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  consulting_ids  == 0:
                    consulting_ids_one=len(consulting_obj.sudo().search([('state','=','draft'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مسودة'
            m['value']=int(consulting_ids+consulting_ids_one)
            m['type']='مسودة'
            data.append(m)


        if self.name == 'الوكالات':
            m={}
            new_att_ids=len(attorney_obj.search([('expiration','=','منتهية')]))
            m['label']='منتهية'
            m['value']=int(new_att_ids)
            m['type']='past'
            data.append(m)
            
            m={}
            new_att_ids=len(attorney_obj.search([('expiration','=','قاربت على الإنتهاء')]))
            m['label']='قاربت على الإنتهاء'
            m['value']=int(new_att_ids)
            m['type']='past'
            data.append(m)

            m={}
            new_att_ids=len(attorney_obj.search([('expiration','=','سارية')]))
            m['label']='سارية'
            m['value']=int(new_att_ids)
            m['type']='future'
            data.append(m)

            
            m={}
            new_att_ids=len(attorney_obj.search([('expiration','=','جديدة')]))
            m['label']='مسودة'
            m['value']=int(new_att_ids)
            m['type']='مسودة'
            data.append(m)
            

        if self.name == 'القضايا':
            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','close')]))
                consulting_ids_one=0
            else:
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','close'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  new_lit_ids  == 0:
                    consulting_ids_one=len(litigation_obj.sudo().search([('state','=','close'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']= 'مغلقة'
            m['value']=int(new_lit_ids+consulting_ids_one)
            m['type']='future'
            data.append(m)


            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','Approve')]))
                consulting_ids_one=0
            else:
                new_lit_ids=len(litigation_obj.search([('state','=','Approve'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  new_lit_ids  == 0:
                    consulting_ids_one=len(litigation_obj.sudo().search([('state','=','Approve'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m={}

            m['label']= 'لدى العميل'
            m['value']=int(new_lit_ids+consulting_ids_one)
            m['type']= 'لدى العميل'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','suspended')]))
                consulting_ids_one=0
            else:

                new_lit_ids=len(litigation_obj.search([('state','=','suspended'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  new_lit_ids  == 0:
                    consulting_ids_one=len(litigation_obj.sudo().search([('state','=','suspended'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0

            m['label']= 'معلقة'
            m['value']=int(new_lit_ids+consulting_ids_one)
            m['type']= 'past'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','Refuse')]))
                consulting_ids_one=0
            else:
                new_lit_ids=len(litigation_obj.search([('state','=','Refuse'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  new_lit_ids  == 0:
                    consulting_ids_one=len(litigation_obj.sudo().search([('state','=','Refuse'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']= 'مرفوضة'
            m['value']=int(new_lit_ids+consulting_ids_one)
            m['type']='past'
            data.append(m)

            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','confirm')]))
                consulting_ids_one=0
            else:
                new_lit_ids=len(litigation_obj.search([('state','=','confirm'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  new_lit_ids  == 0:
                    consulting_ids_one=len(litigation_obj.sudo().search([('state','=','confirm'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0

            m['label']='بإنتظار موافقة المدير'
            m['value']=int(new_lit_ids+consulting_ids_one)
            m['type']='بإنتظار موافقة المدير'
            data.append(m)

            
            m={}
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','draft')]))
                consulting_ids_one=0
            else:
                new_lit_ids=len(litigation_obj.sudo().search([('state','=','draft'),('user_id','=',self.env.user.id)]))
                consulting_ids_one=[]
                if  new_lit_ids  == 0:
                    consulting_ids_one=len(litigation_obj.sudo().search([('state','=','draft'),('helper_ids','in',[self.env.user.id])]))
                if isinstance(consulting_ids_one, list):
                    consulting_ids_one=0
            m['label']='مسودة'
            m['value']=int(new_lit_ids+consulting_ids_one)
            m['type']='مسودة'
            data.append(m)
            
        if self.name == 'المهام':
            
            m={}
            new_task_ids=len(project_task_obj.search([('state_id','=','منتهية'),('user_ids','=',self.env.user.id)]))

            if User.user_has_groups('project.group_project_manager'):
                new_task_ids=len(project_task_obj.sudo().search([('state_id','=','منتهية')]))
            m['label']='منتهية'
            m['value']=int(new_task_ids)
            m['type']='future'
            data.append(m)

            
            m={}

            new_task_ids=len(project_task_obj.search([('state_id','=','قيد التنفيذ'),('user_ids','=',self.env.user.id)]))

            if User.user_has_groups('project.group_project_manager'):
                new_task_ids=len(project_task_obj.sudo().search([('state_id','=','قيد التنفيذ')]))
            m['label']='قيد التنفيذ'
            m['value']=int(new_task_ids)
            m['type']='past'
            data.append(m)


            m={}

            new_task_ids=len(project_task_obj.search([('state_id','=','جديدة'),('user_ids','=',self.env.user.id)]))
            
            if User.user_has_groups('project.group_project_manager'):
                new_task_ids=len(project_task_obj.sudo().search([('state_id','=','جديدة')]))

            m['label']='جديدة'
            m['value']=int(new_task_ids)
            m['type']='جديدة'
            data.append(m)
            
            

        if self.name == 'المشاريع':
            
            m={}
            new_project_ids=len(project_obj.search([('project_type','=','اخرى'),('allowed_internal_user_ids','=',self.env.user.id)]))

            if User.user_has_groups('project.group_project_manager'):
                new_tasknew_project_ids_ids=len(project_obj.sudo().search([('project_type','=','اخرى')]))
            m['label']='اخرى'
            m['value']=int(new_project_ids)
            m['type']='اخرى'
            data.append(m)

            
            m={}

            new_project_ids=len(project_obj.search([('project_type','=','عقود'),('allowed_internal_user_ids','=',self.env.user.id)]))

            if User.user_has_groups('project.group_project_manager'):
                new_project_ids=len(project_obj.sudo().search([('project_type','=','عقود')]))
            m['label']='عقود'
            m['value']=int(new_project_ids)
            m['type']='عقود'
            data.append(m)


            m={}

            new_project_ids=len(project_obj.search([('project_type','=','استشارة'),('allowed_internal_user_ids','=',self.env.user.id)]))
            
            if User.user_has_groups('project.group_project_manager'):
                new_project_ids=len(project_obj.sudo().search([('project_type','=','استشارة')]))

            m['label']='استشارة'
            m['value']=int(new_project_ids)
            m['type']='استشارة'
            data.append(m)

            
            m={}

            new_project_ids=len(project_obj.search([('project_type','=','قضية'),('allowed_internal_user_ids','=',self.env.user.id)]))
            
            if User.user_has_groups('project.group_project_manager'):
                new_project_ids=len(project_obj.sudo().search([('project_type','=','قضية')]))

            m['label']='قضية'
            m['value']=int(new_project_ids)
            m['type']='قضية'
            data.append(m)

        return [{'values': data, 'title': 'test', 'key': keyword, 'is_sample_data':True}]

    def open_nearest_date_record_one(self):
        litigation_obj=self.env['litigation.litigation']
        if self.nearest_date_one:
            lit_ids=litigation_obj.search([('next_court_date','=',self.nearest_date_one)]).ids
            logging.info("data--lit_ids-----------%s",lit_ids)

            return {
                    'domain': [('id','in',lit_ids)],
                    'name': _('القضايا'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'res_model': 'litigation.litigation',
                    'views': [(False, 'tree'),(False, 'form')]   
                } 
    def open_nearest_date_record_two(self):
        litigation_obj=self.env['litigation.litigation']
        if self.nearest_date_two:
            lit_ids=litigation_obj.search([('next_court_date','=',self.nearest_date_two)]).ids
            logging.info("data--lit_ids-----------%s",lit_ids)

            return {
                    'domain': [('id','in',lit_ids)],
                    'name': _('القضايا'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'res_model': 'litigation.litigation',
                    'views': [(False, 'tree'),(False, 'form')]   
                }    
    def open_nearest_date_record(self):
        litigation_obj=self.env['litigation.litigation']
        if self.nearest_date:
            lit_ids=litigation_obj.search([('next_court_date','=',self.nearest_date)]).ids
            logging.info("data--lit_ids-----------%s",lit_ids)

            return {
                    'domain': [('id','in',lit_ids)],
                    'name': _('القضايا'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree',
                    'res_model': 'litigation.litigation',
                    'views': [(False, 'tree'),(False, 'form')]   
                } 
                     

    def open_action(self):

        if self.name=="المشاريع":
             new_lit_ids=self.env['project.project'].search(['|',('user_id','=',self.env.user.id),('allowed_internal_user_ids','in',[self.env.user.id])]).ids
             User = self.env.user
             if User.user_has_groups('project.group_project_manager'):
                    new_lit_ids=self.env['project.project'].search([]).ids
             return {
                'domain': [('id','in',new_lit_ids)],
                'name': _('المشاريع'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'project.project',
                'views': [(False, 'tree'),(False, 'form')]   
            } 


        if self.name=="المهام":
             new_lit_ids=self.env['project.task'].search([('user_ids','=',self.env.user.id)]).ids
             User = self.env.user
             if User.user_has_groups('project.group_project_manager'):
                    new_lit_ids=self.env['project.task'].search([]).ids
             return {
                'domain': [('id','in',new_lit_ids)],
                'name': _('المهام'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'project.task',
                'views': [(False, 'tree'),(False, 'form')]   
            } 

        if self.name=="القضايا":
             new_lit_ids=self.env['litigation.litigation'].search(['|',('user_id','=',self.env.user.id),('helper_ids','in',[self.env.user.id])]).ids
             User = self.env.user
             if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    new_lit_ids=self.env['litigation.litigation'].search([]).ids

             return {
                'domain': [('id','in',new_lit_ids)],
                'name': _('القضايا'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'litigation.litigation',
                'views': [(False, 'tree'),(False, 'form')]   
            } 


        if self.name=="الوكالات":
             return {
                'name': _('الوكالات'),
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban',
                'res_model': 'attorney.attorney',
                'views': [(False, 'tree'),(False, 'form')]   
            } 


        if self.name=="الاستشارات":
            new_lit_ids=self.env['consulting.consulting'].search(['|',('user_id','=',self.env.user.id),('helper_ids','in',[self.env.user.id])]).ids
            User = self.env.user
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    new_lit_ids=self.env['consulting.consulting'].search([]).ids
            return {
                'domain': [('id','in',new_lit_ids)],

                'name': _('الاستشارات'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'consulting.consulting',
                'views': [(False, 'tree'),(False, 'form')]   
            } 

        if self.name=="تقارير الجلسات":
             new_lit_ids=self.env['litigation.report'].search(['|',('user_id','=',self.env.user.id),('helper_ids','in',[self.env.user.id])]).ids
             User = self.env.user
             if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    new_lit_ids=self.env['litigation.report'].search([]).ids
             return {
                'domain': [('id','in',new_lit_ids)],

                'name': _('تقارير الجلسات'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'litigation.report',
                'views': [(False, 'tree'),(False, 'form')]   
            } 

            

        if self.name=="استشارات العقود":
            new_lit_ids=self.env['contractconsulting.contractconsulting'].search(['|',('user_id','=',self.env.user.id),('helper_ids','in',[self.env.user.id])]).ids
            User = self.env.user
            if User.user_has_groups('litigation.group_law_lawyer_manager'):
                    new_lit_ids=self.env['contractconsulting.contractconsulting'].search([]).ids
            return {
                'domain': [('id','in',new_lit_ids)],

                'name': _('استشارات العقود'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'contractconsulting.contractconsulting',
                'views': [(False, 'tree'),(False, 'form')]   
            } 
  
