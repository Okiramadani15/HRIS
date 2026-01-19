
# from odoo import models
# from datetime import datetime
# import pytz

# class OkiAttendanceCardXlsx(models.AbstractModel):
#     _name = 'report.oki_custom_attendance_card.report_attendance_xlsx'
#     _inherit = 'report.report_xlsx.abstract'

#     def generate_xlsx_report(self, workbook, data, cards):
#         sheet = workbook.add_worksheet('Rekap Absensi')
#         sheet.freeze_panes(8, 3)
        
#         tz_name = self.env.user.tz or 'Asia/Jakarta'
#         context_tz = pytz.timezone(tz_name)

#         # STYLES
#         title_style = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Arial'})
#         header_style = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#4472C4', 'font_color': 'white'})
#         dept_style = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
#         cell_style = workbook.add_format({'border': 1, 'align': 'center', 'font_size': 9})
#         date_style = workbook.add_format({'border': 1, 'align': 'center', 'num_format': 'dd-mm-yyyy', 'font_size': 9})
#         absent_style = workbook.add_format({'border': 1, 'align': 'center', 'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'font_size': 9})
        
#         # Summary Styles
#         sum_header_style = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#F2F2F2', 'font_size': 9})
#         sum_val_style = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'font_size': 9})
#         sign_style = workbook.add_format({'bold': True, 'align': 'center'})

#         # HEADER ATAS
#         sheet.merge_range('A1:H1', 'PT KARYABHAKTI MANUNGGAL - MILL 2', title_style)
#         sheet.merge_range('A2:H2', 'LAPORAN REKAPITULASI ABSENSI KARYAWAN', workbook.add_format({'bold': True, 'font_size': 11}))
#         sheet.write('A4', f"Dicetak pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}", workbook.add_format({'italic': True, 'font_size': 8}))

#         # Looping Data
#         sorted_cards = cards.sorted(key=lambda r: (r.department_id.name or '', r.employee_id.name))
#         current_dept = None
#         row = 6

#         for card in sorted_cards:
#             if card.department_id != current_dept:
#                 current_dept = card.department_id
#                 row += 1
#                 sheet.merge_range(row, 0, row, 7, f" DEPARTEMEN: {current_dept.name or 'N/A'}", dept_style)
#                 row += 1
#                 headers = ['ID REG', 'NAMA KARYAWAN', 'TANGGAL', 'HARI', 'MASUK', 'PULANG', 'LEMBUR', 'KETERANGAN']
#                 for col, header in enumerate(headers):
#                     sheet.write(row, col, header, header_style)
#                 row += 1

#             for line in card.line_ids:
#                 is_alpa = line.note == 'ALPA'
#                 curr_style = absent_style if is_alpa else cell_style
                
#                 emp_id = getattr(card.employee_id, 'barcode', '-') or getattr(card.employee_id, 'pin', '-')
                
#                 sheet.write(row, 0, emp_id, cell_style)
#                 sheet.write(row, 1, card.employee_id.name, cell_style)
#                 sheet.write(row, 2, line.date, date_style)
#                 sheet.write(row, 3, line.date.strftime('%A'), curr_style)
#                 sheet.write(row, 4, self._fmt_time(line.check_in, context_tz), curr_style)
#                 sheet.write(row, 5, self._fmt_time(line.check_out, context_tz), curr_style)
#                 sheet.write(row, 6, line.overtime_hours or 0, cell_style)
#                 sheet.write(row, 7, line.note or '', curr_style)
#                 row += 1
            
#             # --- BAGIAN SUMMARY PER KARYAWAN ---
#             sheet.write(row, 1, "TOTAL HADIR", sum_header_style)
#             sheet.write(row, 2, f"{card.total_hadir} Hari", sum_val_style)
#             row += 1
#             sheet.write(row, 1, "TOTAL ALPA", sum_header_style)
#             sheet.write(row, 2, f"{card.total_alpa} Hari", sum_val_style)
#             row += 1
#             sheet.write(row, 1, "TOTAL LEMBUR", sum_header_style)
#             sheet.write(row, 2, f"{card.total_lembur} Jam", sum_val_style)
#             row += 1
#             sheet.write(row, 1, "TOTAL TELAT", sum_header_style)
#             sheet.write(row, 2, f"{card.total_telat} Menit", sum_val_style)
#             row += 2 # Jarak antar karyawan

#         # FOOTER TANDA TANGAN (Hanya muncul sekali di akhir dokumen)
#         row += 1
#         sheet.write(row, 1, 'Prepared by,', sign_style)
#         sheet.write(row, 4, 'Checked by,', sign_style)
#         sheet.write(row, 7, 'Approved by,', sign_style)
        
#         row += 4
#         sheet.write(row, 1, '( Admin HRD )', sign_style)
#         sheet.write(row, 4, '( Manager HRD )', sign_style)
#         sheet.write(row, 7, '( Factory Manager )', sign_style)

#         sheet.set_column('A:A', 10)
#         sheet.set_column('B:B', 25)
#         sheet.set_column('C:D', 12)
#         sheet.set_column('H:H', 22)

#     def _fmt_time(self, dt, tz):
#         if not dt: return ''
#         local_dt = dt.replace(tzinfo=pytz.utc).astimezone(tz)
#         return local_dt.strftime('%H:%M')
        
from odoo import models
from datetime import datetime
import pytz

class OkiAttendanceCardXlsx(models.AbstractModel):
    _name = 'report.oki_custom_attendance_card.report_attendance_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, cards):
        sheet = workbook.add_worksheet('Rekap Absensi')
        sheet.freeze_panes(8, 3) # Mengunci kolom Nama agar tetap terlihat saat scroll ke kanan
        
        tz_name = self.env.user.tz or 'Asia/Jakarta'
        context_tz = pytz.timezone(tz_name)

        # --- STYLES ---
        title_style = workbook.add_format({'bold': True, 'font_size': 14, 'font_name': 'Arial'})
        header_style = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#4472C4', 'font_color': 'white'})
        dept_style = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
        cell_style = workbook.add_format({'border': 1, 'align': 'center', 'font_size': 9})
        date_style = workbook.add_format({'border': 1, 'align': 'center', 'num_format': 'dd-mm-yyyy', 'font_size': 9})
        absent_style = workbook.add_format({'border': 1, 'align': 'center', 'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'font_size': 9})
        
        # Summary Styles
        sum_header_style = workbook.add_format({'bold': True, 'border': 1, 'bg_color': '#F2F2F2', 'font_size': 9})
        sum_val_style = workbook.add_format({'bold': True, 'border': 1, 'align': 'center', 'font_size': 9})
        sign_style = workbook.add_format({'bold': True, 'align': 'center'})

        # --- HEADER ATAS ---
        sheet.merge_range('A1:H1', 'PT KARYABHAKTI MANUNGGAL - MILL 2', title_style)
        sheet.merge_range('A2:H2', 'LAPORAN REKAPITULASI ABSENSI KARYAWAN', workbook.add_format({'bold': True, 'font_size': 11}))
        sheet.write('A4', f"Dicetak pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}", workbook.add_format({'italic': True, 'font_size': 8}))

        # --- LOOPING DATA ---
        # Diurutkan berdasarkan Departemen lalu Nama Karyawan
        sorted_cards = cards.sorted(key=lambda r: (r.department_id.name or '', r.employee_id.name))
        current_dept = None
        row = 6

        for card in sorted_cards:
            # Grouping per Departemen
            if card.department_id != current_dept:
                current_dept = card.department_id
                row += 1
                sheet.merge_range(row, 0, row, 7, f" DEPARTEMEN: {current_dept.name or 'N/A'}", dept_style)
                row += 1
                headers = ['ID REG', 'NAMA KARYAWAN', 'TANGGAL', 'HARI', 'MASUK', 'PULANG', 'LEMBUR', 'KETERANGAN']
                for col, header in enumerate(headers):
                    sheet.write(row, col, header, header_style)
                row += 1

            for line in card.line_ids:
                is_alpa = line.note == 'ALPA'
                curr_style = absent_style if is_alpa else cell_style
                
                # Mengambil Barcode atau PIN sebagai ID REG
                emp_id = getattr(card.employee_id, 'barcode', '-') or getattr(card.employee_id, 'pin', '-') or '-'
                
                sheet.write(row, 0, emp_id, cell_style)
                sheet.write(row, 1, card.employee_id.name, cell_style)
                sheet.write(row, 2, line.date, date_style)
                # strftime('%A') akan menghasilkan nama hari dalam bahasa Inggris
                sheet.write(row, 3, line.date.strftime('%A'), curr_style)
                sheet.write(row, 4, self._fmt_time(line.check_in, context_tz), curr_style)
                sheet.write(row, 5, self._fmt_time(line.check_out, context_tz), curr_style)
                sheet.write(row, 6, line.overtime_hours or 0, cell_style)
                sheet.write(row, 7, line.note or '', curr_style)
                row += 1
            
            # --- BAGIAN SUMMARY PER KARYAWAN ---
            # Menghitung Total Hadir: Total baris dikurang Alpa & Off
            total_hadir = len(card.line_ids.filtered(lambda l: l.note not in ['ALPA', 'OFF']))
            
            sheet.write(row, 1, "TOTAL HADIR", sum_header_style)
            sheet.write(row, 2, f"{total_hadir} Hari", sum_val_style)
            row += 1
            sheet.write(row, 1, "TOTAL ALPA", sum_header_style)
            sheet.write(row, 2, f"{card.total_alpa} Hari", sum_val_style)
            row += 1
            sheet.write(row, 1, "TOTAL LEMBUR", sum_header_style)
            sheet.write(row, 2, f"{card.total_overtime} Jam", sum_val_style)
            row += 1
            sheet.write(row, 1, "TOTAL TELAT", sum_header_style)
            sheet.write(row, 2, f"{card.total_late} Menit", sum_val_style)
            row += 2 # Memberikan jarak antar karyawan agar lebih rapi

        # --- FOOTER TANDA TANGAN ---
        row += 1
        sheet.write(row, 1, 'Prepared by,', sign_style)
        sheet.write(row, 4, 'Checked by,', sign_style)
        sheet.write(row, 7, 'Approved by,', sign_style)
        
        row += 4
        sheet.write(row, 1, '( Admin HRD )', sign_style)
        sheet.write(row, 4, '( Manager HRD )', sign_style)
        sheet.write(row, 7, '( Factory Manager )', sign_style)

        # Pengaturan Lebar Kolom
        sheet.set_column('A:A', 10) # ID REG
        sheet.set_column('B:B', 25) # NAMA
        sheet.set_column('C:D', 12) # TANGGAL & HARI
        sheet.set_column('E:F', 10) # MASUK & PULANG
        sheet.set_column('G:G', 10) # LEMBUR
        sheet.set_column('H:H', 22) # KETERANGAN

    def _fmt_time(self, dt, tz):
        """ Fungsi pembantu konversi jam UTC ke WIB untuk Excel """
        if not dt: return '--:--'
        # Pastikan dt adalah datetime object
        if isinstance(dt, datetime):
            local_dt = pytz.utc.localize(dt).astimezone(tz)
            return local_dt.strftime('%H:%M')
        return '--:--'