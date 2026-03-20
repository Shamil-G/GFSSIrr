import re
from flask import session
from util.ip_addr import ip_addr
from util.logger import log
from app_config import top_post, top_view, middle_post, work_post, tester


def has_invalid_symbols(text: str) -> bool:
    # латиница или цифры
    return bool(re.search(r"[A-Za-z0-9]", text))


class SSO_User:
    def check_tester(self):
        if 'login_name' in tester and tester['login_name']==self.username:
            self.rfbn_id=tester['rfbn_id']
            self.top_level=tester['top_level']
            self.top_view=tester['top_view']

    def get_user_by_name(self, src_user):
        ip = ip_addr()
        self.src_user = src_user
        self.post=''
        self.dep_name=''
        self.roles=''
        self.top_level=0
        self.top_view=0

        if 'password' in session:
            self.password = session['password']
        if src_user and 'login_name' in src_user:
            log.debug(f'SSO_USER. src_user: {src_user}')

            self.username = src_user['login_name']
            session['username'] = self.username
            # Required fields check
            if 'fio' not in src_user:
                log.info(f"---> SSO\n\tUSER {self.username} not Registred\n\tFIO is empty\n<---")
                return None

            if 'dep_name' not in src_user:
                log.info(f"---> SSO\n\tUSER {self.username} not Registred\n\tDEP_NAME is empty\n<---")
                return None

            if 'post' not in src_user:
                log.info(f"---> SSO\n\tUSER {self.username} not Registred\n\tPOST in \n{src_user}\n\tis empty\n<---")
                return None

            # RFBN_ID
            self.rfbn_id=src_user.get('rfbn_id','')
            # dep_name
            self.dep_name = src_user.get('dep_name','')
            session['dep_name']=self.dep_name

            # post
            self.post = src_user.get('post','')
            if has_invalid_symbols(self.post):
                log.info(f"---> SSO\n\tUSER {self.username} имеет в должности {self.post} недействителный символ: не цифры и не кириллица\n<---")
                return

            session['post']=self.post
            # check admin right!
            list_top_dep = top_post.get(self.post,[])
            if self.dep_name in list_top_dep:
                self.roles='TOP'
                self.top_level=2
                self.top_view=1

            if self.top_view==0:
                list_top_view= top_view.get(self.post,[])
                if '*' in list_top_view or self.dep_name in list_top_view:
                    self.top_view=1

            log.debug(f'SSO. list_admin_dep: {list_top_dep}. top_level: {self.top_level}')
            # check user right
            if self.top_level==0:
                list_middle_dep = middle_post.get(self.post,[])
                if '*' in list_middle_dep or self.dep_name in list_middle_dep:
                    self.roles='Head'
                    self.top_level=1

            # check user right
            if self.top_level==0:
                list_work_dep = work_post.get(self.post,[])

                #log.info(f'*** POST: {self.post}\n\tWORK POST: {work_post}\n\tLIST WORK: {list_work_dep}\n***')
                if '*' in list_work_dep or self.dep_name in list_work_dep:
                    self.roles='Operator'
                else:
                    log.info(f'SSO. Undefined ROLE for: {self.username}')
                    return None

            # FIO
            self.fio = src_user.get('fio','')
            session['fio'] = self.fio
            #

            if 'roles' in src_user:
                self.roles.append(src_user['roles'])
                session['roles']=self.roles
                
            session['top_level']=self.top_level
            session['top_view']=self.top_view

            self.full_name = self.fio
            session['full_name'] = self.fio

            self.ip_addr = ip

            self.check_tester()

            log.info(f"--->\n\tSSO SUCCESS\n\tUSERNAME: {self.username}\n\tIP_ADDR: {self.ip_addr}\n\tFIO: {self.fio}" 
                     f"\n\tROLES: {self.roles}\n\tPOST: {self.post}\n\tTOP_VIEW: {self.top_view}\n\tTOP_LEVEL: {self.top_level}"
                     f"\n\tRFBN: {self.rfbn_id}\n\tDEP_NAME: {self.dep_name}\n<---")
            return self
        log.info(f"---> SSO FAIL. USERNAME: {src_user}\n\tip_addr: {ip}, password: {session['password']}\n<---")
        return None

    def have_role(self, role_name):
        if hasattr(self, 'roles'):
            return role_name in self.roles

    def is_authenticated(self):
        if not hasattr(self, 'username'):
            return False
        else:
            return True

    def is_active(self):
        if hasattr(self, 'username'):
            return True
        else:
            return False

    def is_anonymous(self):
        if not hasattr(self, 'username'):
            return True
        else:
            return False

    def get_id(self):
        log.debug(f'LDAP_User. GET_ID. self.src_user: {self.src_user}, self.username: {self.username}')
        if hasattr(self, 'src_user'):
            return self.src_user
        else: 
            return None


if __name__ == "__main__":
    #'bind_dn'       => 'cn=ldp,ou=admins,dc=gfss,dc=kz',
    #'bind_pass'     => 'hu89_fart7',    
    #connect_ldap('Гусейнов', '123')
    log.debug(f'__main__ function')
