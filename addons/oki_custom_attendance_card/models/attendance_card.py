from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz

class OkiAttendanceCard(models.Model):
    _name = 'oki.attendance.card'
    _description = 'Kartu Absensi Karyawan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft', tracking=True)

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    line_ids = fields.One2many('oki.attendance.card.line', 'card_id', string='Lines')
    
    # Field Summary untuk Payroll
    total_worked = fields.Float(string='Total Jam Kerja', compute='_compute_totals', store=True)
    total_overtime = fields.Float(string='Total Lembur', compute='_compute_totals', store=True)
    total_alpa = fields.Integer(string='Total Alpa', compute='_compute_totals', store=True)
    # FIELD BARU: Menghitung total menit keterlambatan
    total_late = fields.Float(string='Total Telat (Menit)', compute='_compute_totals', store=True)

    @api.depends('employee_id', 'date_from')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.date_from:
                rec.name = f"ATT/{rec.employee_id.name}/{rec.date_from}"
            else: rec.name = "New"

    @api.depends('line_ids.worked_hours', 'line_ids.overtime_sys', 'line_ids.note', 'line_ids.late_minutes')
    def _compute_totals(self):
        for rec in self:
            rec.total_worked = sum(rec.line_ids.mapped('worked_hours'))
            rec.total_overtime = sum(rec.line_ids.mapped('overtime_sys'))
            rec.total_alpa = len(rec.line_ids.filtered(lambda l: l.note == 'ALPA'))
            # Menjumlahkan seluruh menit keterlambatan dari detail baris
            rec.total_late = sum(rec.line_ids.mapped('late_minutes'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_generate_lines(self):
        self.ensure_one()
        self.line_ids.unlink()
        tz = pytz.timezone(self.env.user.tz or 'Asia/Jakarta')
        curr_date = self.date_from
        new_lines = []
        
        while curr_date <= self.date_to:
            st_utc = tz.localize(datetime.combine(curr_date, datetime.min.time())).astimezone(pytz.utc).replace(tzinfo=None)
            en_utc = tz.localize(datetime.combine(curr_date, datetime.max.time())).astimezone(pytz.utc).replace(tzinfo=None)
            
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', st_utc),
                ('check_in', '<=', en_utc)
            ], order='check_in asc')
            
            spl = self.env['oki.overtime.request'].search([
                ('employee_id', '=', self.employee_id.id),
                ('date', '=', curr_date),
                ('state', '=', 'approved')
            ], limit=1)

            # Hitung menit telat (Contoh: Jam masuk standar 08:00)
            late_min = 0.0
            if attendances:
                ci_wib = pytz.utc.localize(attendances[0].check_in).astimezone(tz)
                # Jika lewat dari jam 8 (8.0), hitung selisih menitnya
                if ci_wib.hour >= 8 and ci_wib.minute > 0:
                    late_min = ((ci_wib.hour - 8) * 60) + ci_wib.minute

            note = 'ALPA'
            if attendances:
                note = 'HADIR'
            elif curr_date.weekday() == 6:
                note = 'OFF'

            new_lines.append((0, 0, {
                'date': curr_date,
                'check_in': attendances[0].check_in if attendances else False,
                'check_out': attendances[-1].check_out if attendances else False,
                'worked_hours': sum(attendances.mapped('worked_hours')) if attendances else 0.0,
                'late_minutes': late_min,
                'overtime_sys': spl.hours_requested if spl else 0.0,
                'note': note,
            }))
            curr_date += timedelta(days=1)
            
        self.write({'line_ids': new_lines})
        return True

class OkiAttendanceCardLine(models.Model):
    _name = 'oki.attendance.card.line'
    _description = 'Detail Kartu Absensi'
    card_id = fields.Many2one('oki.attendance.card', ondelete='cascade')
    date = fields.Date(string='Tanggal')
    check_in = fields.Datetime(string='Masuk')
    check_out = fields.Datetime(string='Pulang')
    worked_hours = fields.Float(string='Jam Kerja')
    theoretical_hours = fields.Float(string='Jadwal Jam')
    late_minutes = fields.Float(string='Terlambat (Menit)')
    overtime_hours = fields.Float(string='Overtime Hours') 
    overtime_sys = fields.Float(string='Sistem (SPL)')
    overtime_adj = fields.Float(string='Adjustment')
    note = fields.Char(string='Keterangan')