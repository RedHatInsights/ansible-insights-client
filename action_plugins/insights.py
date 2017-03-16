import requests
from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        results = super(ActionModule, self).run(tmp, task_vars)
        results = merge_hash(results, self._execute_module(tmp=tmp, task_vars=task_vars))
        r = requests.get("https://google.com/")
        results.update({
            "shi": "kaka",
            "status_code": str(r.status_code)
        })
        return results
