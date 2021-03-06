'''
request.py
~~~~~~~~~~~

Read information from the environ of WSGI and convert it.

'''
import re
import base64
from cgi import FieldStorage
import traceback

from erweb import erweb_config as app_config
from erweb.cookie import get_cookies
from erweb.encrypt import de_xor_str
from erweb.session import Session

###############################################################################
####### Request ###############################################################
###############################################################################

class Request():

    def __init__(self,env):
        self._env = env
        self.POST = {}
        self.FILE = {}
        
        tmp = re.split("[&=]",env.get('QUERY_STRING','').strip()) or []
        self.GET = dict(zip(tmp[::2],tmp[1::2]))

        tmp = re.split("[;=]",env.get('HTTP_COOKIE',"").replace(" ",""))
        self._COOKIES = dict(zip(tmp[::2],tmp[1::2]))
        self.COOKIES = get_cookies(self._COOKIES)
        
        try:
            self.SESSION_ID = int(self.COOKIES["session_id"])
        except :
            self.SESSION_ID = 0
        
        self.session = Session(self.SESSION_ID)

        if self.SESSION_ID == 0:
            self.SESSION_ID = - self.session.session_id

        try:
            _request_body_size = int(env.get('CONTENT_LENGTH',"") or 0)
        except (ValueError):
            _request_body_size = 0
        try:
            self._POST = FieldStorage(fp=self._env.get("wsgi.input"), environ=self._env, keep_blank_values=True)
            for k in self._POST.keys():
                if k in self._POST and self._POST[k].filename:
                    self.FILE[k] = (self._POST[k].filename,self._POST.getvalue(k))
                else:
                    self.POST[k] = self._POST.getvalue(k)
        except Exception:
            traceback.print_exc()
            self.POST = {}

    @property
    def METHOD(self):
        return self._env.get('REQUEST_METHOD',"")
    
    @property
    def SERVER_PROTOCOL(self):
        return self._env.get('SERVER_PROTOCOL',"")
    
    @property
    def ACCEPT(self):
        return self._env.get('HTTP_ACCEPT',"")

    @property
    def ACCEPT_ENCODING(self):
        return self._env.get('HTTP_ACCEPT_ENCODING',"")

    @property
    def ACCEPT_LANGUAGE(self):
        return self._env.get('HTTP_ACCEPT_LANGUAGE',"")

    @property
    def USER_AGENT(self):
        return self._env.get('HTTP_USER_AGENT','')
    
    @property
    def URL(self):
        return re.sub("\\?.*$","",self._env.get('RAW_URI',""))
    
    @property
    def REMOTE_IP(self):
        return str(self._env.get('REMOTE_ADDR',""))+':'+str(self._env.get('REMOTE_PORT',""))

    

