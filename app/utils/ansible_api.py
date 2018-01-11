#coding:utf8

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
import os


class ResultsCollector(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result,  *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result,  *args, **kwargs):
        self.host_failed[result._host.get_name()] = result

class MyRunner(object):  
    """ 
    This is a General object for parallel execute modules. 
    """  
    def __init__(self, resource,*args, **kwargs):  
        self.resource = resource  
        self.inventory = None  
        self.variable_manager = None  
        self.loader = None  
        self.options = None  
        self.passwords = None  
        self.callback = None  
        self.__initializeData()  
        self.results_raw = {}  
  
    def __initializeData(self):  
        """ 
        初始化ansible 
        """  
        Options = namedtuple('Options', ['connection','module_path', 'forks', 'timeout',  'remote_user',  
                'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',  
                'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass', 'verbosity',  
                'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])  
  
        # initialize needed objects  
        self.variable_manager = VariableManager()  
        self.loader = DataLoader()  
        self.options = Options(connection='smart', module_path='/python2.7_env/lib/python2.7/site-packages/ansible/modules', forks=10, timeout=10,  
                remote_user='root', ask_pass=False, private_key_file=None, ssh_common_args=None, ssh_extra_args=None,  
                sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,  
                become_user='root', ask_value_pass=False, verbosity=None, check=False, listhosts=False,  
                listtasks=False, listtags=False, syntax=False)  
  
        self.passwords = dict(sshpass=None, becomepass=None)  
	self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=self.resource)
        self.variable_manager.set_inventory(self.inventory)

  
    def run(self, module_name, module_args,):  
        """ 
        run module from andible ad-hoc. 
        module_name: ansible module_name 
        module_args: ansible module args 
        """  
        # create play with tasks  
        play_source = dict(  
                name="Ansible Play",  
                hosts='all',  
                gather_facts='no',  
                tasks=[dict(action=dict(module=module_name, args=module_args))]  
        )  
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)  
  
        # actually run it  
        tqm = None  
        self.callback = ResultsCollector()  
        try:  
            tqm = TaskQueueManager(  
                    inventory=self.inventory,  
                    variable_manager=self.variable_manager,  
                    loader=self.loader,  
                    options=self.options,  
                    passwords=self.passwords,  
            )  
            tqm._stdout_callback = self.callback  
            #result = tqm.run(play)
            tqm.run(play)
	except Exception as e:
	    print e
	    pass 
  
    def run_playbook(self, role_name,tomcatname=None,tagname=None,host_list=None):  
        """ 
        run ansible palybook 
        """  
        try:  
            self.callback = ResultsCollector()
	    BASE_DIR="/etc/ansible"
            filenames = [BASE_DIR + '/roles/test.yml'] 
  
            extra_vars = {}     #额外的参数 test.yml以及模板中的参数，它对应ansible-playbook test.yml --extra-vars "host='aa' name='cc' " 
	    if host_list and isinstance(host_list,list):
            	host_list_str = ','.join([item for item in host_list])  
            	extra_vars['host_list'] = host_list_str  
            extra_vars['username'] = role_name  
            extra_vars['tomcatname'] = tomcatname
            extra_vars['tagname'] = tagname
            self.variable_manager.extra_vars = extra_vars  
            executor = PlaybookExecutor(  
                playbooks=filenames, inventory=self.inventory, variable_manager=self.variable_manager, loader=self.loader,  
                options=self.options, passwords=self.passwords,  
            )
            executor._tqm._stdout_callback = self.callback  
            executor.run()
        except Exception as e:
	    print e
	    pass
  
    def get_result(self):  
        self.results_raw = {'success':{}, 'failed':{}, 'unreachable':{}}  
        for host, result in self.callback.host_ok.items():  
            self.results_raw['success'][host] = result._result  
  
        for host, result in self.callback.host_failed.items():  
            self.results_raw['failed'][host] = result._result['msg']  
  
        for host, result in self.callback.host_unreachable.items():  
            self.results_raw['unreachable'][host]= result._result['msg']  
  
        return self.results_raw
