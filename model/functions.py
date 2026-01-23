from db.connect import get_connection, select_one, plsql_execute_s
from main_app   import log
from datetime import datetime


def get_list_rayons(rfbn_id):
    stmt = f"""
        select rfbn_id, name
        from loader.branch b 
        where substr(b.rfbn_id,1,2)||'00'=:rfbn_id
        and   substr(b.rfbn_id,3)!='00'
    """
    full_stmt = f"""
        select rfbn_id, name
        from loader.branch b 
    """
    log.debug(f'GET LIST RAYONS')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if rfbn_id!='0000':
                args = {'rfbn_id': rfbn_id}
                cursor.execute(stmt, args)
            else:
                cursor.execute(full_stmt)
            result = {}
            records = cursor.fetchall()
            for rec in records:
                result[rec[0]] = rec[1]
            log.debug(f'------ GET LIST RAYONS. RESULT:\n\t{result}')
            return result


def get_partners():
    stmt = f"""
        select code, value from params where param_name='partner'
    """
    log.debug(f'GET PARTNERS')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(stmt)
            result = {}
            records = cursor.fetchall()
            for rec in records:
                result[rec[0]] = rec[1]
            log.info(f'------ GET PARTNERS. RESULT:\n\t{result}')
            return result


def get_org_name(bin: str)->str:
    stmt = "select p_name from loader.pmpd_pay_doc pd where p_rnn=:bin and rownum=1"
    args={'bin': bin}
    status, rec, err_message = select_one(stmt, args)
    log.info(f'------ GET ORG NAME. STATUS: {status}, RESULT: {rec}')
    if status=='fail' or rec==None:
        log.info(f'*** GET ORG NAME\n\tSTATUS: {status}\n\tERROR: {err_message}\n\t***')
        return {'name': ''}
    return {'name': rec}


def add_protocol(data: dict):
    cmd="""
    begin manage.add_protocol(:meet_date, :region, :district, :participants_total, 
                                :participants_women, :bin, :meeting_format,
                                :business_category, :partners, :speaker_fio, :employee,
                                :meeting_place, :photo_path); end;
    """

    if 'bin' not in data:
        data['bin']=''
    if 'business_category' not in data:
        data['business_category']=''
    if 'meeting_place' not in data:
        data['meeting_place']=''
    data['meet_date']=datetime.strptime(data['meet_date'], "%Y-%m-%d").date()
    if 'organization_name' in data:
        data.pop('organization_name')
    plsql_execute_s('ADD_PROTOCOL', cmd, data)
