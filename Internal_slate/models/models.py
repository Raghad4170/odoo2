# Copyright to Mutn

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import uuid
from datetime import timedelta, datetime


class serivce_type(models.Model):
    _name = 'serivce.type'
    _description = 'انواع الخدمات'

    name = fields.Char(string="الاسم")
    price = fields.Float(string="السعر")
    user_ids = fields.Many2many('res.users', string='المحاميين', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company, required=True)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user, required=True)
    no_edit = fields.Boolean('من غير تعديلات')

class internal_slate(models.Model):
    _name = 'internal.slate'
    _description = 'اللائحة الداخلية'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    
    service_date = fields.Date("الوقت المتوقع لتقديم الخدمة", compute='_count_service', store=True, tracking=True)

    @api.depends('create_date') 
    def _count_service(self):
        for slate in self:
            if slate.create_date:
                new_due_date = slate.create_date + timedelta(days = 30)
                slate.service_date = new_due_date
            else:
                slate.service_date = False

    
    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/slate_print/' + str(self.id)
        url = access_url + '%s?access_token=%s%s%s%s%s' % (
            suffix if suffix else '',
            self.access_token,
            '&report_type=%s' % report_type if report_type else '',
            '&download=true' if download else '',
            query_string if query_string else '',
            '#%s' % anchor if anchor else ''
        )
        return url
    
    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)

    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)
    
    
    url = fields.Char(compute='get_url')
    
    def get_url(self):
        base_url = self.company_id.website
        self.url = base_url + '/web#id=' + str(self.id) + '&model=internal.slate&view_type=form'
        
        
    portal_url = fields.Char(compute='get_portal_url')
    
    def get_portal_url(self):
        base_url = self.company_id.website
        self.portal_url = base_url + '/my/slate/' + str(self.id) + '?access_token=' + self.access_token
        
        
    sale_url = fields.Char(compute='get_sale_url')
    
    def get_sale_url(self):
        sale_url = False
        if self.qutation_id:
            base_url = self.company_id.website
            sale_url = base_url + '/my/orders/' + str(self.qutation_id.id) + '?access_token=' + self.qutation_id.access_token
        self.sale_url = sale_url
        

    def action_review(self):
        for slate in self:
            slate.write({'state': 'في حالة المراجعة'})
            return True

    def action_submit(self):
        for slate in self:
            slate.write({'state': 'معتمد'})
            return True

    def action_draft(self):
        for slate in self:
            slate.write({'state': 'جديد'})
            return True

    state = fields.Selection([
        ('جديد', 'جديد'),
        ('في حالة المراجعة', 'في حالة المراجعة'),
        ('معتمد', 'معتمد'),
        ], string='الحالة', default='جديد')
    name = fields.Char(string="الاسم")
    qutation_id = fields.Many2one('sale.order', string='عرض السعر', readonly=True)
    service_type_id = fields.Many2one('serivce.type', string='نوع الخدمة', required=True)
    no_edit = fields.Boolean(related='service_type_id.no_edit')
    certificate = fields.Char(string="رقم الإعتماد")
    slate_file = fields.Binary(string='اللائحة المعتمدة')
    registry_file = fields.Binary(string='السجل التجاري')
    partner_id = fields.Many2one('res.partner', string='مقدم الطلب', required=True)
    partner_company = fields.Many2one('res.partner', string='المنشأة', required=True)
    partner = fields.Char(related='partner_id.name', string='اسم العميل')
    user_ids = fields.Many2many(related='service_type_id.user_ids')
    user_id = fields.Many2one(related='service_type_id.user_id')
    company_id = fields.Many2one(related='service_type_id.company_id')
    phone = fields.Char(related='partner_id.phone', readonly=False)
    email = fields.Char(related='partner_id.email', readonly=False)
    company_phone = fields.Char(related='partner_company.phone', string='الجوال', readonly=False)
    company_email = fields.Char(related='partner_company.email', string='البريد الإلكتروني', readonly=False)
    company_registry = fields.Char(related='partner_company.company_registry', string='رقم السجل التجاري', readonly=False)
    company_file = fields.Binary(string='عقد تأسيس الشركة')
    main_center = fields.Char(string="المركز الرئيسي")
    labor = fields.Integer(string="عدد العاملين")
    avtivity = fields.Char(string="النشاط")
    address = fields.Char(string="العنوان الوطني", compute="get_address", readonly=False)
    
    short_address = fields.Char(string="العنوان المختصر", required=True)
    building_no = fields.Char(string="رقم المبنى", required=True)
    street = fields.Char(related='partner_company.street', string='الشارع', readonly=False, required=True)
    neighborhood = fields.Char(string="الشارع", required=True)
    addititonal_no = fields.Char(string="الرقم الفرعي", required=True)
    zip = fields.Char(related='partner_company.zip', string="الرمز البريدي", readonly=False, required=True)
    city = fields.Char(related='partner_company.city', string="المدينة", readonly=False, required=True)
    country_id = fields.Many2one(related='partner_company.country_id', string="الدولة", readonly=False, required=True)
    
    def get_address(self):
        for slate in self:
            short_address = '......'
            building_no = '......'
            street = '......'
            neighborhood = '......'
            addititonal_no = '......'
            zip = '......'
            city = '......'
            country_id = '......'
            if slate.short_address:
                short_address = slate.short_address
            if slate.building_no:
                building_no = slate.building_no
            if slate.street:
                street = slate.street
            if slate.neighborhood:
                neighborhood = slate.neighborhood
            if slate.addititonal_no:
                addititonal_no = slate.addititonal_no
            if slate.zip:
                zip = slate.zip
            if slate.city:
                city = slate.city
            if slate.country_id:
                country_id = slate.country_id.name
            slate.address = '[' + short_address + ']' + '، ' + street + '، ' + building_no + '، ' + neighborhood + '، ' + addititonal_no + '، ' + zip + '، ' + city + '، ' + country_id + '، ' 
            
    mail_box = fields.Char(string="صندوق بريد")
    mail_code = fields.Char(string="الرمز البريدي")
    wassel = fields.Char(string="رقم بريد واصل")
    fax = fields.Char(string="فاكس")
    file_number = fields.Char(string="رقم ملف المنشأة")
    day = fields.Char(string="تاريخ إصدار السجل التجاري")
    month = fields.Char(string="شهر")
    year = fields.Char(string="سنة")
    calander = fields.Selection([
            ('الهجري', 'الهجري'),
            ('الميلادي', 'الميلادي'),
            ], string='التقويم المعمول به في المنشأة')
    workdays = fields.Char(string="أيام العمل", compute="get_workdays")
    offdays = fields.Char(string="أيام الراحة", compute="get_offdays")
    
    sat = fields.Boolean('السبت')
    sun = fields.Boolean('الأحد')
    mon = fields.Boolean('الأثنين')
    tus = fields.Boolean('الثلاثاء')
    wed = fields.Boolean('الأربعاء')
    thur = fields.Boolean('الخميس')
    fri = fields.Boolean('الجمعة')

    def get_offdays(self):
        for slate in self:
            sat = ''
            sun = ''
            mon = ''
            tus = ''
            wed = ''
            thur = ''
            fri = ''
            if slate.sat:
                sat = 'السبت '
            if slate.sun:
                sun = 'الأحد '
            if slate.mon:
                mon = 'الأثنين '
            if slate.tus:
                tus = 'الثلاثاء '
            if slate.wed:
                wed = 'الأربعاء '
            if slate.thur:
                thur = 'الخميس '
            if slate.fri:
                fri = 'الجمعة '
            slate.offdays = sat + sun + mon + tus + wed + thur + fri
            
    def get_workdays(self):
        for slate in self:
            sat = 1
            sun = 1
            mon = 1
            tus = 1
            wed = 1
            thur = 1
            fri = 1
            if slate.sat:
                sat = 0
            if slate.sun:
                sun = 0
            if slate.mon:
                mon = 0
            if slate.tus:
                tus = 0
            if slate.wed:
                wed = 0
            if slate.thur:
                thur = 0
            if slate.fri:
                fri = 0
            days = sat + sun + mon + tus + wed + thur + fri
            slate.workdays = str(days)
    
    worktime_violation = fields.One2many('worktime.violation', 'slate_id', string="مخالفات تتعلق بمواعيد العمل")
    organize_violation = fields.One2many('organize.violation', 'slate_id', string="مخالفات تتعلق بتنظيم العمل")
    labor_violation = fields.One2many('labor.violation', 'slate_id', string="مخالفات تتعلق بسلوك العامل")
    
    name_edit = fields.Char(compute="get_name_edit")
    
    def get_name_edit(self):
        for slate in self:
            name_edit = 'موضحة بالتعديلات'
            if slate.name:
                name_edit = slate.name + ' موضحة بالتعديلات'
            slate.name_edit = name_edit

    edited_1 = fields.Text(string="إضافة على المادة (١)")
    edited_2 = fields.Text(string="إضافة على المادة (٢)")
    edited_3 = fields.Text(string="إضافة على المادة (٣)")
    edited_4 = fields.Text(string="إضافة على المادة (٤)")
    edited_5 = fields.Text(string="إضافة على المادة (٥)")
    edited_6 = fields.Text(string="إضافة على المادة (٦)")
    edited_7 = fields.Text(string="إضافة على المادة (٧)")
    edited_8 = fields.Text(string="إضافة على المادة (٨)")
    edited_9 = fields.Text(string="إضافة على المادة (٩)")
    edited_10 = fields.Text(string="إضافة على المادة (١٠)")
    edited_11 = fields.Text(string="إضافة على المادة (١١)")
    edited_12 = fields.Text(string="إضافة على المادة (١٢)")
    edited_13 = fields.Text(string="إضافة على المادة (١٣)")
    edited_14 = fields.Text(string="إضافة على المادة (١٤)")
    edited_15 = fields.Text(string="إضافة على المادة (١٥)")
    edited_16 = fields.Text(string="إضافة على المادة (١٦)")
    edited_17 = fields.Text(string="إضافة على المادة (١٧)")
    edited_18 = fields.Text(string="إضافة على المادة (١٨)")
    edited_19 = fields.Text(string="إضافة على المادة (١٩)")
    edited_20 = fields.Text(string="إضافة على المادة (٢٠)")
    edited_21 = fields.Text(string="إضافة على المادة (٢١)")
    edited_22 = fields.Text(string="إضافة على المادة (٢٢)")
    edited_23 = fields.Text(string="إضافة على المادة (٢٣)")
    edited_24 = fields.Text(string="إضافة على المادة (٢٤)")
    edited_25 = fields.Text(string="إضافة على المادة (٢٥)")
    edited_26 = fields.Text(string="إضافة على المادة (٢٦)")
    edited_27 = fields.Text(string="إضافة على المادة (٢٧)")
    edited_28 = fields.Text(string="إضافة على المادة (٢٨)")
    edited_29 = fields.Text(string="إضافة على المادة (٢٩)")
    edited_30 = fields.Text(string="إضافة على المادة (٣٠)")
    edited_31 = fields.Text(string="إضافة على المادة (٣١)")
    edited_32 = fields.Text(string="إضافة على المادة (٣٢)")
    edited_33 = fields.Text(string="إضافة على المادة (٣٣)")
    edited_34 = fields.Text(string="إضافة على المادة (٣٤)")
    edited_35 = fields.Text(string="إضافة على المادة (٣٥)")
    edited_36 = fields.Text(string="إضافة على المادة (٣٦)")
    edited_37 = fields.Text(string="إضافة على المادة (٣٧)")
    edited_38 = fields.Text(string="إضافة على المادة (٣٨)")
    edited_39 = fields.Text(string="إضافة على المادة (٣٩)")
    edited_40 = fields.Text(string="إضافة على المادة (٤٠)")
    edited_41 = fields.Text(string="إضافة على المادة (٤١)")
    edited_42 = fields.Text(string="إضافة على المادة (٤٢)")
    edited_43 = fields.Text(string="إضافة على المادة (٤٣)")
    edited_44 = fields.Text(string="إضافة على المادة (٤٤)")
    edited_45 = fields.Text(string="إضافة على المادة (٤٥)")
    edited_46 = fields.Text(string="إضافة على المادة (٤٦)")
    edited_47 = fields.Text(string="إضافة على المادة (٤٧)")
    edited_48 = fields.Text(string="إضافة على المادة (٤٨)")
    edited_49 = fields.Text(string="إضافة على المادة (٤٩)")
    edited_50 = fields.Text(string="إضافة على المادة (٥٠)")
    edited_51 = fields.Text(string="إضافة على المادة (٥١)")
    edited_52 = fields.Text(string="إضافة على المادة (٥٢)")
    edited_53 = fields.Text(string="إضافة على المادة (٥٣)")
    edited_54 = fields.Text(string="إضافة على المادة (٥٤)")
    edited_55 = fields.Text(string="إضافة على المادة (٥٥)")


    standard_1 = fields.Text(compute="get_standard_1", string="المادة (١)")

    def get_standard_1(self):
        for slate in self:
            partner = "......."
            if slate.partner_company:
                partner = slate.partner_company.name
            slate.standard_1 = ("يقصد بلفظ المنشأة أينما ورد في هذه اللائحة: " + partner + "." + "\n" 
                                + "يقصد بلفظ العامل أينما ورد في هذه اللائحة: كل شخص طبيعي - ذكراً أو أنثى - يعمل لمصلحة هذه المنشأة وتحت إدارتها، أو إشرافها مقابل أجر، ولو كان بعيداً عن نظارتها.") 
                

    standard_2 = fields.Text(compute="get_standard_2", string="المادة (٢)")


    def get_standard_2(self):
        for slate in self:
            calander = "......."
            if slate.calander:
                calander = slate.calander
            slate.standard_2 = ("التقويم المعمول به في المنشأة هو: التقويم " + calander + ".") 


    standard_3 = fields.Text(compute="get_standard_3", string="المادة (٣)")

    def get_standard_3(self):
        for slate in self:
            slate.standard_3 = ("١. تسري أحكام هذه اللائحة على جميع العاملين بالمنشأة، والفروع التابعة لها." + "\n" 
                                + "٢. لا تخل أحكام هذه اللائحة بالحقوق المكتسـبة للعمال ، و تعتبر هذه اللائحة مكملة لعقود العمل فيما لا يتعارض مع هذه الحقوق." + "\n"
                               + "٣. تطلع المنشأة العامل على هذه اللائحة عند التعاقد ، و تنص على ذلك في عقد العمل.") 

    standard_4 = fields.Text(compute="get_standard_4", string="المادة (٤)")

    def get_standard_4(self):
        for slate in self:
            slate.standard_4 = ("١. يجوز للمنشأة إصدار قرارات ، و سياسات خاصة بها يعطى بموجبها العمال حقوقا أفضل مما هو وارد في هذه اللائحة." + "\n" 
                                + "٢.  للمنشأة الحق في تضمين هذه اللائحة شروطا ، و أحكاما إضافية بما لا ينتقص من حقوق العمال المكتسبة بموجب نظام العمل ، ولائحته التنفيذية ، و القرارات الـصـادرة تنفيذا له ؛ و لا تكون هذه الإضـافـات أو التعديلات نافذة إلا بعـد اعتمادها من وزارة الموارد البشرية والتنمية الاجتماعية. " + "\n"
                               + "٣.كل نص يتم إضافته إلى هذه اللائحة يتعارض مع أحكام نظام العمل ، و لائحته التنفيذية ، و القرارات الصادرة تنفيذا له ؛ يعتبر باطلا ولا يعتد به." ) 


    standard_5 = fields.Text(compute="get_standard_5", string="المادة (٥)")

    def get_standard_5(self):
        for slate in self:
            slate.standard_5 = ("يوظف العمال على وظائف ذات مسميات ، و مواصفات معينة ؛ و يراعى عند التوظيف في المنشأة ما يلي:" + "\n"
                               + "١. أن يكون طالب العمل سعودي الجنسية." + "\n"
                               + "٢. أن يكون حائزا على المؤهلات العلمية ، و الخبرات المطلوبة للوظيفة من قبل المنشأة." + "\n"
                               + "٣. أن يجتاز بنجاح ما قد تقرره المنشأة من اختبارات ، أو مقابلات شخصية تتطلبها الوظيفة." + "\n"
                               + "٤.أن يكون لائقا طبيا بموجب شهادة طبية من الجهة التي تحددها المنشأة." + "\n"
                               + "٥. يجوز استثناء توظيف غير السعودي وفقا للشروط ، و الأحكام الواردة في المواد : ( السادسة والعشرون ، الثانية والثلاثون ، الثالثة والثلاثون ) من نظام العمل.")      
            
    standard_6 = fields.Text(compute="get_standard_6", string="المادة (٦)")

    def get_standard_6(self):
        for slate in self:
            slate.standard_6 = ("يتم توظيف العامل بموجب عقد عمل يحرر من نسختين باللغة العربية وفقا للنموذج الموحد المعد من الوزارة ، تسلم إحداهما للعامل وتودع الأخرى في ملف خدمته لدى المنشأة ، بحيث يتضمن العقد اسم صاحب العمل ، و اسم العامل ، و جنسيته ، و عنوانه الأصلي ، و عنوانه المختار ، و نوع العمل ، و مكانه ، و الأجر الأساسي المتفق عليه ، و أية مزايا وبدلات أخرى يتفق عليها ، و ما إذا كان العقد محدد المدة ، أو غير محدد المدة ، أو لأداء عمل معين ، و مدة التجربة إذا تم الاتفاق عليها ، و تاريخ مباشرة العمل ، و أية بيانات ضرورية ، و يجوز تحرير العقد بلغة أخرى إلى جانب اللغة العربية ؛ على أن يكون النص العربي هو المعتمد دوما.") 

            
            
    standard_7 = fields.Text(compute="get_standard_7", string="المادة (٧)")

    def get_standard_7(self):
        for slate in self:
            slate.standard_7 = ("مع مراعاة التاريخ المحدد في عقد العمل لمباشـرة العمل ؛ يحق للمنشـأة إلغاء عقد العامل الذي لا يباشـر مهام عمله دون عذر مشـروع خلال سبعة أيام عمل من تاريخ التوقيع على العقد بين الطرفين إذا كان التعاقد تم داخل المملكة ، أو من تاريخ قدومه إلى المملكة إذا كان التعاقد تم خارج المملكة.") 

            
            
    standard_8 = fields.Text(compute="get_standard_8", string="المادة (٨)")

    def get_standard_8(self):
        for slate in self:
            slate.standard_8 = ("١. لا يجوز للمنشأة أن ينقل العامل بغير موافقته – كتابة – من مكان عمله الأصلي إلى مكان آخر يقتضي تغير محل إقامته." + "\n"
                               + "للمنشأة في حالات الضرورة التي قد تقتضيها ظروف عارضة ولمدة لا تتجاوز ثلاثين يوماً في السنة تكليف العامل بعمل في مكان يختلف عن المكان المتفق عليه دون اشتراط موافقته ، على أن تتحمل المنشأة تكاليف انتقال العامل وإقامته خلال تلك المدة.") 

            
            
    standard_9 = fields.Text(compute="get_standard_9", string="المادة (٩)")

    def get_standard_9(self):
        for slate in self:
            slate.standard_9 = ("يتحدد الالتزام بمصروفات إركاب العامل ، أو أفراد أسرته وفق الضوابط التالية :" + "\n"
                               + "١.عند بداية التعاقد ، وفق ما يتفق عليه في عقد العمل." + "\n"
                               + "٢.عند تمتع العامل بإجازته السنوية ، وفق ما يتفق عليه في عقد العمل." + "\n"
                               + "٣. عند انتهاء خدمة العامل ، طبقاً لأحكام المادة ( الأربعون ) فقرة ( ١ ) من نظام العمل." + "\n"
                    + "٤.لا تتحمل المنشـأة تكاليف عودة العامل إلى بلده في حالة عدم صـلاحيته للعمل خلال فترة التجربة ، أو إذا رغب في العودة دون سبب مشروع ، أو في حالة ارتكابه مخالفة أدت إلى ترحيله بموجب قرار إداري ، أو حكم قضائي. ")  
            
            
    standard_10 = fields.Text(compute="get_standard_10", string="المادة (١٠)")

    def get_standard_10(self):
        for slate in self:
            slate.standard_10 = (" يستحق العامل الذي يتم نقله من مكان عمله الأصـلي إلى مكان آخر يقتضي تغيير محل إقامته نفقات نقله، ومن يعولهم شـرعا ممن يقيمون معه في تاريخ النقل بما فيها نفقات الإركاب مع نفقات نقل أمتعتهم ؛ ما لم يكن النقل بناء على رغبة العامل.") 

            

    standard_11 = fields.Text(compute="get_standard_11", string="المادة (١١)")

    def get_standard_11(self):
        for slate in self:
            slate.standard_11 = ("تتحمل المنشـأة في حال قيامها بتأهيل، أو تدريب العاملين السـعوديين كافة التكاليف، و إذا كان مكان التأهيل أو التدريب في غير الدائرة المكانية للمنشأة تؤمن تذاكر السفر في الذهاب، و العودة بالدرجة التي تحددها المنشأة ، كما تؤمن وسائل المعيشة من مأكل، و مسكن، و تنقلات داخلية، أو تصرف للعامل بدلا عنها، و تستمر في صرف أجر العامل طوال فترة التأهيل، و التدريب.") 



    standard_12 = fields.Text(compute="get_standard_12", string="المادة (١٢)")

    def get_standard_12(self):
        for slate in self:
            slate.standard_12 = (
                "١. يجوز للمنشـأة أن تُنهي عقد التأهيل ، أو التدريب من غير العاملين ، إذا ثبت من التقارير الصـادرة عن الجهة التي تتولى التدريب ، أو التأهيل عدم قابليته ، أو قدرته على إكمال برامج التدريب بصورة مفيدة." + "\n"
                + "٢.للمتدرب ، أو الخاضع للتأهيل من غير العاملين ، أو وليه ، أو وصيه الحق في إنهاء التدريب ، أو التأهيل إذا ثبت من التقارير الصادرة عن الجهة التي تتولى التدريب ، أو التأهيل عدم قابليته ، أو قدرته على إكمال برامج التدريب بصورة مفيدة." + "\n"
                + "٤.وفي كلتا الحالتين السـابقتين يجب على الطرف الذي يرغب في انهاء العقد إبلاغ الطرف الآخر بذلك قبل أسـبـوع على الأقل من تاريخ التوقف عن التدريب والتأهيل." + "\n"
                + "٤.للمنشأة أن تلزم المتدرب أو الخاضع للتأهيل من غير العاملين لديه ـ بعد إكمال مدة التدريب أو التأهيل ـ أن يعمل لديها مدة مماثلة لمدة التدريب أو التأهيل." + "\n"
                + "٥.للمنشـأة أن تلزم المتدرب أو الخاضـع للتأهيل من غير العاملين لديها بدفع تكاليف التدريب أو التأهيل التي تحملتها أو بنسبة المدة المتبقية في حالة رفضه رفض العمل المدة المماثلة او بعضها.") 
 
            
            
    standard_13 = fields.Text(compute="get_standard_13", string="المادة (١٣)")

    def get_standard_13(self):
        for slate in self:
            slate.standard_13 = ("أولا: يجوز للمنشأة أن تشترط على الخاضع للتدريب، أو التأهيل من العاملين لديها. بعد إكمال مدة التدريب أو التأهيل. أن يعمل لديها مدة لا تتجاوز المدة المماثلة لمدة برنامج التدريب أو التأهيل الذي خضع له العامل، إذا كان عقد العمل غير محددة المدة ، أو باقي مدة العقد في العقود محددة المدة إذا كانت المدة المتبقية من عقد العمل أقل من المدة المماثلة لمدة برنامج التدريب." + "\n"
                                + "ثانيا: يجوز للمنشأة أن تُنهي تأهيل أو تدريب العامل ، مع الزامه بدفع تكاليف التدريب التي تحملتها المنشأة أو بنسبة منها وذلك في الحالات التالية:" + "\n"
                                + "١. إذا قرر العامل إنهاء التدريب ، أو التأهيل قبل الموعد المحدد لذلك دون عذر مشروع." + "\n"
                                + "٢. إذا تم فسخ عقد عمل العامل وفق إحدى الحالات الواردة في المادة ( الثمانون ) من نظام العمل عدا الفقرة ( 6 ) منها أثناء فترة التدريب أو التأهيل." + "\n"
                                + "٣. إذا استقال العامل من العمل ، أو تركه لغير الحالات الواردة في المادة (الحادية والثمانون) من نظام العمل أثناء فترة التدريب أو التأهيل." + "\n"
                                + "ثالثا: يجوز للمنشـاة الزام العامل بدفع تكاليف التدريب أو التاهيل التي تحملتها المنشـأة أو بنسـبة منها إذا اسـتقال العامل من العمل ، أو تركه لغير الحالات الواردة في المادة (الحادية والثمانون) من نظام العمل قبل إنتهاء مدة العمل التي إشـترطتها عليه المنشأة بعد إنتهاء التدريب أو التأهيل.") 


            
            
    standard_14 = fields.Text(compute="get_standard_14", string="المادة (١٤)")

    def get_standard_14(self):
        for slate in self:
            slate.standard_14 = ("مع مراعاة أي إجراءات ، أو ترتيبات ينص عليها برنامج حماية الأجور ؛ تدفع أجور العمال بالعملة الرسمية للبلاد في مواعيد استحقاقها ، و تودع في حسابات العمال عن طريق البنوك المعتمدة في المملكة.") 

            

    standard_15 = fields.Text(compute="get_standard_15", string="المادة (١٥)")

    def get_standard_15(self):
        for slate in self:
            slate.standard_15 = ("تدفع أجور الساعات الإضافية المستحقة للعامل في نهاية الشهر الذي تم فيه التكليف.") 


            
    standard_16 = fields.Text(compute="get_standard_16", string="المادة (١٦)")

    def get_standard_16(self):
        for slate in self:
            slate.standard_16 = ("إذا وافق يوم دفع الأجور يوم الراحة الأسبوعية ، أو عطلة رسمية يتم الدفع في يوم العمل السابق.") 


            
            
    standard_17 = fields.Text(compute="get_standard_17", string="المادة (١٧)")

    def get_standard_17(self):
        for slate in self:
            slate.standard_17 = ("تعد المنشـأة تقارير عن الأداء بصـفة دورية ، مرة كل سـنة على الأقل لجميع العاملين وفقا للنماذج التي تضـعها لذلك؛ على أن تتضمن العناصر التالية:" + "\n"
                                + "١.المقدرة على العمل ، و درجة إتقانه (الكفاءة)." + "\n"
                                + "٢. سلوك العامل ، و مدى تعاونه مع رؤسانه ، و زملائه ، و عملاء المنشأة." + "\n"
                                + "٣.المواظبة.") 
    
            

    standard_18 = fields.Text(compute="get_standard_18", string="المادة (١٨)")

    def get_standard_18(self):
        for slate in self:
            slate.standard_18 = ("يقيم أداء العامل في التقرير بالتقديرات التي تحددها المنشأة ؛ على أن يتبع في ذلك مقياس من خمسة مستويات.") 

            
            

    standard_19 = fields.Text(compute="get_standard_19", string="المادة (١٩)")

    def get_standard_19(self):
        for slate in self:
            slate.standard_19 = ("يعد التقرير بمعرفة الرئيس المباشـر للعامل ؛ على أن يعتمد من ( صـاحب الصـلاحية ) ، و يخطر العامل بصـورة من التقرير فـور اعتماده ، و يحق للعامل أن يتظلم من التقرير وفقا لقواعد التظلم المنصوص عليها في هذه اللائحة.") 



            
    standard_20 = fields.Text(compute="get_standard_20", string="المادة (٢٠)")

    def get_standard_20(self):
        for slate in self:
            slate.standard_20 = ("١.يجوز للمنشأة منح العاملين علاوات سنوية ، يتم تحديد نسبتها بناء على ضوء المركز المالي للمنشأة." + "\n"
                                + "٢. يكون العامل مؤهلًا لاستحقاق العلاوة متى حصـل في تقريره الدوري على مسـتوى متوسـط على الأقل في النموذج الذي تضعه المنشأة ، وذلك بعد مضي سنة كاملة من تاريخ التحاقه بالعمل ، أو من تاريخ حصوله على العلاوة السابقة." + "\n"
                                + "٣. يجوز لإدارة المنشأة منح العامل علاوة استثنائية وفقا للضوابط التي تضعها في هذا الشأن.") 

            

    standard_21 = fields.Text(compute="get_standard_21", string="المادة (٢١)")

    def get_standard_21(self):
        for slate in self:
            slate.standard_21 = ("تضع المنشأة سلما وظيفيا لوظائفها تحدد فيه عدد ، و مسميات الوظائف . ـ وفقا لما جاء في دليل التصنيف ، و التوصيف المهني السعودي ـ و درجة كل وظيفة ، و شروط شغلها ، و بداية أجرها فيه ، و يكون العامل مؤهلًا للترقية إلى وظيفة أعلى ؛ متى توفرت الشروط التالية:" + "\n"
                                + "١.وجود الوظيفة الشاغرة الأعلى." + "\n"
                                + "٢.توافر مؤهلات شغل الوظيفة المرشح للترقية إليها." + "\n"
                                + "٣.حصوله على مستوى فوق المتوسط على الأقل في آخر تقرير دوري." + "\n"
                                + "٤.موافقة صاحب الصلاحية." + "\n"
                                + "٥.يجوز لإدارة المنشأة منح العامل ترقية استثنائية ؛ وفقا للضوابط التي تضعها في هذا الشأن.") 




    standard_22 = fields.Text(compute="get_standard_22", string="المادة (٢٢)")

    def get_standard_22(self):
        for slate in self:
            slate.standard_22 = ("إذا توافرت شروط الترقية لوظيفة أعلى في أكثر من عامل ؛ فإن المفاضلة للترقية تكون كالآتي:" + "\n"
                                + "١.ترشيح صاحب الصلاحية." + "\n"
                                + "٢.الحاصل على تقدير أعلى." + "\n"
                                + "٣. الحاصل على شهادات علمية أعلى ، أو دورات تدريبية أكثر." + "\n"
                                + "٦.الأكثر خبرة عملية بمجال عمل المنشأة." + "\n"
                                + "٥.الأقدمية في العمل بالمنشأة.") 




    standard_23 = fields.Text(compute="get_standard_23", string="المادة (٢٣)")

    def get_standard_23(self):
        for slate in self:
            slate.standard_23 = ("إذا تم انتداب العامل لأداء عمل خارج مقر عمله تلتزم المنشأة بما يلي:" + "\n"
                                + "١. تؤمن للعامل وسائل التنقل اللازمة ، ما لم يتم صرف مقابل لها بموافقته." + "\n"
                                + "٢.يصرف للعامل مقابل للتكاليف التي يتكبدها للسكن ، و الطعام ، و ما إلى ذلك ؛ ما لم تؤمنها له المنشأة." + "\n"
                                + "٣.قيمة البدل اليومي للانتداب حسب درجة العامل." + "\n"
        + "ويجب أن تحدد تلك الالتزامات في قرار الانتداب ؛ وفقا للفئات ، و الضـوابط التي تضعها المنشأة في هذا الشأن ، و يكون احتساب تلك النفقات من وقت مغادرة العامل لمقر عمله إلى وقت عودته ؛ وفق المدة المحددة له من قبل المنشأة.") 




    standard_24 = fields.Text(compute="get_standard_24", string="المادة (٢٤)")

    def get_standard_24(self):
        for slate in self:
            slate.standard_24 = ("تؤمن المنشأة لعمالها السكن المناسب ، وكذلك وسيلة النقل إذا نص على ذلك في عقد العمل ، و يجوز النص في عقد العمل على أن تدفع المنشأة للعامل بدل سكن ، وبدل نقل نقدي.") 




    standard_25 = fields.Text(compute="get_standard_25", string="المادة (٢٥)")

    def get_standard_25(self):
        for slate in self:
            workdays = "......."
            offdays = "......."
            if slate.workdays:
                workdays = slate.workdays
            if slate.offdays:
                offdays = slate.offdays                
            slate.standard_25 = ("١.يكون عدد أيام العمل " + workdays + " أيام في الأسـبـوع ، و يكون ( يوم / يومي) " + offdays + " الراحة الأسـبوعية بأجر كامل لجميع العمال ، و يجوز للمنشأة. بعد إبلاغ مكتب العمل المختص. أن تستبدل بهذا اليوم لبعض عمالها أي يوم من أيام الأسبوع ، و عليها أن تمكنهم من القيام بواجباتهم الدينية ، و لا يجوز تعويض يوم الراحة الأسبوعية بمقابل نقدي." + "\n"
                                + "٢.تكون ساعات العمل (ثماني) ساعات عمل يوميا تخفض الى (ست) ساعات يوميا في شهر رمضان للعمال المسلمين.") 




    standard_26 = fields.Text(compute="get_standard_26", string="المادة (٢٦)")

    def get_standard_26(self):
        for slate in self:
            slate.standard_26 = ("١. في حال تكليف العامل بالعمل الإضـافي ؛ يتم ذلك بموجب تكليف كتابي ، أو الكتروني موجه له تصـدره الجهة المسـئولة في المنشـأة يبين فيه عدد السـاعات الإضـافية المكلف بها العامل ، و عدد الأيام اللازمة لذلك ؛ وفق ما نصـت عليه المادة (السادسة بعد المائة) من نظام العمل." + "\n"
                                + "٢. تدفع المنشأة للعامل عن ساعات العمل الإضافية أجرا إضافيا يوازي أجر الساعة مضافا إليه (٥٠%) من أجره الأساسي.") 



    standard_27 = fields.Text(compute="get_standard_27", string="المادة (٢٧)")

    def get_standard_27(self):
        for slate in self:
            slate.standard_27 = ("يكون دخول العمال إلى مواقع عملهم ، و انصرافهم منه من الأماكن المخصصة لذلك ، و على العمال الامتثال للتفتيش (التفتيش الإداري) متى طلب منهم ذلك.") 




    standard_28 = fields.Text(compute="get_standard_28", string="المادة (٢٨)")

    def get_standard_28(self):
        for slate in self:
            slate.standard_28 = ("يجوز للمنشأة أن تلزم العامل بأن يثبت حضوره ، و انصرافه بإحدى الوسائل المعدة لهذا الغرض.") 


            

    standard_29 = fields.Text(compute="get_standard_29", string="المادة (٢٩)")

    def get_standard_29(self):
        for slate in self:
            slate.standard_29 = ("يستحق العامل عن كل سنة من سنوات الخدمة إجازة سنوية بأجر كامل لا تقل مدتها عن واحد وعشرين يوما ، تزاد إلى مدة لا تقل عن ثلاثين يوما ، إذا بلغت خدمته خمس سـنوات متصـلة ، و للعامل بعد موافقة المنشـأة الحصـول على جزء من إجازته السنوية بنسبة المدة التي قضاها من السنة في العمل؛ و يجوز الاتفاق في عقد العمل على أن تكون مدة الإجازة السنوية أكثر من ذلك. ") 


            

    standard_30 = fields.Text(compute="get_standard_30", string="المادة (٣٠)")

    def get_standard_30(self):
        for slate in self:
            slate.standard_30 = ("للعامل الحق في إجازة بأجر كامل في الأعياد ، و المناسبات ؛ وفق مايلي:" + "\n"
                                + "١.أربعة أيام بمناسبة عيد الفطر المبارك ، تبدأ من اليوم التالي لليوم التاسع و العشرين من شهر رمضان المبارك حسـب تقويم أم القرى." + "\n"
                                + "٢.أربعة أيام بمناسبة عيد الأضحى المبارك ، تبدأ من يوم الوقوف بعرفة." + "\n"
                                + "٣.يوم واحد بمناسبة اليوم الوطني للمملكة (أول الميزان)." + "\n"
                                + "وإذا تداخلت أيام هذه الإجازات مع الراحة الأسبوعية يعوض العامل عنها بما يعادلها قبل أيام تلك الإجازات أو بعدها." + "\n"
                                + "أما إذا تداخلت أيام إجازة أحد العيدين مع إجازة اليوم الوطني فلا يعوض العامل عنه.") 


            

    standard_31 = fields.Text(compute="get_standard_31", string="المادة (٣١)")

    def get_standard_31(self):
        for slate in self:
            slate.standard_31 = ("يحق للعامل الحصول على إجازة بأجر كامل في الحالات التالية:" + "\n"
                                + "١.خمسة أيام عند زواجه." + "\n"
                                + "٢.ثلاثة أيام في حالة ولادة مولود له." + "\n"
                                + "٣.خمسة أيام في حالة وفاة زوجة العامل ، أو أحد أصوله ، أو فروعه." + "\n"
                                + "٤.أربعة أشهر ، و عشـرة أيام في حالة وفاة زوج العاملة المسلمة ؛ و لها الحق في تمديدها دون أجر إن كانت حاملا حتى تضع حملها ، و لا يجوز لها الاستفادة من باقي إجازة العدة الممنوحة لها بعد وضع هذا الحمل." + "\n"
                                + "٥.خمسة عشر يوما في حالة وفاة زوج العاملة غير المسلمة." + "\n"
                                + "وللمنشأة الحق في طلب الوثائق المؤيدة للحالات المشار إليها.") 

            

    standard_32 = fields.Text(compute="get_standard_32", string="المادة (٣٢)")

    def get_standard_32(self):
        for slate in self:
            slate.standard_32 = ("يستحق العامل - الذي يثبت مرضـه بشهادة طبية صادرة عن طبيب المنشأة ، أو مرجع طبي معتمد لديها - إجازات مرضية خلال السنة الواحدة ، و التي تبدأ من تاريخ أول إجازة مرضية ؛ سواء أكانت هذه الإجازات متصلة أم متقطعة ، وذلك على النحو التالي:" + "\n"
                                + "١. الثلاثون يوما الأولى ، بأجر كامل." + "\n"
                                + "٢.الستون يوما التالية ، بثلاثة أرباع الأجر." + "\n"
                                + "٣.لثلاثون يوما التي تلي ذلك ، بدون أجر." + "\n"
                                + "وللعامل الحق في وصل إجازته السنوية بالمرضية") 



    standard_33 = fields.Text(compute="get_standard_33", string="المادة (٣٣)")

    def get_standard_33(self):
        for slate in self:
            slate.standard_33 = ("تقوم المنشـأة بالتأمين على جميع العاملين لديها صحيا؛ وفقا لما يقرره نظام التأمين الصـحي التعاوني ، ولائحته التنفيذية ، كما تقوم بالاشتراك عن جميع العاملين في فرع الأخطار المهنية لدى المؤسسة العامة للتأمينات الاجتماعية ؛ وفقا لما يقرره نظامها.") 


    standard_34 = fields.Text(compute="get_standard_34", string="المادة (٣٤)")

    def get_standard_34(self):
        for slate in self:
            slate.standard_34 = ("للمرأة العاملة الحق في إجازة وضـع بأجر كامل لمدة عشـرة أسابيع توزعها كيف تشـاء ، بحيث تبدأ بحد أقصى بأربعة أسابيع قبل التاريخ المرجح للوضـع ؛ و يحدد هذا التاريخ بواسـطة الجهة الطبية المعتمدة لدى المنشـأة ، أو بشهادة طبية مصـدقة من جهة صحية ، و لا يجوز تشغيل المرأة العاملة خلال الأسابيع الستة التالية لوضعها." + "\n"
                                + "وفي حالة إنجاب طفل مريض ، أو من ذوي الاحتياجات الخاصة ؛ فللعاملة الحق في إجازة بأجر كامل لمدة شهر واحد بعد انقضاء إجازة الوضع ؛ و لها تمديد الإجازة لمدة شهر دون أجر.") 


    standard_35 = fields.Text(compute="get_standard_35", string="المادة (٣٥)")

    def get_standard_35(self):
        for slate in self:
            slate.standard_35 = ("يحق للمرأة العاملة في المنشـأة عندما تعود إلى مزاولة عملها بعد إجازة الوضـع أن تأخذ بقصـد إرضـاع مولودها فترة ، أو فترات استراحة ، لا تزيد في مجموعها على الساعة في اليوم الواحد ، وذلك علاوة على فترات الراحة الممنوحة لجميع العمال ، و تحسـب هذه الفترة ، أو الفترات من ساعات العمل الفعلية ، وذلك لمدة أربعة و عـشـريـن شـهرا من تاريخ الـوضـع ، و لا يترتب على ذلك تخفيض الأجر ، و يجب على المرأة العاملة بعد عودتها من إجازة الـوضـع إشـعـار صـاحب العمل كتابة بوقت فترة ، أو فترات تلك الاستراحة ، و ما يطرأ على ذلك الوقت من تعديل ، و تحدد فترة ، أو فترات الرضـاعة على ضـوء ذلك بحسـب ما ورد في اللائحة التنفيذية لنظام العمل") 


    standard_36 = fields.Text(compute="get_standard_36", string="المادة (٣٦)")

    def get_standard_36(self):
        for slate in self:
            slate.standard_36 = ("تلتزم المنشأة بتقديم الخدمات الاجتماعية التالية:" + "\n"
                                + "١. إعداد مكان لأداء الصلاة." + "\n"
                                + "٣. إعداد مكان لتناول الطعام." + "\n"
                                + "٣.توفر المنشأة المتطلبات ، و الخدمات ، و المرافق التيسيرية الضرورية للعمال من ذوي الاعاقة التي تمكنهم من أداء أعمالهم بحسب الاشتراطات المنصوص عليها في اللائحة التنفيذية لنظام العمل.") 


    standard_37 = fields.Text(compute="get_standard_37", string="المادة (٣٧)")

    def get_standard_37(self):
        for slate in self:
            slate.standard_37 = ("١. يجب على كل منشأة وضع تنظيم لاشتراطات زي العاملين لديها نساء ورجالاً وفق الضوابط التالية:" + "\n"
                                + "١.الا يتعارض مع الأحكام الشرعية." + "\n"
                                + "٢.أن يكون بمظہر مهني لائق يتناسب مع مهام العامل في مكان العمل." + "\n"
                                + "٣.أن يكون محتشماً وغير شفاف." + "\n"
                                + "٤.وضع العقوبات المترتبة على مخالفة الاشتراطات." + "\n"
                                + "٥.إعلان تلك الاشتراطات على حده في مكان ظاهر بالمنشأة أو أي وسيلة أخرى تكفل علم الخاضعين لها بأحكامها ، وإقرارهم بالعلم بها." + "\n"
                                + "٢.على جميع العاملين بالمنشأة الالتزام بمقتضيات أحكام الشريعة الإسلامية ، و الأعراف الاجتماعية المرعية في التعامل مع الآخرين." + "\n"
                                + "٣.يمتنع على جميع العاملين الخلوة مع الجنس الآخر ، وعلى المنشأة أن تتخذ كل التدابير التي تمنع الخلوة بين الجنسين داخل المنشأة." + "\n"
                                + "٤.على جميع العاملين الامتناع عن القيام بأي شكل من أشكال الايذاء ، أو الإساءة الجسدية ، أو القولية ، أو الإيحائية ، أو باتخاذ أي موقف يخدش الحياء ، أو ينال من الكرامة ، أو السمعة ، أو الحرية ، أو يقصد منه استدراج ، أو إجبار أي شخص إلى علاقة غير مشروعة ، حتى لو كان ذلك على سبيل المزاح ، وذلك عند التواصل المباشر ، أو بأي وسيلة تواصل أخرى ، و للمنشأة أن تتخذ كل الترتيبات ، و الإجراءات الضرورية ، و اللازمة لتبليغ جميع العاملين بذلك.") 


    standard_38 = fields.Text(compute="get_standard_38", string="المادة (٣٨)")

    def get_standard_38(self):
        for slate in self:
            slate.standard_38 = ("١.يعتبر من قبيل الايذاء ، جميع ممارسات الإساءة الإيجابية ، أو السلبية ، وجميع أشكال الاستغلال ، أو الابتزاز ، أو الإغراء أو التهديد ؛ سواء أكانت جسدية ، أو نفسية ، أو جنسية ؛ و التي تقع في مكان العمل من قبل صاحب العمل على العامل أو من قبل العامل على صاحب العمل ، أو من قبل عامل على آخر ، أو على أي شخص موجود في مكان العمل ، و تعتبر المساعدة ، و التستر على ذلك في حكم الإيذاء." + "\n"
                                + "٢. يعتبر من قبيل الايذاء المقصود في الفقرة السابقة ، ما يقع باستخدام أية وسيلة من وسائل الاتصال سواء بالقول ، أو الكتابة ، أو الاشارة ، أو الايحاء ، أو الرسم ، أو باستخدام الهاتف ، أو بالوسائل الإلكترونية الأخرى ، أو بأي شكل من أشكال السلوك الذي يدل على ذلك.") 


    standard_39 = fields.Text(compute="get_standard_39", string="المادة (٣٩)")

    def get_standard_39(self):
        for slate in self:
            slate.standard_39 = ("١.مع عدم الإخلال بحق من وقع عليه الإيذاء في مكان العمل من الالتجاء إلى الجهات الحكومية المختصـة ، يحق له التقدم بشكواه للمنشـأة خلال مدة أقصاها خمسـة أيام عمل من وقوع الإيذاء عليه ، و يجوز لكل من شاهد أو اطلع على واقعة إيذاء ، التقدم ببلاغ للمنشأة بذلك؛ أما إذا كان الإيذاء قد وقع من قبل صاحب المنشـأة ، أو من أعلى سلطة فيها ؛ فيكون التقدم بالشكوى للجهة الحكومية المختصة." + "\n"
                                + "٢.على المنشأة عند تقديم شكوى ، أو بلاغ ، تشكيل لجنة بقرار من المسئول المختص ، تكون مهمتها التحقيق في حالات الإيذاء ، والاطلاع على الأدلة ، و التوصية بإيقاع الجزاء التأديبي المناسب على من ثبتت إدانته ، و ذلك خلال خمسة أيام عمل من تلقيها الشكوى ، أو البلاغ.") 


    standard_40 = fields.Text(compute="get_standard_40", string="المادة (٤٠)")

    def get_standard_40(self):
        for slate in self:
            slate.standard_40 = ("١.مع مراعاة مبدأ السرية تستمع اللجنة لجميع الأطراف ، و الشهود ، و تدون كل ما يجري في محاضر؛ توقع من الأطراف ، و الشهود على أقوالهم ، ثم توقع من أعضاء اللجنة في نهاية كل صفحة." + "\n"
                                + "٢.للجنة حق استدعاء من ترى ضـرورة استجوابه من العاملين ، و الاستماع إلى أقواله ، و على من تم استدعاؤه المثول أمام اللجنة ؛ حتى لا يقع تحت طائلة المسؤولية." + "\n"
                                + "٣.يجوز للجنة أن ترفع توصية لإدارة المنشأة بالتفريق بين الشاكي ، و المشكو في حقه أثناء فترة التحقيق." + "\n"
                                + "٤. في حال ثبوت واقعة الإيذاء بأي طريقة من طرق الإثبات المعتبرة ؛ توصي اللجنة بالأغلبية بإيقاع الجزاء التأديبي المناسـب على المعتدي." + "\n"
                                + "٥.إذا كان الاعتداء يشكل جريمة جنائية ، وجب على اللجنة رفع الشكوى للمدير العام؛ لتبليغ الجهات الحكومية المختصة بذلك." + "\n"
                                + "٦.في حال عدم ثبوت واقعة الإيذاء ، توصي اللجنة بإيقاع عقوبة تأديبية على المبلغ؛ إذا تبين لها أن الشكوى ، أو البلاغ كيدي." + "\n"
                                + "٧.لا يمنع الجزاء التأديبي الموقع من قبل المنشأة على المعتدي ، من حق المعتدى عليه اللجوء للجهات الحكومية المختصة." + "\n"
                                + "٨.لا يمنع توقيع عقوبة شرعية ، أو نظامية أخرى على المعتدي ، من توقيع المنشأة جزاء تأديبيا عليه.") 



    standard_41 = fields.Text(compute="get_standard_41", string="المادة (٤١)")

    def get_standard_41(self):
        for slate in self:
            slate.standard_41 = ("المخالفة هي كل فعل من الأفعال التي يرتكبها العامل ، و تستوجب أيا من الجزاءات التالية:" + "\n"
                                + "١.الإنذار الكتابي: و هو كتاب توجهه المنشأة إلى العامل موضحا به نوع المخالفة التي ارتكبها ، مع لفت نظره إلى إمكان تعرضه إلى جزاء أشد ، في حالة استمرار المخالفة ، أو العودة إلى مثلها مستقبلا." + "\n"
                                + "٢.غرامة مالية: و هي حسـم نسبة من الأجر في حدود جزء من الأجر اليومي ، أو الحسـم من الأجر بما يتراوح بين أجر يوم ، و خمسة أيام في الشهر الواحد كحد أقصى." + "\n"
                                + "٣.الإيقاف عن العمل بدون أجر: و هو منع العامل من مزاولة عمله خلال فترة معينة ، مع حرمانه من أجره خلال هذه الفترة . على أن لا تتجاوز فترة الإيقاف خمسة أيام في الشهر الواحد." + "\n"
                                + "٤.الحرمان من الترقية ، أو العلاوة الدورية: و ذلك لمدة أقصاها سنة واحدة من تاريخ استحقاقها." + "\n"
                                + "٥.الفصل من الخدمة مع المكافأة: و هو فصـل العامل بناء على سبب مشـروع؛ لارتكابه المخالفة مع عدم المساس بحقه في مكافأة نهاية الخدمة." + "\n"
                                + "٦.الفصـل من الخدمة بدون مكافأة: و هو فسخ عقد عمل العامل دون مكافأة ، أو إشـعار ، أو تعويض؛ لارتكابه أي من الحالات المنصوص عليها في المادة (الثمانون) من نظام العمل." + "\n"
                                + "ويجب أن يتناسب الجزاء المفروض على العامل مع نوع ، و مدى جسامة المخالفة المرتكبة من قبله.") 



    standard_42 = fields.Text(compute="get_standard_42", string="المادة (٤٢)")

    def get_standard_42(self):
        for slate in self:
            slate.standard_42 = ("كل عامل يرتكب أيا من المخالفات الواردة في جداول المخالفات ، و الجزاءات - الملحق بهذه اللائحة - يعاقب بالجزاء الموضـح قرين المخالفة التي ارتكبها.") 



    standard_43 = fields.Text(compute="get_standard_43", string="المادة (٤٣)")

    def get_standard_43(self):
        for slate in self:
            slate.standard_43 = ("تكون صلاحية توقيع الجزاءات المنصوص عليها في هذه اللائحة ، من قبل (صاحب الصلاحية) بالمنشأة ، أو من يفوضه ؛ و يجوز له استبدال الجزاء المقرر لأية مخالفة بجزاء أخف.") 



    standard_44 = fields.Text(compute="get_standard_44", string="المادة (٤٤)")

    def get_standard_44(self):
        for slate in self:
            slate.standard_44 = ("في حال ارتكاب العامل ذات المخالفة بعد مضي مائة وثمانين يوما على سـبق ارتكابها ؛ فإنه لا يعتبر عائدا ، و تعد مخالفة ، وكأنها ارتكبت للمرة الأولى.") 



    standard_45 = fields.Text(compute="get_standard_45", string="المادة (٤٥)")

    def get_standard_45(self):
        for slate in self:
            slate.standard_45 = ("عند تعدد المخالفات الناشئة عن فعل واحد ، يكتفى بتوقيع الجزاء الأشد من بين الجزاءات المقررة في هذه اللائحة.") 



    standard_46 = fields.Text(compute="get_standard_46", string="المادة (٤٦)")

    def get_standard_46(self):
        for slate in self:
            slate.standard_46 = ("لا يجوز أن يوقع على العامل عن المخالفة الواحدة أكثر من جزاء واحد ، كما لا يجوز أن يوقع على العامل عن المخالفة الواحدة غرامة تزيد قيمتها على أجر خمسـة أيام ، و لا أن يقتطع من أجره أكثر من أجر خمسـة أيام في الشهر الواحد وفاء للغرامات التي توقع عليه.") 



    standard_47 = fields.Text(compute="get_standard_47", string="المادة (٤٧)")

    def get_standard_47(self):
        for slate in self:
            slate.standard_47 = ("لا توقع المنشأة أيا من الجزاءات التي تتجاوز عقوبتها غرامة أجر يوم واحد ، إلا بعد إبلاغ العامل كتابة بالمخالفات المنسوبة إليه ، و سماع أقواله ، و تحقيق دفاعه ، و ذلك بموجب محضر يودع بملفه الخاص.") 



    standard_48 = fields.Text(compute="get_standard_48", string="المادة (٤٨)")

    def get_standard_48(self):
        for slate in self:
            slate.standard_48 = ("لا يجوز للمنشـأة توقيع أي جزاء على العامل لأمر ارتكبه خارج مكان العمل إلا إذا كان له علاقة مباشـرة بطبيعة عمله أو بالمنشـأة أو بمديرها المسئول ، وذلك دون الإخلال بحكم المادة (الثمانون) من نظام العمل.") 



    standard_49 = fields.Text(compute="get_standard_49", string="المادة (٤٩)")

    def get_standard_49(self):
        for slate in self:
            slate.standard_49 = ("لا يجوز مساءلة العامل تأديبيا عن مخالفة مضي على كشفها أكثر من ثلاثين يوما من تاريخ علم المنشـأة بمرتكبها ، دون أن تقوم باتخاذ أي من إجراءات التحقيق بشأنها.") 




    standard_50 = fields.Text(compute="get_standard_50", string="المادة (٥٠)")

    def get_standard_50(self):
        for slate in self:
            slate.standard_50 = ("لا يجوز للمنشأة توقيع أي جزاء على العامل ، إذا مضى على تاريخ ثبوت المخالفة أكثر من ثلاثين يوما.") 



    standard_51 = fields.Text(compute="get_standard_51", string="المادة (٥١)")

    def get_standard_51(self):
        for slate in self:
            slate.standard_51 = ("تلتزم المنشـأة بإبلاغ العامل كتابة بما أوقع عليه من جزاءات ، و نوعها ، و مقدارها ، و الجزاء الذي سـوف يتعرض له في حالة تكرار المخالفة ، و إذا امتنع العامل عن استلام الإخطار ، أو رفض التوقيع بالعلم ، أو كان غائبا ؛ يرسل إليه بالبريد المسجل على عنوانه المختار الثابت في ملف خدمته ، أو بالبريد الالكتروني الشخصي الثابت بعقد العمل ، أو المعتمد لدى المنشأة ؛ و يترتب على التبليغ بأي من هذه الوسائل جميع الآثار القانونية.") 



    standard_52 = fields.Text(compute="get_standard_52", string="المادة (٥٢)")

    def get_standard_52(self):
        for slate in self:
            slate.standard_52 = ("يخصص لكل عامل صحيفة جزاءات ، يدون فيها نوع المخالفة التي ارتكبها ، و تاريخ وقوعها ، والجزاء الموقع عليه ؛ و تحفظ هذه الصحيفة في ملف خدمة العامل.") 



    standard_53 = fields.Text(compute="get_standard_53", string="المادة (٥٣)")

    def get_standard_53(self):
        for slate in self:
            slate.standard_53 = ("تقيد الغرامات الموقعة على العمال في سجل خاص ؛ وفق أحكام المادة (الثالثة والسبعون) من نظام العمل ، و يكون التصرف فيها بما يعود بالنفع على العمال من قبل اللجنة العمالية في المنشـأة ؛ و في حالة عدم وجود لجنة عمالية يكون التصـرف في الغرامات بموافقة وزارة الموارد البشرية والتنمية الاجتماعية.") 



    standard_54 = fields.Text(compute="get_standard_54", string="المادة (٥٤)")

    def get_standard_54(self):
        for slate in self:
            slate.standard_54 = ("مع عدم الإخلال بحق العامل في الالتجاء إلى الجهات الإدارية ، أو القضائية المختصة ، أو الهيئات ؛ يحق للعامل أن يتظلم إلى إدارة المنشأة من أي تصرف ، أو إجراء ، أو جزاء يتخذ في حقه من قبلها ، و يقدم التظلم إلى إدارة المنشأة خلال ثلاثة أيام عمل من تاريخ العلم بالتصـرف ، أو الإجراء المتظلم منه ، و لا يضـار العامل من تقديم تظلمه ، و يخطر العامل بنتيجة البت في تظلمه ، في ميعاد لا يتجاوز خمسة أيام عمل من تاريخ تقديمه التظلم.") 



    standard_55 = fields.Text(compute="get_standard_55", string="المادة (٥٥)")

    def get_standard_55(self):
        for slate in self:
            slate.standard_55 = ("تنفذ أحكام هذه اللائحة في حق المنشـأة اعتبارا من تاريخ إبلاغها باعتمادها ؛ على أن تسـري في حق العمال اعتبارا من اليوم التالي لإعلانها.") 

            
            
            
    @api.model_create_multi
    def create(self, vals_list):
        record = super(internal_slate, self).create(vals_list)
        if record.partner_company:
            record.name = 'لائحة العمل الداخلية ل' + str(record.partner_company.name)
        else:
            record.name = 'لائحة العمل الداخلية ل' + str(record.partner)
        worktime_violation_value = [{
            'name': 'التأخر عن مواعيد الحضور للعمل لغاية (15) دقيقة دون إذن، أو عذر مقبول: إذا لم يترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '5%',
            'Third_penality': '10%',
            'Fourth_penality': '20%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التأخر عن مواعيد الحضور للعمل لغاية (15) دقيقة دون إذن، أو عذر مقبول: إذا ترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '15%',
            'Third_penality': '25%',
            'Fourth_penality': '50%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التأخر عن مواعيد الحضور للعمل أكثر من (15) دقيقة لغاية (30) دقيقة دون إذن، أو عذر مقبول: إذا لم يترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': '10%',
            'Second_penality': '15%',
            'Third_penality': '25%',
            'Fourth_penality': '50%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التأخر عن مواعيد الحضور للعمل أكثر من (15) دقيقة لغاية (30) دقيقة دون إذن، أو عذر مقبول: إذا ترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': '25%',
            'Second_penality': '50%',
            'Third_penality': '75%',
            'Fourth_penality': 'يوم',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التأخر عن مواعيد الحضور للعمل أكثر من (30) دقيقة لغاية (60) دقيقة دون إذن، أو عذر مقبول: إذا لم يترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': '25%',
            'Second_penality': '50%',
            'Third_penality': '75%',
            'Fourth_penality': 'يوم',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التأخر عن مواعيد الحضور للعمل أكثر من (30) دقيقة يوم لغاية (60) دقيقة دون إذن، أو عذر مقبول: إذا ترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': '30%',
            'Second_penality': '50%',
            'Third_penality': 'يوم',
            'Fourth_penality': 'يومين',
            'note': 'بالإضافة إلى حسم أجر دقائق التأخر',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التأخر عن مواعيد الحضور للعمل لمدة تزيد على ساعة دون إذن، أو عذر مقبول: سواءً ترتب، أو لم يترتب على ذلك تعطيل عمال آخرين.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': 'يوم',
            'Third_penality': 'يومين',
            'Fourth_penality': 'ثلاثة أيام',
            'note': 'بالإضافة إلى حسم أجر ساعات التأخر',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'ترك العمل، أو الانصراف قبل الميعاد دون إذن، أو عذر مقبول بما لا يتجاوز (15) دقيقة.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10٪',
            'Third_penality': '25٪',
            'Fourth_penality': 'يوم',
            'note': 'بالإضافة إلى حسم أجر مدة ترك العمل',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'ترك العمل، أو الانصراف قبل الميعاد دون إذن، أو عذر مقبول بما يتجاوز (15) دقيقة.',
            'First_penality': '10%',
            'Second_penality': '25%',
            'Third_penality': '50%',
            'Fourth_penality': 'يوم',
            'note': 'بالإضافة إلى حسم أجر مدة ترك العمل',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'البقاء في أماكن العمل، أو العودة إليها بعد انتهاء مواعيد العمل دون إذن مسبق.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '25%',
            'Fourth_penality': 'يوم',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الغياب دون إذن كتابي، أو عذر مقبول لمدة يوم، خلال السنة العقدية الواحدة.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'أربعة أيام',
            'Fourth_penality': 'الحرمان من الترقيات، أو العلاوات لمرة واحدة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الغياب المتصل دون إذن كتابي، أو عذر مقبول من يومين إلى ستة أيام، خلال السنة العقدية الواحدة.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'أربعة أيام',
            'Fourth_penality': 'الحرمان من الترقيات، أو العلاوات لمرة واحدة',
            'note': 'بالإضافة إلى حسم أجر مدة الغياب',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الغياب المتصل دون إذن كتابي، أو عذر مقبول من سبعة أيام إلى عشرة أيام، خلال السنة العقدية الواحدة.',
            'First_penality': 'أربعة أيام',
            'Second_penality': 'خمسة أيام',
            'Third_penality': 'الحرمان من الترقيات، أو العلاوات لمرة واحدة',
            'Fourth_penality': 'فصل من الخدمة مع المكافأة: إذا لم يتجاوز مجموع الغياب (۳۰) يوم',
            'note': 'بالإضافة إلى حسم أجر مدة الغياب',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الغياب المتصل دون إذن كتابي، أو عذر مقبول من أحد عشر يومًا إلى أربعة عشر يومًا، خلال السنة العقدية الواحدة.',
            'First_penality': 'خمسة أيام',
            'Second_penality': 'الحرمان من الترقيات، أو العلاوات لمرة واحدة، مع توجيه إنذار بالفصل طبقًا للمادة (الثمانون) من نظام العمل',
            'Third_penality': 'فصل من الخدمة طبقًا للمادة (الثمانون) من نظام العمل',
            'Fourth_penality': '-------',
            'note': 'بالإضافة إلى حسم أجر مدة الغياب',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الانقطاع عن العمل دون سبب مشروع مدة تزيد على خمسة عشر يومًا متصلة، خلال السنة العقدية الواحدة.',
            'note': 'الفصل دون مكافأة، أو تعويض، على أن يسبقه إنذار كتابي بعد الغياب مدة عشرة أيام، في نطاق حكم المادة (الثمانون) من نظام العمل',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الغياب المتقطع دون سبب مشروع مدداً تزيد في مجموعها على ثلاثين يومًا خلال السنة العقدية الواحدة.',
            'note': 'الفصل دون مكافأة، أو تعويض، على أن يسبقه إنذار كتابي بعد الغياب مدة عشرين يومًا، في نطاق حكم المادة (الثمانون) من نظام العمل.',
            'no_delete': True,
            'slate_id': record.id,
        }]
        worktime_violation = self.env['worktime.violation'].sudo().create(worktime_violation_value)
        organize_violation_value = [{
            'name': 'التواجد دون مبرر في غير مكان العمل المخصص للعامل أثناء وقت الدوام.',
            'First_penality': '10%',
            'Second_penality': '25%',
            'Third_penality': '50%',
            'Fourth_penality': 'يوم',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'استقبال زائرين في غير أمور عمل المنشأة في أماكن العمل، دون إذن من الإدارة.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '15%',
            'Fourth_penality': '25%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'استعمال آلات، ومعدات، وأدوات المنشأة: لأغراض خاصة، دون إذن.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '25%',
            'Fourth_penality': '50%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'تدخل العامل، دون وجه حق في أي عمل ليس في اختصاصه أو لم يعهد به إليه.',
            'First_penality': '50%',
            'Second_penality': 'يوم',
            'Third_penality': 'يومان',
            'Fourth_penality': 'ثلاثة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الخروج، أو الدخول من غير المكان المخصص لذلك.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '15%',
            'Fourth_penality': '25%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الإهمال في تنظيف الآلات، وصيانتها، أو عدم العناية بها، أو عدم التبليغ عما بها من خلل.',
            'First_penality': '50%',
            'Second_penality': 'يوم',
            'Third_penality': 'يومان',
            'Fourth_penality': 'ثلاثة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'عدم وضع أدوات الإصلاح، والصيانة واللوازم الأخرى في الأماكن المخصصة لها، بعد الانتهاء من العمل.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '25%',
            'Third_penality': '50%',
            'Fourth_penality': 'يوم',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'تمزيق، أو إتلاف إعلانات، أو بلاغات إدارة المنشأة.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الإهمال في العهد التي بحوزته، مثال: (سيارات، آلات، أجهزة، معدات، أدوات، ..... الخ).',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الأكل في مكان العمل، أو غير المكان المعد له، أو في غير أوقات الراحة.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '15%',
            'Fourth_penality': '25%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'النوم أثناء العمل.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '25%',
            'Fourth_penality': '50%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'النوم في الحالات التي تستدعي يقظة مستمرة.',
            'First_penality': '50%',
            'Second_penality': 'يوم',
            'Third_penality': 'يومان',
            'Fourth_penality': 'ثلاثة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التسكع، أو وجود العامل في غير مكان عمله، أثناء ساعات العمل.',
            'First_penality': '10%',
            'Second_penality': '25%',
            'Third_penality': '50%',
            'Fourth_penality': 'يوم',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التلاعب في إثبات الحضور، والانصراف.',
            'First_penality': 'يوم',
            'Second_penality': 'يومان',
            'Third_penality': 'الحرمان من الترقيات أو العلاوات لمرة واحدة',
            'Fourth_penality': 'فصل من الخدمة مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'عدم إطاعة الأوامر العادية الخاصة بالعمل، أو عدم تنفيذ التعليمات الخاصة بالعمل، والمعلقة في مكان ظاهر.',
            'First_penality': '25%',
            'Second_penality': '50%',
            'Third_penality': 'يوم',
            'Fourth_penality': 'يومان',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التحريض على مخالفة الأوامر، والتعليمات الخطية الخاصة بالعمل.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التدخين في الأماكن المحظورة، والمعلن عنها للمحافظة على سلامة العمال، والمنشأة.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الإهمال، أو التهاون في العمل الذي قد ينشأ عنه ضرر في صحة العمال، أو سلامتهم، أو في المواد، أو الأدوات، والأجهزة.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        }]
        organize_violation = self.env['organize.violation'].sudo().create(organize_violation_value)
        labor_violation_value = [{
            'name': 'التشاجر مع الزملاء، أو مع الغير، أو إحداث مشاغبات في مكان العمل.',
            'First_penality': 'يوم',
            'Second_penality': 'يومان',
            'Third_penality': 'ثلاثة أيام',
            'Fourth_penality': 'خمسة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'التمارض، أو ادعاء العامل كذبًا أنه أصيب أثناء العمل، أو بسببه.',
            'First_penality': 'يوم',
            'Second_penality': 'يومان',
            'Third_penality': 'ثلاثة أيام',
            'Fourth_penality': 'خمسة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الامتناع عن إجراء الكشف الطبي عند طلب طبيب المنشأة، أو رفض اتباع التعليمات الطبية أثناء العلاج.',
            'First_penality': 'يوم',
            'Second_penality': 'يومان',
            'Third_penality': 'ثلاثة أيام',
            'Fourth_penality': 'خمسة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'مخالفة التعليمات الصحية المعلقة بأماكن العمل.',
            'First_penality': '50%',
            'Second_penality': 'يوم',
            'Third_penality': 'يومان',
            'Fourth_penality': 'خمسة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الكتابة على جدران المنشأة، أو لصق إعلانات عليها.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': '10%',
            'Third_penality': '25%',
            'Fourth_penality': '50%',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'رفض التفتيش الإداري عند الانصراف.',
            'First_penality': '25%',
            'Second_penality': '50%',
            'Third_penality': 'يوم',
            'Fourth_penality': 'يومان',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'عدم تسليم النقود المحصلة لحساب المنشأة في المواعيد المحددة دون تبرير مقبول.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الامتناع عن ارتداء الملابس، والأجهزة المقررة للوقاية وللسلامة.',
            'First_penality': 'إنذار كتابي',
            'Second_penality': 'يوم',
            'Third_penality': 'يومان',
            'Fourth_penality': 'خمسة أيام',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'تعمد الخلوة مع الجنس الآخر في أماكن العمل.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الإيحاء للآخرين بما يخدش الحياء قولًا، أو فعلًا.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الاعتداء على زملاء العمل بالقول، أو الإشارة، أو باستعمال وسائلالاتصال الالكترونية بالشتم، أو التحقير.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الاعتداء بالإيذاء الجسدي على زملاء العمل، أو على غيرهم بطريقة إباحية.',
            'note': 'فصل بدون مكافأة أو إشعار، أو تعويض بموجب المادة (الثمانون)',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'الاعتداء الجسدي، أو القولي، أو بأي وسيلة من وسائل الاتصال الالكترونية على صاحب العمل، أو المدير المسئول، أو أحد الرؤساء أثناء العمل، أو بسببه.',
            'note': 'فصل بدون مكافأة أو إشعار، أو تعويض بموجب المادة (الثمانون)',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'تقديم بلاغ، أو شكوى كيدية.',
            'First_penality': 'ثلاثة أيام',
            'Second_penality': 'خمسة أيام',
            'Third_penality': 'فصل مع المكافأة',
            'Fourth_penality': '------',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'عدم الامتثال لطلب لجنة التحقيق بالحضور.',
            'First_penality': 'يومان',
            'Second_penality': 'ثلاثة أيام',
            'Third_penality': 'خمسة أيام',
            'Fourth_penality': 'فصل مع المكافأة',
            'no_delete': True,
            'slate_id': record.id,
        },{
            'name': 'عدم التقييد بالزي الرسمي المعتمد بالمنشأة',
            'First_penality': 'يوم',
            'Second_penality': 'يومان',
            'Third_penality': 'ثلاثة أيام',
            'Fourth_penality': 'خمسة أيام',
            'no_delete': True,
            'slate_id': record.id,
        }]
        labor_violation = self.env['labor.violation'].sudo().create(labor_violation_value)
        
        product_slate = self.env['product.product'].sudo().search([('name', '=', 'لائحة عمل داخلية')], limit=1)
        product_qwa = self.env['product.product'].sudo().search([('name', '=', 'الرسوم الحكومية لمنصة قوى لاعتماد اللائحة')], limit=1)
        vals = [{
            'name': record.name,
            'partner_id': record.partner_id.id,
            'user_id': record.user_id.id,
            'sale_type': 'خدمات',
            'payment_term_note': 'كامل المبلغ مقدما',
            'state': 'sent',
            }]
        qutation_id = self.env['sale.order'].sudo().create(vals)
        line = [{
            'name': record.service_type_id.name,
            'product_id': product_slate.id,
            'price_unit': record.service_type_id.price,
            'order_id': qutation_id.id,
            'product_uom_qty': 1.0,
            'qty_delivered': 1.0,
            },{
            'name': "المبلغ أعلاه شامل للرسوم الحكومية لمنصة قوى لاعتماد اللائحة وقدرها 3,162.50 ريال.",
            'order_id': qutation_id.id,
            'display_type': "line_note",
            }]
        self.env['sale.order.line'].sudo().create(line)
        record.qutation_id = qutation_id.id
        if record.user_id != self.env.user:
            mail_template = self.env.ref('Internal_slate.new_slate_email_template')
            mail_template.send_mail(record.id, force_send=True,notif_layout='mail.mail_notification_light')        
        return record
    

class worktime_violation(models.Model):
    _name = 'worktime.violation'
    _description = 'مخالفات أوقات العمل'

    name = fields.Text(string="الاسم")
    First_penality = fields.Text(string="أول مرة")
    Second_penality = fields.Text(string="ثاني مرة")
    Third_penality = fields.Text(string="ثالث مرة")
    Fourth_penality = fields.Text(string="رابع مرة")
    note = fields.Text(string="ملاحظة")
    no_delete = fields.Boolean()
    slate_id = fields.Many2one('internal.slate')

    
    def unlink(self):
        for worktime in self:
            if worktime.no_delete:
                raise UserError(('لا يمكنك حذف مخالفة من لائحة نظام العمل'))
        result = super(worktime_violation, self).unlink()
        return result
    
    sequence_no = fields.Integer('م', compute="_sequence_no")
    
    @api.depends('slate_id.worktime_violation')
    def _sequence_no(self):
        for line in self:
            no = 0
            for l in line.slate_id.worktime_violation:
                no += 1
                l.sequence_no = no


class organize_violation(models.Model):
    _name = 'organize.violation'
    _description = 'مخالفات الأنظمة'

    name = fields.Text(string="الاسم")
    First_penality = fields.Text(string="أول مرة")
    Second_penality = fields.Text(string="ثاني مرة")
    Third_penality = fields.Text(string="ثالث مرة")
    Fourth_penality = fields.Text(string="رابع مرة")
    note = fields.Text(string="ملاحظة")
    no_delete = fields.Boolean()
    slate_id = fields.Many2one('internal.slate')

    
    def unlink(self):
        for organize in self:
            if organize.no_delete:
                raise UserError(('لا يمكنك حذف مخالفة من لائحة نظام العمل'))
        result = super(organize_violation, self).unlink()
        return result
    
    
    sequence_no = fields.Integer('م', compute="_sequence_no")
    
    @api.depends('slate_id.organize_violation')
    def _sequence_no(self):
        for line in self:
            no = 0
            for l in line.slate_id.organize_violation:
                no += 1
                l.sequence_no = no

    
class labor_violation(models.Model):
    _name = 'labor.violation'
    _description = 'مخالفات العمال'

    name = fields.Text(string="الاسم")
    First_penality = fields.Text(string="أول مرة")
    Second_penality = fields.Text(string="ثاني مرة")
    Third_penality = fields.Text(string="ثالث مرة")
    Fourth_penality = fields.Text(string="رابع مرة")
    note = fields.Text(string="ملاحظة")
    no_delete = fields.Boolean()
    slate_id = fields.Many2one('internal.slate')

    
    def unlink(self):
        for labor in self:
            if labor.no_delete:
                raise UserError(('لا يمكنك حذف مخالفة من لائحة نظام العمل'))
        result = super(labor_violation, self).unlink()
        return result
    
    sequence_no = fields.Integer('م', compute="_sequence_no")
    
    @api.depends('slate_id.labor_violation')
    def _sequence_no(self):
        for line in self:
            no = 0
            for l in line.slate_id.labor_violation:
                no += 1
                l.sequence_no = no
