from flask import session
from util.ip_addr import ip_addr
from util.logger import log
from app_config import permit_post, boss_post

     
class SSO_User:
    def get_user_by_name(self, src_user):
        ip = ip_addr()
        self.src_user = src_user
        self.post=''
        self.dep_name=''
        self.roles=''
        self.top_control=0
        self.boss='N'


        if 'password' in session:
            self.password = session['password']
        if src_user and 'login_name' in src_user:
            log.debug(f'SSO_USER. src_user: {src_user}')

            self.username = src_user['login_name']
            session['username'] = self.username
            
            if 'fio' not in src_user:
                log.info(f"---> SSO\n\tUSER {self.username} not Registred\n\tFIO is empty\n<---")
                return None

            if 'dep_name' not in src_user:
                log.info(f"---> SSO\n\tUSER {self.username} not Registred\n\tDEP_NAME is empty\n<---")
                return None

            # post
            if 'post' not in src_user:
                log.info(f"---> SSO\n\tUSER {self.username} not Registred\n\tPOST in \n{src_user}\n\tis empty\n<---")
                return None

            self.post = src_user['post']
            session['post']=self.post

            if self.post in boss_post:
                self.top_control=1
                self.boss='Y'

            if self.boss=='N' and self.post not in permit_post:
                return None

            # RFBN_ID
            self.rfbn_id=src_user.get('rfbn_id','')
            # dep_name
            self.dep_name = src_user.get('dep_name','')
            session['dep_name']=self.dep_name
            self.post = src_user.get('post','')
            session['post']=self.post
            # FIO
            self.fio = src_user.get('fio','')
            session['fio'] = self.fio
            #

            if 'roles' in src_user:
                self.roles = self.roles.append(src_user['roles'])
                session['roles']=self.roles
                
            session['full_name'] = self.fio
            self.full_name = self.fio

            self.ip_addr = ip
            log.info(f"---> SSO SUCCESS\n\tUSERNAME: {self.username}\n\tIP_ADDR: {self.ip_addr}\n\tFIO: {self.fio}\n\tROLES: {self.roles}, POST: {self.post}\n\tDEP_NAME: {self.dep_name}\n<---")
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
        log.debug(f'---> SSO\n\tGET_ID. self.src_user: {self.src_user}, self.username: {self.username}\n<---')
        if hasattr(self, 'src_user'):
            return self.src_user
        else: 
            return None


if __name__ == "__main__":
    #'bind_dn'       => 'cn=ldp,ou=admins,dc=gfss,dc=kz',
    #'bind_pass'     => 'hu89_fart7',    
    #connect_ldap('Гусейнов', '123')
    log.debug(f'__main__ function')
