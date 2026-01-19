from odoo import models, fields, api
import pytz

class OkiAttendanceCardLine(models.Model):
    _name = 'oki.attendance.card.line'
    _description = 'Oki Kartu Absensi Detail'
    _order = 'date'

    card_id = fields.Many2one('oki.attendance.card', string='Header Kartu', ondelete='cascade', index=True)
    date = fields.Date(string='Tanggal')
    
    check_in = fields.Datetime(string='Check In (UTC)')
    check_out = fields.Datetime(string='Check Out (UTC)')
    
    # Field display untuk tampilan di list view agar WIB (tidak selisih 7 jam)
    display_check_in = fields.Char(string='Masuk', compute='_compute_display_time')
    display_check_out = fields.Char(string='Keluar', compute='_compute_display_time')

    theoretical_hours = fields.Float(string='Jadwal (Jam)')
    worked_hours = fields.Float(string='Kerja (Jam)')
    
    # LOGIKA KETERLAMBATAN
    late_minutes = fields.Float(string='Telat (Menit)', default=0.0)
    
    # LOGIKA LEMBUR
    overtime_sys = fields.Float(string='Lembur (Sistem)', help="Lembur otomatis dari hasil hitung jam kerja")
    overtime_adj = fields.Float(string='Lembur (Adj)', help="Input manual jika ada penyesuaian")
    overtime_hours = fields.Float(string='Total Lembur', compute='_compute_total_overtime', store=True)
    
    note = fields.Char(string='Keterangan')

    @api.depends('overtime_sys', 'overtime_adj')
    def _compute_total_overtime(self):
        for rec in self:
            # Menggabungkan lembur sistem dan manual
            rec.overtime_hours = rec.overtime_sys + rec.overtime_adj

    def _compute_display_time(self):
        # Mengambil timezone dari user profile atau default ke Jakarta
        tz_name = self.env.user.tz or 'Asia/Jakarta'
        context_tz = pytz.timezone(tz_name)
        for rec in self:
            # Konversi check_in ke zona waktu lokal untuk tampilan
            if rec.check_in:
                local_in = pytz.utc.localize(rec.check_in).astimezone(context_tz)
                rec.display_check_in = local_in.strftime('%H:%M')
            else:
                rec.display_check_in = '--:--'
            
            # Konversi check_out ke zona waktu lokal untuk tampilan
            if rec.check_out:
                local_out = pytz.utc.localize(rec.check_out).astimezone(context_tz)
                rec.display_check_out = local_out.strftime('%H:%M')
            else:
                rec.display_check_out = '--:--'