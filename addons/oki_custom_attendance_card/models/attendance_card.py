from odoo import models, fields, api, _
from odoo.exceptions import UserError
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
    
    # Field Summary untuk Payroll (Sesuai Blueprint URD)
    total_worked = fields.Float(string='Total Jam Kerja', compute='_compute_totals', store=True)
    total_overtime = fields.Float(string='Total Lembur', compute='_compute_totals', store=True)
    total_alpa = fields.Integer(string='Total Alpa', compute='_compute_totals', store=True)
    total_late = fields.Float(string='Total Telat (Menit)', compute='_compute_totals', store=True)

    @api.depends('employee_id', 'date_from')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.date_from:
                rec.name = f"ATT/{rec.employee_id.name}/{rec.date_from}"
            else:
                rec.name = "New"

    @api.depends('line_ids.worked_hours', 'line_ids.overtime_sys', 'line_ids.note', 'line_ids.late_minutes')
    def _compute_totals(self):
        for rec in self:
            rec.total_worked = sum(rec.line_ids.mapped('worked_hours'))
            rec.total_overtime = sum(rec.line_ids.mapped('overtime_sys'))
            rec.total_alpa = len(rec.line_ids.filtered(lambda l: l.note == 'ALPA'))
            rec.total_late = sum(rec.line_ids.mapped('late_minutes'))

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_generate_lines(self):
        self.ensure_one()
        
        # --- ADDED: SAFETY GUARD ---
        if self.state == 'confirmed':
            raise UserError(_("Data sudah dikunci (Confirmed)! Silakan set ke Draft terlebih dahulu jika ingin generate ulang."))

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

            # 1. CEK JADWAL KERJA & HITUNG THEORETICAL
            calendar = self.employee_id.resource_calendar_id
            expected_in = 0.0
            theoretical_total = 0.0 # ADDED: To capture schedule hours
            is_working_day = False
            
            if calendar:
                work_intervals = calendar._work_intervals_batch(
                    st_utc.replace(tzinfo=pytz.utc), 
                    en_utc.replace(tzinfo=pytz.utc), 
                    self.employee_id.resource_id
                )
                if work_intervals.get(self.employee_id.resource_id.id):
                    is_working_day = True
                    for start, end, meta in work_intervals[self.employee_id.resource_id.id]:
                        # Calculate theoretical hours for the day
                        diff = end - start
                        theoretical_total += diff.total_seconds() / 3600.0
                        
                        # Set expected check-in time
                        if expected_in == 0.0:
                            start_wib = start.astimezone(tz)
                            expected_in = start_wib.hour + (start_wib.minute / 60.0)

            # 2. LOGIKA PEMBULATAN LEMBUR (URD HAL 19)
            overtime_rounded = 0.0
            if spl and spl.hours_requested > 0:
                total_minutes = spl.hours_requested * 60
                full_hours = int(total_minutes // 60)
                rem_minutes = total_minutes % 60
                if rem_minutes >= 30:
                    overtime_rounded = full_hours + 0.5
                else:
                    overtime_rounded = float(full_hours)

            # 3. HITUNG TELAT
            late_min = 0.0
            if attendances and expected_in > 0:
                ci_wib = pytz.utc.localize(attendances[0].check_in).astimezone(tz)
                actual_in = ci_wib.hour + (ci_wib.minute / 60.0)
                if actual_in > (expected_in + 0.001):
                    late_min = (actual_in - expected_in) * 60

            # 4. CEK HOLIDAY
            is_public_holiday = False
            if calendar and calendar.global_leave_ids:
                holidays = calendar.global_leave_ids.filtered(lambda l: l.date_from.date() <= curr_date <= l.date_to.date())
                if holidays:
                    is_public_holiday = True

            # 5. STATUS NOTE
            if attendances:
                note = 'HADIR'
            elif is_public_holiday:
                note = 'HOLIDAY'
            elif not is_working_day:
                note = 'OFF'
            else:
                note = 'ALPA'

            new_lines.append((0, 0, {
                'date': curr_date,
                'check_in': attendances[0].check_in if attendances else False,
                'check_out': attendances[-1].check_out if attendances else False,
                'worked_hours': sum(attendances.mapped('worked_hours')) if attendances else 0.0,
                'theoretical_hours': theoretical_total, # UPDATED: Now filled automatically
                'late_minutes': late_min,
                'overtime_hours': 0.0,
                'overtime_sys': overtime_rounded,
                'overtime_adj': 0.0,
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