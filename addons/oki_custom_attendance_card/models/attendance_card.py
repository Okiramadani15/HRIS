
# from odoo import models, fields, api, _
# from datetime import datetime, timedelta
# import pytz

# class OkiAttendanceCard(models.Model):
#     _name = 'oki.attendance.card'
#     _description = 'Attendance Card'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'date_from desc'

#     name = fields.Char(string='Reference', compute='_compute_name', store=True)
#     employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
#     department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True)
#     date_from = fields.Date(string='Date From', required=True, tracking=True)
#     date_to = fields.Date(string='Date To', required=True, tracking=True)
    
#     line_ids = fields.One2many('oki.attendance.card.line', 'card_id', string='Attendance Lines')
    
#     total_worked = fields.Float(string='Total Worked Hours', compute='_compute_totals', store=True)
#     total_late = fields.Float(string='Total Late (Minutes)', compute='_compute_totals', store=True)
#     total_overtime = fields.Float(string='Total Overtime Hours', compute='_compute_totals', store=True)
#     total_alpa = fields.Integer(string='Total Alpa (Days)', compute='_compute_totals', store=True)

#     @api.depends('employee_id', 'date_from', 'date_to')
#     def _compute_name(self):
#         for rec in self:
#             if rec.employee_id and rec.date_from and rec.date_to:
#                 rec.name = f"ATT/{rec.employee_id.name}/{rec.date_from}-{rec.date_to}"
#             else:
#                 rec.name = "New"

#     @api.depends('line_ids.worked_hours', 'line_ids.late_minutes', 'line_ids.overtime_hours', 'line_ids.note')
#     def _compute_totals(self):
#         for rec in self:
#             rec.total_worked = sum(rec.line_ids.mapped('worked_hours'))
#             rec.total_late = sum(rec.line_ids.mapped('late_minutes'))
#             rec.total_overtime = sum(rec.line_ids.mapped('overtime_hours'))
#             rec.total_alpa = len(rec.line_ids.filtered(lambda l: l.note == 'ALPA'))

#     def action_generate_lines(self):
#         self.ensure_one()
#         # Hapus data lama
#         self.line_ids.unlink()
        
#         # Pengaturan Timezone (WIB) karena data mesin biasanya Lokal, Odoo itu UTC
#         tz = pytz.timezone(self.env.user.tz or 'Asia/Jakarta')
        
#         curr_date = self.date_from
#         new_lines = []
        
#         while curr_date <= self.date_to:
#             # 1. Cari data absensi dari mesin (hr.attendance)
#             # Kita cari dari jam 00:00 sampai 23:59 di tanggal tersebut
#             start_of_day = datetime.combine(curr_date, datetime.min.time())
#             end_of_day = datetime.combine(curr_date, datetime.max.time())
            
#             attendances = self.env['hr.attendance'].search([
#                 ('employee_id', '=', self.employee_id.id),
#                 ('check_in', '>=', start_of_day),
#                 ('check_in', '<=', end_of_day)
#             ], order='check_in asc')

#             # Ambil Fingerprint/Face pertama dan terakhir
#             check_in_utc = attendances[0].check_in if attendances else False
#             check_out_utc = attendances[-1].check_out if attendances and attendances[-1].check_out else False
#             worked_hours = sum(attendances.mapped('worked_hours')) if attendances else 0.0

#             # 2. Ambil Jadwal Kerja (Resource Calendar)
#             calendar = self.employee_id.resource_calendar_id
#             theoretical_hours = 0.0
#             late_minutes = 0.0
#             overtime = 0.0
#             note = 'ALPA'
#             is_working_day = False

#             if calendar:
#                 dayofweek = str(curr_date.weekday())
#                 # Cari jadwal di hari tersebut
#                 working_intervals = calendar.attendance_ids.filtered(lambda r: r.dayofweek == dayofweek)
                
#                 if working_intervals:
#                     is_working_day = True
#                     for interval in working_intervals:
#                         theoretical_hours += (interval.hour_to - interval.hour_from)
                        
#                         # Hitung Keterlambatan (Hanya jika ada check_in)
#                         if check_in_utc:
#                             # Konversi Check-in ke WIB untuk dibandingkan dengan jadwal
#                             check_in_wib = pytz.utc.localize(check_in_utc).astimezone(tz)
#                             # Jam masuk di jadwal (misal 08:00)
#                             sched_in_hour = int(interval.hour_from)
#                             sched_in_min = int((interval.hour_from % 1) * 60)
                            
#                             actual_time = check_in_wib.hour + (check_in_wib.minute / 60.0)
#                             if actual_time > interval.hour_from:
#                                 diff = actual_time - interval.hour_from
#                                 late_minutes += (diff * 60)

#             # 3. Tentukan Status & Lembur
#             if attendances:
#                 note = 'HADIR'
#                 if worked_hours > theoretical_hours and is_working_day:
#                     overtime = worked_hours - theoretical_hours
#                 elif not is_working_day:
#                     note = 'LEMBUR LIBUR'
#                     overtime = worked_hours
#             elif not is_working_day:
#                 note = 'OFF'
#                 theoretical_hours = 0.0

#             # 4. Buat Baris Detail
#             new_lines.append((0, 0, {
#                 'date': curr_date,
#                 'check_in': check_in_utc,
#                 'check_out': check_out_utc,
#                 'worked_hours': worked_hours,
#                 'theoretical_hours': theoretical_hours,
#                 'late_minutes': late_minutes,
#                 'overtime_hours': overtime,
#                 'note': note,
#             }))

#             curr_date += timedelta(days=1)

#         self.write({'line_ids': new_lines})
#         return True
    
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import pytz

class OkiAttendanceCard(models.Model):
    _name = 'oki.attendance.card'
    _description = 'Attendance Card'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True)
    date_from = fields.Date(string='Date From', required=True, tracking=True)
    date_to = fields.Date(string='Date To', required=True, tracking=True)
    
    line_ids = fields.One2many('oki.attendance.card.line', 'card_id', string='Attendance Lines')
    
    total_worked = fields.Float(string='Total Worked Hours', compute='_compute_totals', store=True)
    total_late = fields.Float(string='Total Late (Minutes)', compute='_compute_totals', store=True)
    total_overtime = fields.Float(string='Total Overtime Hours', compute='_compute_totals', store=True)
    total_alpa = fields.Integer(string='Total Alpa (Days)', compute='_compute_totals', store=True)

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.date_from and rec.date_to:
                rec.name = f"ATT/{rec.employee_id.name}/{rec.date_from}-{rec.date_to}"
            else:
                rec.name = "New"

    @api.depends('line_ids.worked_hours', 'line_ids.late_minutes', 'line_ids.overtime_hours', 'line_ids.note')
    def _compute_totals(self):
        for rec in self:
            rec.total_worked = sum(rec.line_ids.mapped('worked_hours'))
            rec.total_late = sum(rec.line_ids.mapped('late_minutes'))
            rec.total_overtime = sum(rec.line_ids.mapped('overtime_hours'))
            rec.total_alpa = len(rec.line_ids.filtered(lambda l: l.note == 'ALPA'))

    def action_generate_lines(self):
        self.ensure_one()
        # Hapus data lama
        self.line_ids.unlink()
        
        # Pengaturan Timezone (WIB)
        tz = pytz.timezone(self.env.user.tz or 'Asia/Jakarta')
        
        curr_date = self.date_from
        new_lines = []
        
        while curr_date <= self.date_to:
            # 1. Cari data absensi dari mesin (hr.attendance)
            start_of_day = datetime.combine(curr_date, datetime.min.time())
            end_of_day = datetime.combine(curr_date, datetime.max.time())
            
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', self.employee_id.id),
                ('check_in', '>=', start_of_day),
                ('check_in', '<=', end_of_day)
            ], order='check_in asc')

            check_in_utc = attendances[0].check_in if attendances else False
            check_out_utc = attendances[-1].check_out if attendances and attendances[-1].check_out else False
            worked_hours = sum(attendances.mapped('worked_hours')) if attendances else 0.0

            # 2. Ambil Jadwal Kerja (Resource Calendar)
            calendar = self.employee_id.resource_calendar_id
            theoretical_hours = 0.0
            late_minutes = 0.0
            overtime_sys = 0.0
            note = 'ALPA'
            is_working_day = False

            if calendar:
                dayofweek = str(curr_date.weekday())
                working_intervals = calendar.attendance_ids.filtered(lambda r: r.dayofweek == dayofweek)
                
                if working_intervals:
                    is_working_day = True
                    # Ambil jam masuk pertama dan jam pulang terakhir dari jadwal
                    first_interval = working_intervals[0]
                    last_interval = working_intervals[-1]
                    
                    theoretical_hours = sum(working_intervals.mapped(lambda r: r.hour_to - r.hour_from))
                        
                    if check_in_utc:
                        # --- HITUNG TELAT ---
                        check_in_wib = pytz.utc.localize(check_in_utc).astimezone(tz)
                        actual_in_time = check_in_wib.hour + (check_in_wib.minute / 60.0)
                        
                        if actual_in_time > first_interval.hour_from:
                            diff_in = actual_in_time - first_interval.hour_from
                            late_minutes = diff_in * 60

                        # --- HITUNG LEMBUR SISTEM (Berdasarkan Jam Pulang) ---
                        if check_out_utc:
                            check_out_wib = pytz.utc.localize(check_out_utc).astimezone(tz)
                            actual_out_time = check_out_wib.hour + (check_out_wib.minute / 60.0)
                            
                            # Jika absen pulang > jam pulang jadwal, hitung selisihnya
                            if actual_out_time > last_interval.hour_to:
                                overtime_sys = actual_out_time - last_interval.hour_to

            # 3. Tentukan Status
            if attendances:
                note = 'HADIR'
                if not is_working_day:
                    note = 'LEMBUR LIBUR'
                    overtime_sys = worked_hours
            elif not is_working_day:
                note = 'OFF'
                theoretical_hours = 0.0

            # 4. Buat Baris Detail
            new_lines.append((0, 0, {
                'date': curr_date,
                'check_in': check_in_utc,
                'check_out': check_out_utc,
                'worked_hours': worked_hours,
                'theoretical_hours': theoretical_hours,
                'late_minutes': late_minutes,
                'overtime_sys': overtime_sys,
                'note': note,
            }))

            curr_date += timedelta(days=1)

        self.write({'line_ids': new_lines})
        return True