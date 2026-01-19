from odoo import models, fields, api

class OkiOvertimeRequest(models.Model):
    _name = 'oki.overtime.request'
    _description = 'Surat Perintah Lembur'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Field 'name' ditambahkan agar tidak error saat Upgrade
    name = fields.Char(string='Nomor SPL', required=True, copy=False, readonly=True, 
                       index=True, default=lambda self: 'New')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Date', required=True)
    hours_requested = fields.Float(string='Hours Requested', required=True)
    reason = fields.Text(string='Reason')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    # Menambahkan Sequence otomatis sederhana jika belum ada module sequence
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('oki.overtime.request') or 'SPL/' + fields.Date.today().strftime('%Y/%m/%d')
        return super(OkiOvertimeRequest, self).create(vals)

    def action_submit(self):
        for rec in self:
            rec.state = 'to_approve'

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'