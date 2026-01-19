from odoo import models, fields, api
import pytz

class OkiAttendanceCardLine(models.Model):
    _name = 'oki.attendance.card.line'
    _description = 'Oki Kartu Absensi Detail'
    _order = 'date'

    card_id = fields.Many2one('oki.attendance.card', string='Header', ondelete='cascade')
    date = fields.Date(string='Tanggal')
    check_in = fields.Datetime(string='Check In')
    check_out = fields.Datetime(string='Check Out')
    
    # Field display untuk UI
    display_check_in = fields.Char(string='Masuk', compute='_compute_display_time')
    display_check_out = fields.Char(string='Keluar', compute='_compute_display_time')

    theoretical_hours = fields.Float(string='Jadwal (Jam)')
    worked_hours = fields.Float(string='Kerja (Jam)')
    late_minutes = fields.Float(string='Telat (Menit)')
    
    overtime_sys = fields.Float(string='Sistem (SPL)')
    overtime_adj = fields.Float(string='Adj')
    overtime_hours = fields.Float(string='Total', compute='_compute_total_overtime', store=True)
    note = fields.Char(string='Keterangan')

    @api.depends('overtime_sys', 'overtime_adj')
    def _compute_total_overtime(self):
        for rec in self:
            rec.overtime_hours = rec.overtime_sys + rec.overtime_adj

    def _compute_display_time(self):
        tz = pytz.timezone(self.env.user.tz or 'Asia/Jakarta')
        for rec in self:
            rec.display_check_in = pytz.utc.localize(rec.check_in).astimezone(tz).strftime('%H:%M') if rec.check_in else ''
            rec.display_check_out = pytz.utc.localize(rec.check_out).astimezone(tz).strftime('%H:%M') if rec.check_out else ''