from db.connect import get_connection
from main_app   import log


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
