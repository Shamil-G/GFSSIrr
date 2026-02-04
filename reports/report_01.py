import xlsxwriter
import datetime
from   util.logger import log
from	db.connect import select
from  app_config import REPORT_PATH
import pandas as pd
from flask import Response
import io


def get_select():
    return """
		select
			prot_num as "Номер протокола",
			date_irr as "Дата ИРР",
			l.rfbn_id as  "Код области",
			b2.name as "Область",
			b.name as "Район",
			cnt_total as "Всего участников",
			cnt_women as "Всего женщин",
			bin as "БИН",
			(select p_name from loader.pmpd_pay_doc pd where pd.p_rnn=l.bin and rownum=1) as "Наименование предприятия",
			meeting_format as "Формат встречи",
			case when category='large' then 'Крупный'
			when category='medium' then 'Средний'
			when category='small' then 'Малый'
			else '' end  as "Категория бизнеса",
			speaker as "ФИО спикера",
			employee as "Исполнитель",
			meeting_place as "Адрес ИРР",
			partners as "Партнеры"
		from list_protocol l, loader.branch b, loader.branch b2
		where l.rfbn_id=case when :rfbn='00' then l.rfbn_id else :rfbn end
		and  l.district=b.rfbn_id
		and  l.rfbn_id||'00'=b2.rfbn_id
		and l.status=2
		order by prot_num
    """

report_name = 'Проведение ИРР'
report_code = 'PROT_01'

HEADER_ROW = 2
DATA_START_ROW = HEADER_ROW + 1
EXCLUDE_COL = "Партнеры"
LINE_HEIGHT = 15


def report_01(rfbn_id: str, filename=f"rep_{report_code}.xlsx"):
	s_date = datetime.datetime.now().strftime("%H:%M:%S")
	output = io.BytesIO()

	params = {'rfbn': rfbn_id[:2]}
	records = select(get_select(),params)
	log.info(f'\tPARAMS: {params}\n\tRECORDS: {records}')

	with xlsxwriter.Workbook(output, {'in_memory': True}) as workbook:
		worksheet = workbook.add_worksheet("Отчет")

		if not records:
			worksheet.write(0, 0, "Нет данных для отображения")
			excel_bytes = output.getvalue()
    
			return Response(
				excel_bytes,
				mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
				headers={"Content-Disposition": f"attachment; filename={filename}"}
			)

		### ЗАГОЛОВКИ
		title_name_report = workbook.add_format({ "align": "left", "font_color": "black", "font_size": "14", "valign": "vcenter", "bold": True	})
		header_format = workbook.add_format({ "bold": True, "align": "center", "font_size": "12", "valign": "vcenter", "border": 1, "bg_color": "#E0F7FF", "text_wrap": True })
		text_format = workbook.add_format({ "align": "left", "valign": "vjustify", "border": 1, "bg_color": "#f2f2f2" })
		number_format = workbook.add_format({ "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })
		text_format_center = workbook.add_format({ "text_wrap": True, "align": "center", "valign": "vjustify", "border": 1, "bg_color": "#f2f2f2", "num_format": '@' })
		date_format = workbook.add_format({	"num_format": "dd/mm/yyyy", "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })
		title_format_it = workbook.add_format({	"align": "right", "valign": "vcenter", "italic": True })
		list_format = workbook.add_format({ "text_wrap": True, "align": "left", "valign": "vcenter", "border": 1 })
		##
		list_name_number = ['Всего участников', 'Всего женщин']
		list_name_date = ['Дата ИРР']
		list_name_text = ["Наименование предприятия", "Область","Район","ФИО спикера", "Исполнитель", "Адрес ИРР"]
		list_name_text_list = ["Партнеры"]
		list_name_text_center = ["Код области", "БИН", "Категория бизнеса", "Номер протокола", "Формат встречи"]
		list_column_width =[11,12,10,45,45,12,12,14, 60, 12,12,30,40,50,30]
		# Пишем шапку и указываем ширину колонок
		for col_num, column_name in enumerate(records[0]):
			worksheet.write(HEADER_ROW, col_num, column_name, header_format)
			worksheet.set_column(col_num, col_num, list_column_width[col_num])
			log.info(f'{col_num}. CREATE TITLE. {column_name}:{list_column_width[col_num]}')

		worksheet.set_row(0, 24)
		worksheet.set_row(1, 24)
		worksheet.set_row(HEADER_ROW, 50)  

		worksheet.write(0, 0, report_name, title_name_report)
		worksheet.write(0, 11, report_code, title_name_report)

		now = datetime.datetime.now()

		### ЗАПИСЬ
		for row_num, record in enumerate(records):
			# worksheet.write( DATA_START_ROW + row_num, 0, row_num, number_format )
			for col_num, (column_name, value) in enumerate(record.items()):
				if any(column_name.lower() in name.lower() for name in list_name_date):
					worksheet.write( DATA_START_ROW + row_num, col_num, value, date_format )
				if any(column_name.lower() in name.lower() for name in list_name_number):
					worksheet.write( DATA_START_ROW + row_num, col_num, float(value), number_format )
				if any(column_name.lower() in name.lower() for name in list_name_text):
					worksheet.write( DATA_START_ROW + row_num, col_num, value, text_format )
				if any(column_name.lower() in name.lower() for name in list_name_text_center):
					worksheet.write( DATA_START_ROW + row_num, col_num, value, text_format_center )
				if any(column_name.lower() in name.lower() for name in list_name_text_list):
					text='\n'.join(value)
					worksheet.write( DATA_START_ROW + row_num, col_num, text, list_format )

		stop_time = now.strftime("%H:%M:%S")

		worksheet.write(1, 11, f'Дата формирования: {now.strftime("%d.%m.%Y ")}({s_date} - {stop_time})', title_format_it)


	log.info(f'REPORT: {report_code}. Формирование отчета {filename} завершено ({s_date} - {stop_time}).')

	excel_bytes = output.getvalue()
	return Response(
		excel_bytes,
		mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		headers={"Content-Disposition": f"attachment; filename={filename}"}
	)
