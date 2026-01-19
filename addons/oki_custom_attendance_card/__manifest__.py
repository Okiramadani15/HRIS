{
    "name": "Oki - Kartu Absensi",
    "summary": "Kartu Absensi berbasis jadwal kerja dan attendance",
    "version": "18.0.1.0.0",
    "author": "Oki Ramadani",
    "category": "Human Resources",
    "depends": [
        "hr",
        "hr_attendance",
        "hr_holidays",
        "report_xlsx"
    ],
    "data": [
        # "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "wizard/attendance_card_wizard_views.xml",
        "views/attendance_card_views.xml",
        "views/overtime_request_views.xml",
        "views/attendance_card_action.xml",
        "views/menu.xml"
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3"
}