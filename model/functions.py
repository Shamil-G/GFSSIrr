from db.connect import get_connection, select_one, plsql_execute_s, select
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
        select value from params where param_name='partner'
    """
    log.debug(f'GET PARTNERS')
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(stmt)
            result = []
            records = cursor.fetchall()
            for rec in records:
                result.append(rec[0])
            log.info(f'------ GET PARTNERS. RESULT:\n\t{result}')
            return result


def get_org_name(bin: str)->str:
    stmt = "select p_name as name from loader.pmpd_pay_doc pd where p_rnn=:bin and rownum=1"
    args={'bin': bin}
    status, rec, err_message = select_one(stmt, args)
    log.info(f'------ GET ORG NAME. STATUS: {status}, RESULT: {rec}')
    if status=='fail' or rec==None:
        log.info(f'*** GET ORG NAME\n\tSTATUS: {status}\n\tERROR: {err_message}\n\t***')
        return {'name': ''}
    return rec


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


def list_protocol(rfbn, boss):
    cmd="""
        select prot_num, 
               l.status,
               district, 
               b.name,
               cnt_total, cnt_women, 
               speaker, 
               meeting_format,        
               partners, 
               bin, 
               case when bin is null then 'Встреча с населением'
                    else ( select p_name from loader.pmpd_pay_doc pd where pd.p_rnn=bin and rownum=1)
                    end org_name, 
               meeting_place, 
               category, 
               path_photo, 
               employee 
        from list_protocol l, loader.branch b
        where l.district=b.rfbn_id
        and   date_irr>=trunc(sysdate,'YY')
        and   l.rfbn_id = 
                case when substr(:rfbn,1,2)='00' 
                     then l.rfbn_id
                     else substr(:rfbn,1,2)
                end
        order by status asc, date_irr desc               
    """

    args = { 'rfbn': rfbn[0:2]}
    log.info(f'LIST_PROTOCOL: {args}')
    return select(cmd, args)


def set_action(f_name, proc_name, args):
    plsql_execute_s(f_name, proc_name, args)
