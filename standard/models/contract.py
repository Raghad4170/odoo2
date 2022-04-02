# Copyright to Mutn
from odoo import models, fields, api, _
import uuid


class payment(models.Model):
    _name = 'contract.payment'
    _description = 'الدفعات'    


    name = fields.Integer('No.', compute="_sequence_no")
    
    @api.depends('standard_id.payment')
    def _sequence_no(self):
        for line in self:
            no = 0
            for l in line.standard_id.payment:
                no += 1
                l.name = no

    
    amount = fields.Float(string='قيمة الدفعة')
    amount_discount = fields.Float(string='خصم الدفعة المقدمة')
    issue_date = fields.Date(string='تاريخ الإصدار')
    due_date = fields.Date(string='تاريخ الإستحقاق')
    payment_type = fields.Selection([
            ('معلفة بشرط', 'معلفة بشرط'),
            ('معلفة بتاريخ', 'معلفة بتاريخ'),
            ], string='نوع الدفعة')
    standard_id = fields.Many2one('contract.standard', string='العقد')

class contract(models.Model):
    _name = 'contract.standard'
    _description = 'العقود الموحدة'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    
    
    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/standardcontract_print/' + str(self.id)
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

    name = fields.Char(string="الاسم")
    user_id = fields.Many2one('res.users', string='المسؤول', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one(related='user_id.company_id', string='الشركة')
    partner_id = fields.Many2one('res.partner', string='العميل', required=True)
    date = fields.Date(string='اليوم')
    contract_type = fields.Char(string='نوع العقد')
    contract_purpose = fields.Text(string='الغرض من التعاقد')
    second_speciality = fields.Text(string='إمكانيات الطرف الثاني')

    terms = fields.Text(string='مصطلحات تعريفية')
    contract_period = fields.Char(string='مدة العقد')
    calander = fields.Selection([
            ('ميلادية', 'ميلادية'),
            ('هجرية', 'هجرية'),
            ], string='التقويم')
    start = fields.Date(string='يبدأ من')
    end = fields.Date(string='ينتهي في')
    
    payment_type = fields.Selection([
            ('شهرية', 'شهرية'),
            ('نصف سنوية', 'نصف سنوية'),
            ('سنوية', 'سنوية'),
            ], string='الدفعات')
    amount = fields.Float(string='قيمة العقد')
    contract_calander = fields.Selection([
            ('الهجري', 'الهجري'),
            ('الميلادي', 'الميلادي'),
            ], string='التاريخ المعتمد')
    sides = fields.Selection([
            ('الطرف الأول', 'الطرف الأول'),
            ('الطرف الثاني', 'الطرف الثاني'),
            ], string='المحكم يملكه')
    prove = fields.Char(string="عبء الإثبات على")
    judge = fields.Char(string="مقر التحكيم في مدينة")
    payment = fields.One2many('contract.payment', 'standard_id', string='الدفعات')
    contract_days = fields.Char(string="عدد أيام الإشعار")

    not_saudi = fields.Boolean(string='أحد الأطراف غير سعودي')

    first_side = fields.Many2one('res.partner', string='الطرف الأول')
    company_person = fields.Many2one(related='first_side.author_id', string='ممثل الطرف الأول', readonly=False)
    company_attorney = fields.Selection(related='first_side.author_attorney', string='بموجب ممثل الطرف الأول', readonly=False)
    authorـcompany_no = fields.Char(related='first_side.author_no', string='رقم تفويض ممثل الطرف الأول', readonly=False)
    author_company_date = fields.Date(related='first_side.author_date', string='تاريخ تفويض ممثل الطرف الأول', readonly=False)     
    company_function = fields.Char(related='company_person.function', string='منصب ممثل الطرف الأول', readonly=False)
    company_phone = fields.Char(related='company_person.phone', string='جوال ممثل الطرف الأول', readonly=False)
    first_activity = fields.Char(string='نشاط شركة الطرف الأول')

    second_side = fields.Many2one('res.partner', string='الطرف الثاني')
    author_id = fields.Many2one(related='second_side.author_id', string='ممثل الطرف الثاني', readonly=False)
    author_attorney = fields.Selection(related='second_side.author_attorney', string='بموجب ممثل الطرف الثاني', readonly=False)
    author_no = fields.Char(related='second_side.author_no', string='رقم تفويض ممثل الطرف الثاني', readonly=False)
    author_date = fields.Date(related='second_side.author_date', string='تاريخ تفويض ممثل الطرف الثاني', readonly=False)
    author_function = fields.Char(related='author_id.function', string='منصب ممثل الطرف الثاني', readonly=False)
    author_phone = fields.Char(related='author_id.phone', string='جوال ممثل الطرف الثاني', readonly=False)
    second_activity = fields.Char(string='نشاط شركة الطرف الثاني')

    
    first_side_sign_name = fields.Image(attachment=True, max_width=1024, max_height=1024)
    first_side_sign = fields.Image(attachment=True, max_width=1024, max_height=1024)
    second_side_sign_name = fields.Image(attachment=True, max_width=1024, max_height=1024)
    second_side_sign = fields.Image(attachment=True, max_width=1024, max_height=1024)
    first_witness = fields.Many2one('res.partner', string='الشاهد الأول')
    first_witness_sign_name = fields.Image(attachment=True, max_width=1024, max_height=1024)
    first_witness_sign = fields.Image(attachment=True, max_width=1024, max_height=1024)
    second_witness = fields.Many2one('res.partner', string='الشاهد الثاني')
    second_witness_sign_name = fields.Image(attachment=True, max_width=1024, max_height=1024)
    second_witness_sign = fields.Image(attachment=True, max_width=1024, max_height=1024)

    sides_contract = fields.Text(compute='_get_sides_contract')
                
    def _get_sides_contract(self):
        for contract in self:
            first_side = ''
            first_address = ''
            company_person = ''
            
            second_side = ''
            second_address = ''
            author_id = ''
            
            if contract.first_side:
                first_name = ''
                first_c_form = ''
                first_nationality = ''
                first_company_registry = ''
                first_register_date = ''
                first_city = ''
                first_capital = ''
                first_address = ''

                if contract.first_side.name:
                    first_name = "الطرف الأول: " + contract.first_side.name + ' '
                if contract.first_side.company_form:
                    first_c_form = contract.first_side.company_form + ' '
                if contract.first_side.nationality:
                    first_nationality = contract.first_side.nationality
                if contract.first_side.company_registry:
                    first_company_registry = " والمقيدة بالسجل التجاري رقم " + contract.first_side.company_registry 
                if contract.first_side.register_date:
                    first_register_date = " بتاريخ " + str(contract.first_side.register_date) 
                if contract.first_side.city:
                    first_city = " ومقرها الرئيسي: " + contract.first_side.city
                if contract.first_side.capital:
                    first_capital = " ورأس مالها: " + str(contract.first_side.capital) 
                if contract.first_side.country_id and contract.first_side.city and contract.first_side.street and contract.first_side.street2 and contract.first_side.zip:
                    first_address = " وعنوانها: " + contract.first_side.country_id.name + " - " + contract.first_side.city + " - " + contract.first_side.street + " - " + contract.first_side.street2 + " - " + contract.first_side.zip 
                
                first_side = first_name + first_c_form + first_nationality + first_company_registry + first_register_date + first_city + first_capital + first_address
           
                if contract.company_person:
                    company_person_name = ''
                    company_person_nationality = ''
                    company_person_national = ''
                    cperson_birth_date = ''
                    cperson_phone = ''
                    cperson_email = ''
                    company_function = ''
                    company_attorney = ''
                    authorـcompany_no = ''
                    author_company_date = ''

                    if contract.company_person.name:
                        company_person_name = " ويمثلها في هذا العقد " + contract.company_person.name + ' '
                    if contract.company_person.nationality:
                        company_person_nationality = contract.company_person.nationality
                    if contract.company_person.national_id:
                        company_person_national = " بموجب هوية رقم " + contract.company_person.national_id
                    if contract.company_person.birth_date:
                        cperson_birth_date = " وتاريخ الميلاد " + str(contract.company_person.birth_date)
                    if contract.company_phone:
                        cperson_phone = " وجواله " + contract.company_phone
                    if contract.company_person.email:
                        cperson_email = " وبريده الإلكتروني " + str(contract.company_person.email)
                    if contract.company_function:
                        company_function = " بصفته " + contract.company_function
                    if contract.company_attorney:
                        company_attorney = " وذلك بموجب " + contract.company_attorney
                    if contract.authorـcompany_no:
                        authorـcompany_no = " رقم " + contract.authorـcompany_no
                    if contract.author_company_date:
                        author_company_date = " وتاريخ " + str(contract.author_company_date)
                        
                    company_person = company_person_name + company_person_nationality + company_person_national + cperson_birth_date + cperson_phone + cperson_email + company_function + company_attorney + authorـcompany_no + author_company_date 
            
            if contract.second_side:
                second_name = ''
                second_c_form = ''
                second_nationality = ''
                second_company_registry = ''
                second_register_date = ''
                second_city = ''
                second_capital = ''
                second_address = ''
                if contract.second_side.name:
                    second_name = "الطرف الثاني: " + contract.second_side.name + ' '
                if contract.second_side.company_form:
                    second_c_form = contract.second_side.company_form + ' '
                if contract.second_side.nationality:
                    second_nationality = contract.second_side.nationality
                if contract.second_side.company_registry:
                    second_company_registry = " والمقيدة بالسجل التجاري رقم " + contract.second_side.company_registry 
                if contract.second_side.register_date:
                    second_register_date = " بتاريخ " + str(contract.second_side.register_date) 
                if contract.second_side.city:
                    second_city = " ومقرها الرئيسي: " + contract.second_side.city
                if contract.second_side.capital:
                    second_capital = " ورأس مالها: " + str(contract.second_side.capital) 
                if contract.second_side.country_id and contract.second_side.city and contract.second_side.street and contract.second_side.street2 and contract.second_side.zip:
                    second_address = " وعنوانها: " + contract.second_side.country_id.name + " - " + contract.second_side.city + " - " + contract.second_side.street + " - " + contract.second_side.street2 + " - " + contract.second_side.zip 
                
                second_side = second_name + second_c_form + second_nationality + second_company_registry + second_register_date + second_city + second_capital + second_address
                
                if contract.author_id:
                    author_name = ''
                    author_nationality = ''
                    author_national = ''
                    author_birth_date = ''
                    author_phone = ''
                    author_email = ''
                    author_function = ''
                    author_attorney = ''
                    author_no = ''
                    author_date = ''

                    if contract.author_id.name:
                        author_name = " ويمثلها في هذا العقد " + contract.author_id.name + ' '
                    if contract.author_id.nationality:
                        author_nationality = contract.author_id.nationality
                    if contract.author_id.national_id:
                        author_national = " بموجب هوية رقم " + contract.author_id.national_id
                    if contract.author_id.birth_date:
                        author_birth_date = " وتاريخ الميلاد " + str(contract.author_id.birth_date)
                    if contract.author_phone:
                        author_phone = " وجواله " + contract.author_phone
                    if contract.author_id.email:
                        author_email = " وبريده الإلكتروني " + str(contract.author_id.email)
                    if contract.author_function:
                        author_function = " بصفته " + contract.author_function
                    if contract.author_attorney:
                        author_attorney = " وذلك بموجب " + contract.author_attorney
                    if contract.author_no:
                        author_no = " رقم " + contract.author_no
                    if contract.author_date:
                        author_date = " وتاريخ " + str(contract.author_date)
                
                    author_id = author_name + author_nationality + author_national + author_birth_date + author_phone + author_email + author_function + author_attorney + author_no + author_date             

            the_first = first_side + company_person
            the_second = second_side + author_id
            date = "(اليوم)" 
            contract_type = "(نوع العقد)" 
            if contract.date:
                date = str(contract.date)  
            if contract.contract_type:
                contract_type = contract.contract_type 
         
            start = ("""تم بحمد الله في يوم """ + date + """ توقيع عقد """ + contract_type + """ بين كل من:""") 

            contract.sides_contract = start + '\n' + the_first + '\n' + the_second            
                

    intro = fields.Text(compute='_get_intro', string='تمهيد')
                
    def _get_intro(self):
        for contract in self:
            first_activity = """(يكتب هنا نشاط الشركة الطرف الأول)"""
            contract_purpose = """(يكتب هنا الغرض من التعاقد)"""
            second_activity = """(يكتب هنا نشاط الشركة الطرف الثاني)"""
            second_speciality = """(يكتب هنا إمكانيات الطرف الثاني المتخصصة في محل العقد)"""
            if contract.first_activity:
                first_activity = contract.first_activity
            if contract.contract_purpose:
                contract_purpose = contract.contract_purpose
            if contract.second_activity:
                second_activity = contract.second_activity
            if contract.second_speciality:
                second_speciality = contract.second_speciality

            contract.intro = ("""لما كان الطرف الأول """ + first_activity + """. """ + """ولما كان الطرف الأول لديه الرغبة في التعاقد للقيام بأعمال """ + contract_purpose + """. """ + """ولما كان الطرف الثاني """ + second_activity 
            + """ولديه القدرة على""" + second_speciality + """. """ + """ولما كان الطرفان قد تلاقت إرادتهما للتعاقد للقيام بالأعمال المنصوص عليها في هذا العقد. عليه؛ فقد اتفق الطرفان وهما بكامل أهليتهما القانونية والشرعية على التعاقد وفق الشروط التالية:""") 


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


    standard_1 = fields.Text(compute="get_standard_1", string="تمهيد:")

    def get_standard_1(self):
        for contract in self:
            contract.standard_1 = ("""يعتبر التمهيد أعلاه جزءًا لا يتجزأ من هذا العقد.""") 
                

    standard_2 = fields.Text(compute="get_standard_2", string="التعريفات:")


    def get_standard_2(self):
        for contract in self:
            terms = """(في حال كان هناك مصطلحات تحتاج إلى تعريف أو توضيح)"""
            if contract.terms:
                terms = contract.terms
            contract.standard_2 = ("""يقصد بالمصطلحات التالية في هذا العقد ما يلي: """ + terms) 


    standard_3 = fields.Text(compute="get_standard_3", string="محل العقد:")

    def get_standard_3(self):
        for contract in self:
            contract_purpose = """(يكتب هنا الغرض من العقد)"""
            if contract.contract_purpose:
                contract_purpose = contract.contract_purpose
            contract.standard_3 = ("اتفق الطرفان بموجب هذا العقد على " + contract_purpose) 


            
            
    standard_4 = fields.Text(compute="get_standard_4", string="مدة العقد:")

    def get_standard_4(self):
        for contract in self:
            contract_period = """(يكتب هنا عدد السنوات أو الشهور)"""
            calander = """ميلادية/هجرية"""
            start = """../../"""
            end = """../../"""
            if contract.contract_period:
                contract_period = contract.contract_period
            if contract.calander:
                calander = contract.calander
            if contract.start:
                start = str(contract.start)
            if contract.end:
                end = str(contract.end)
            contract.standard_4 = ("""مدة هذا العقد """ + contract_period + """ """ + calander + """ تبدأ من """ + start + """ وتنتهي في """ + end + """ ويتجدد العقد لمدة أو مدة مماثلة ما لم يشعر أحد الأطراف الآخر رغبته في تجديد العقد.""") 

            
    standard_5 = fields.Text(compute="get_standard_5", string="المقابل المالي:")

    def get_standard_5(self):
        for contract in self:
            amount = "(...)"
            payment_type = "(شهرية/نصف سنوية/ سنوية)"
            if contract.amount:
                amount = str(contract.amount)
            if contract.payment_type:
                payment_type = contract.payment_type
            contract.standard_5 = ("""قيمة هذا العقد """ + amount + """ ريال تدفع على دفعات """ + payment_type + """.""")      
            
    standard_6 = fields.Text(compute="get_standard_6", string="التزامات الطرف الأول:")

    def get_standard_6(self):
        for contract in self:
            contract.standard_6 = ("6.1. يلتزم الطرف الأول بتزويد الطرف الثاني بالمعلومات اللازمة التي تمكنه من تنفيذ التزاماته تجاه الطرف الأول.") 

            
            
    standard_7 = fields.Text(compute="get_standard_7", string="التزامات الطرف الثاني:")

    def get_standard_7(self):
        for contract in self:
            contract.standard_7 = ("7.1. يلتزم الطرف الثاني بأداء المقابل المالي حسب الدفعات المنصوص عليها في البند الخامس.") 

            
            
    standard_8 = fields.Text(compute="get_standard_8", string="فسخ العقد وانتهاءه:")

    def get_standard_8(self):
        for contract in self:
            contract_days = """(تحديد عدد أيام الإشعار)"""
            if contract.contract_days:
                contract_days = contract.contract_days
            contract.standard_8 = ("8.1. ينتهي هذا العقد بانتهاء مدته ما لم يشعر أحد الطرفين الآخر برغبته بالتجديد قبل " + contract_days + " من انتهاء العقد.") 

    standard_8_1 = fields.Text(compute="get_standard_8_1", string="فسخ العقد وانتهاءه (إختيارية):", readonly=False)
    
    def get_standard_8_1(self):
        for contract in self:
            contract.standard_8_1 = ("8.2. يحق (للطرف الأول/ الثاني) فسخ العقد عند إخلال (الطرف الأول/ الثاني) عن تنفيذ التزاماته المنصوص عليها في هذا العقد وفي كل الأحوال يحق للطرف (الأول/ الثاني) الرجوع على الطرف (الأول/ الثاني) بكافة الخسائر المترتبة نتيجة عدم وفائه بالتزاماته." + "\n" + "8.3. ينتهي هذا العقد عند استحالة تنفيذه سواء كان سبب ذلك القوة القاهرة أو الظرف الطارئ أو عند استحالة تنفيذه.") 

    standard_9 = fields.Text(compute="get_standard_9", string="تسوية النزاعات:")

    def get_standard_9(self):
        for contract in self:
            sides = "(الطرف الأول/ الثاني)"
            prove = "(...)"
            judge = "(...)"
            if contract.sides:
                sides = contract.sides
            if contract.prove:
                prove = contract.prove
            if contract.judge:
                judge = contract.judge
            contract.standard_9 = ("9.1. أي منازعة أو خلاف أو مطالبة تنشأ عن هذا العقد أو تتعلق به أو بالإخلال بما فيه أو إنهائه أو بطلانه فيجب على الطرفين حلها بالطرق الودية خلال (15 يومًا) من نشوء النزاع، فإذا تعذر حلها خلال المدة المحددة فيتم الفصل فيها عن طريق محكم فردي يملك " + sides + " تعيينه الذي يحدد النظام الإجرائي والموضوعي على ألا يكون له مصلحة في النزاع ويقر كتابيًا بحياده واستقلاليته ويقع عبء الإثبات على " + prove + " ومقر التحكيم في مدينة " + judge + " وأن يكون التحكيم باللغة العربية وخلال مدة لا تتجاوز شهرين ويتحمل الطرف الخاسر مصاريف التحكيم والمحاماة والخبير إن وجد.") 
            
            
    standard_10 = fields.Text(compute="get_standard_10", string="أحكام عامة:")

    def get_standard_10(self):
        for contract in self:
            contract.standard_10 = ("10.1. عند سكوت أحد طرفي العقد لأي سبب من الأسباب عن إخلال الطرف الآخر بتنفيذه لأحد التزاماته أو التأخر في تنفيذها فإن ذلك لا يعد تعديل أو تنازل لأي بند من بنود هذا العقد ويبقى لكلا الطرفين الحق في مطالبة الطرف الآخر بتلك الالتزامات." + "\n" + "10.2. ينسخ هذا العقد كافة الاتفاقيات والعقود السابقة سواء كانت شفهية أو كتابية، خاصة أو عامة، مقيدة أو مطلقة.") 

    standard_10_1 = fields.Text(compute="get_standard_10_1", string="أحكام عامة (إختيارية):", readonly=False)

    def get_standard_10_1(self):
        for contract in self:
            contract_calander = "(الهجري/ الميلادي)"
            if contract.contract_calander:
                contract_calander = contract.contract_calander
            contract.standard_10_1 = ("10.3. يكون التاريخ المعتمد في هذا العقد هو التاريخ " + contract_calander + "." + "\n" + "10.4.اللغة المعتمدة في هذا العقد هي اللغة العربية." + "\n" 
                                    + "10.5. في حال وجود اختلاف  بين الرقم والكتابة في هذا العقد فإنه يتم اعتماد الرقم المكتوب." + "\n" 
                                    + "10.6. أي تعديل أو إضافة أو إلغاء بند من بنود هذا العقد فإنها تتم عن طريق ملحق للعقد بموافقة وتوقيع طرفيه.") 



    standard_11 = fields.Text(compute="get_standard_11", string="المراسلات، الإشعارات، نسخ العقد:")

    def get_standard_11(self):
        for contract in self:
            contract.standard_11 = ("11.1. تكون المراسلات منتجة لآثارها بين الطرفين إذا تمت على العناوين المعتمدة في صدر هذا العقد ما لم يشعر أحد الطرفين الآخر بتغيير العنوان." + "\n" 
                                    + "11.2. يقر كلا الطرفان بتوقيعهم على هذا العقد بأنهما قد فهما الشروط التي يحتويها وأنهما يمثلان الجهات المذكورة بصدر هذا العقد وإذا تبين لأحد الطرفين عدم الصفة النظامية للطرف الآخر فإنه يحق للطرف المتضرر المطالبة بالتعويض." + "\n" + "11.3. حرر هذا العقد من نسختين تسلم كل طرف نسخة للعمل بموجبها.")