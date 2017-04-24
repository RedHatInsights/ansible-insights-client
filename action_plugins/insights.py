from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        results = super(ActionModule, self).run(tmp, task_vars)

        # copy our egg
        tmp = self._make_tmp_path()
        source_full = self._loader.get_real_file("falafel-1.35.0-py2.7.egg")
        tmp_src = self._connection._shell.join_path(tmp, 'insights')
        remote_path = self._transfer_file(source_full, tmp_src)

        results = merge_hash(results, self._execute_module(module_args={"egg_path": remote_path}, module_name="insights", tmp=tmp, task_vars=task_vars))
        return results
