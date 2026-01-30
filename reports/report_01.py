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
            date_irr as "Дата проведения ИРР",
            district as "Район",
            cnt_total as "Всего участников",
            cnt_women as "Всего женщин",
            bin as "БИН",
            meeting_format as "Формат встречи",
            case when category='large' then 'Крупный'
			     when category='middle' then 'Средний'
			     when category='small' then 'Малый'
				 else '' end  as "Категория",
            speaker as "ФИО спикера",
            employee as "Исполнитель",
            meeting_place as "Адрес ИРР",
            partners as "Партнеры"
        from list_protocol l
		where l.rfbn_id=case when :rfbn='00' then l.rfbn_id else :rfbn end
		--and l.status=2
        order by district, date_irr
    """

report_name = 'Проведение ИРР'
report_code = 'PROT_01'

HEADER_ROW = 2
DATA_START_ROW = HEADER_ROW + 1
EXCLUDE_COL = "Партнеры"
LINE_HEIGHT = 15


def report_01(rfbn_id: str, filename=f"rep_{report_code}.xlsx"):
	s_date = datetime.datetime.now().strftime("%H:%M:%S")
	log.info('We are in report_01 !')
	output = io.BytesIO()

	params = {'rfbn': rfbn_id[:2]}
	records = select(get_select(),params)
	log.info(f'\tPARAMS: {params}\n\tRECORDS: {records}')

	if not records:
		with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
			workbook  = writer.book
			worksheet = workbook.add_worksheet("Отчет")
			worksheet.write(0, 0, "Нет данных для отображения")
		excel_bytes = output.getvalue()
    
		return Response(
			excel_bytes,
			mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			headers={"Content-Disposition": f"attachment; filename={filename}"}
		)

	with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
		
		df = pd.DataFrame.from_records(records)


		# Преобразования
		# df["Партнеры"] = df["Партнеры"].apply(
		# 	lambda x: ",\n".join(map(str, x)) if isinstance(x, list)
		# 	else str(x) if x
		# 	else ""
		# )
		# df['Дата проведения ИРР'] = pd.to_datetime(df['Дата проведения ИРР'], errors='coerce')
		# for key in ["Всего участников", "Всего женщин"]:
		# 	df[key] = pd.to_numeric(df[key], errors="coerce").astype('Int64')


		df.to_excel(writer, sheet_name="Отчет", index=False, startrow=HEADER_ROW)
		
		### WORKBOOK ###
		workbook  = writer.book
		worksheet = writer.sheets["Отчет"]

		### НАИМЕНОВАНИЕ ОТЧЕТА
		title_name_report = workbook.add_format({ "align": "left", "font_color": "black", "font_size": "14", "valign": "vcenter", "bold": True	})

		worksheet.set_row(0, 50)
		worksheet.set_row(1, 30)

		worksheet.write(0, 0, report_name, title_name_report)
		worksheet.write(0, 6, report_code, title_name_report)

		title_format_it = workbook.add_format({	"align": "right", "valign": "vcenter", "italic": True })

		now = datetime.datetime.now()
		stop_time = now.strftime("%H:%M:%S")

		worksheet.write(1, 6, f'Дата формирования: {now.strftime("%d.%m.%Y ")}({s_date} - {stop_time})', title_format_it)


		### ЗАГОЛОВКИ
		header_format = workbook.add_format({
			"bold": True,
			"align": "center",
			"valign": "vcenter",
			"border": 1,
			"bg_color": "#E0F7FF"
		})

		worksheet.set_row(HEADER_ROW, 50)  

		for col_num, column_name in enumerate(df.columns):
			worksheet.write(HEADER_ROW, col_num, column_name, header_format)
			worksheet.set_column(col_num, col_num, 20)

		### ФОРМАТ ЯЧЕЕК
		cell_format = workbook.add_format({ "text_wrap": True, "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })
		lalign_format = workbook.add_format({ "align": "left", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })
		list_format = workbook.add_format({ "align": "left", "valign": "vjustify", "border": 1, "bg_color": "#f2f2f2" })
		date_format = workbook.add_format({	"num_format": "dd/mm/yyyy", "align": "center", "valign": "vcenter", "border": 1, "bg_color": "#f2f2f2" })

		### АВТОШИРИНА
		for col_num, column_name in enumerate(df.columns):
			if column_name == "Партнеры":
				worksheet.set_column(col_num, col_num, 50) 
				continue

			max_len = max(
				df[column_name].apply(lambda x: len(str(x)) if pd.notna(x) else 0).max(),
				len(column_name)
			) + 4
			worksheet.set_column(col_num, col_num, max_len)


		### ЗАПИСЬ
		for row_num in range(df.shape[0]):

			worksheet.set_row(row_num, 35)  

			for col_num, column_name in enumerate(df.columns):
				value = df.iloc[row_num, col_num]

				if column_name == "Дата проведения ИРР" and pd.notna(value):
						worksheet.write_datetime(
							DATA_START_ROW + row_num,
							col_num,
							value.to_pydatetime(),
							date_format
						)
				elif column_name in ["Всего участников", "Всего женщин"]:
						worksheet.write_number(
							DATA_START_ROW + row_num,
							col_num,
							int(value),
							cell_format
						)
				elif column_name in ["ФИО спикера", "Исполнитель", "Адрес ИРР"]:
						worksheet.write(
							DATA_START_ROW + row_num,
							col_num,
							"" if pd.isna(value) else str(value),
							lalign_format
						)
				elif column_name == EXCLUDE_COL:
						worksheet.write(
							DATA_START_ROW + row_num,
							col_num,
							"" if pd.isna(value) else str(value),
							list_format
						)
				else:
						worksheet.write(
							DATA_START_ROW + row_num,
							col_num,
							"" if pd.isna(value) else str(value),
							cell_format
						)


	log.info(f'REPORT: {report_code}. Формирование отчета {filename} завершено ({s_date} - {stop_time}).')

	excel_bytes = output.getvalue()
	return Response(
		excel_bytes,
		mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		headers={"Content-Disposition": f"attachment; filename={filename}"}
	)
