from odoo import api, fields, models, tools, SUPERUSER_ID, _
import uuid
import qrcode
from io import BytesIO
import base64


class Document(models.Model):
    _name = 'company.document'
    _description = 'مستندات الشركة'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string='المستند', required=True)
    user_id = fields.Many2one('res.users', string='المستخدم', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one('res.company', string='الشركة', default=lambda self: self.env.company, required=True)
    Text = fields.Html(string='المحتوى')
    qr_invoice = fields.Binary(compute='_generate_qr_code')


    def _default_access_token(self):
        return str(uuid.uuid4())

    access_token = fields.Char('Security Token', required=True, default=_default_access_token, readonly=True)

    def get_qr_code(self, data):
        qr = qrcode.QRCode(
                 version=1,
                 error_correction=qrcode.constants.ERROR_CORRECT_L,
                 box_size=20,
                 border=4,
                 )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_img = base64.b64encode(temp.getvalue())
        return qr_img
    
    def _generate_qr_code(self):
        for document in self:
            base_url = document.company_id.website
            data = base_url + '/company_document/' + str(document.id) + '?access_token=' + str(document.access_token)
            document.qr_invoice = document.get_qr_code(data)
            
    def get_portal_url_pdf_download(self, suffix=None, report_type=None, download=None, query_string=None, anchor=None):
        self.ensure_one()
        base_url = self.company_id.website
        access_url = base_url + '/my/company_document_print/' + str(self.id)
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

