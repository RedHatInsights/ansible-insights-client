from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        results = super(ActionModule, self).run(tmp, task_vars)
        results = merge_hash(results, self._execute_module(module_name="insights", tmp=tmp, task_vars=task_vars))
        results.update({
            "shi": "kaka"
        })
        return results
