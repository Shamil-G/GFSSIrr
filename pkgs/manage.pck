create or replace package manage is

  -- Author  : √”—≈…ÕŒ¬_ÿ
  -- Created : 23.01.2026 19:14:39
  -- Purpose : Manage procedures
  
  -- Public type declarations
  
  function get_org_name(i_bin in varchar2) return varchar2;
  
  procedure add_protocol(i_date_irr in date, i_rfbn_id in varchar2, i_district in varchar2, 
                         i_cnt_total in number, i_cnt_women in number, 
                         i_bin in varchar2, i_meeting_format in varchar2, 
                         i_category in varchar2, i_partners in varchar2, i_speaker in varchar2, 
                         i_employee in varchar2, i_meeting_place in varchar2, i_path_photo in varchar2);
                         
  procedure update_protocol(i_prot_num in varchar2, i_date_irr in date, i_rfbn_id in varchar2, i_district in varchar2, 
                         i_cnt_total in number,i_cnt_women in number, 
                         i_bin in varchar2, i_meeting_format in varchar2, 
                         i_category in varchar2, i_partners in varchar2, i_speaker in varchar2, 
                         i_employee in varchar2, i_meeting_place in varchar2, i_path_photo in varchar2);
                         

  procedure set_action(i_action in varchar2, i_prot_num in varchar2, top_level in number);

end manage;
/
create or replace package body manage is


  procedure log(imess in varchar2)
  is
    PRAGMA AUTONOMOUS_TRANSACTION;
  begin
   insert into log(msg) values(imess);
   commit;
  end;

  function get_org_name(i_bin in varchar2) return varchar2
  is
    nm varchar2(512) default '';
  begin
    select p_name into nm from loader.pmpd_pay_doc pd where p_rnn=i_bin and rownum=1;
    log('get_org_name. BIN: '||i_bin||', NM: '||nm);
    return nm;
    exception when no_data_found then
      select o.nm_ru into nm
      from loader.rfon_organization o
      where o.bin=i_bin and rownum=1;
      log('get_org_name. BIN: '||i_bin||', NM: '||nm);
      return nm;
    when others then return '';
  end;
  
  function get_prot_num(i_rfbn in varchar2, i_date_irr in date) return varchar2
  is
    seq_number pls_integer default 0;
  begin
    select count(prot_num) 
    into seq_number
    from list_protocol lp 
    where substr(lp.prot_num,1,8)=substr(i_rfbn,1,2)||'-'||to_char(i_date_irr, 'YY')||'-'||to_char(i_date_irr, 'MM');
    
    return substr(i_rfbn,1,2)||'-'||to_char(i_date_irr, 'YY')||'-'||to_char(i_date_irr, 'MM')||'-'||(seq_number+1);
  end get_prot_num;
  
  procedure add_protocol(i_date_irr in date, i_rfbn_id in varchar2, 
                         i_district in varchar2, i_cnt_total in number,
                         i_cnt_women in number, i_bin in varchar2, i_meeting_format in varchar2, 
                         i_category in varchar2, i_partners in varchar2, i_speaker in varchar2, 
                         i_employee in varchar2, i_meeting_place in varchar2, i_path_photo in varchar2)
  is
    v_prot_num list_protocol.prot_num%type;
  begin
    v_prot_num:=get_prot_num(i_rfbn_id, i_date_irr);
    
    insert into list_protocol(date_op, prot_num, date_irr, status, rfbn_id, district, cnt_total,
                         cnt_women, bin, meeting_format, category, partners, speaker, employee,
                         meeting_place, path_photo)
    values( sysdate, v_prot_num, i_date_irr, 0, substr(i_rfbn_id,1,2), i_district, 
            i_cnt_total, i_cnt_women, i_bin, i_meeting_format, i_category, i_partners, 
            i_speaker, i_employee, i_meeting_place, i_path_photo);
    commit;
  end add_protocol;


  procedure update_protocol(i_prot_num in varchar2, i_date_irr in date, i_rfbn_id in varchar2, 
                         i_district in varchar2, i_cnt_total in number,
                         i_cnt_women in number, i_bin in varchar2, i_meeting_format in varchar2, 
                         i_category in varchar2, i_partners in varchar2, i_speaker in varchar2, 
                         i_employee in varchar2, i_meeting_place in varchar2, i_path_photo in varchar2)
  is
  begin
    log('update_protocol. i_path_photo: "'||i_path_photo||'"');
    
    update list_protocol l
           set l.date_irr=case when i_date_irr is not null then i_date_irr else l.date_irr end, 
               l.status=0,
               l.rfbn_id=case when i_rfbn_id is not null then i_rfbn_id else l.rfbn_id end, 
               l.district=case when i_district is not null then i_district else l.district end, 
               l.cnt_total=case when i_cnt_total is not null then i_cnt_total else l.cnt_total end,
               l.cnt_women=case when i_cnt_women is not null then i_cnt_women else l.cnt_women end, 
               l.bin=case when i_bin is not null then i_bin else l.bin end,
               l.meeting_format=case when i_meeting_format is not null then i_meeting_format else l.meeting_format end, 
               l.category=case when i_category is not null then i_category else l.category end, 
               l.partners=case when i_partners is not null then i_partners else l.partners end,
               l.speaker=case when i_speaker is not null then i_speaker else l.speaker end, 
               l.employee=case when i_employee is not null then i_employee else l.employee end,
               l.meeting_place=case when i_meeting_place is not null then i_meeting_place else l.meeting_place end, 
               l.path_photo=case when i_path_photo is not null then i_path_photo else l.path_photo end
    where l.prot_num=i_prot_num;
    commit;
  end update_protocol;


  procedure set_action(i_action in varchar2, i_prot_num in varchar2, top_level in number) 
  is
  begin
    if i_action='approve' and top_level in (1,2) then
        update list_protocol l set l.status=2 where l.prot_num=i_prot_num;
    end if;

    if i_action='finalize' and top_level in (1,2) then
        update list_protocol l set l.status=1 where l.prot_num=i_prot_num;
    end if;

    if i_action='remove' and top_level in (1,2) then
        delete from list_protocol l where l.prot_num=i_prot_num;
    end if;

    commit;
  end set_action;
  

begin
  null;
end manage;
/
