from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


def update_code(module_location):
    """
    Let's just see if we can execute a module "generated" on-the-fly by an
    action plugin
    """
    with open("insights/insights.py") as fp:
        content = fp.read()
    content = content.replace("regoob", "Content updated!")
    with open(module_location, "w") as fp:
        fp.write(content)


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        results = super(ActionModule, self).run(tmp, task_vars)
        module_location = self._shared_loader_obj.module_loader.find_plugin("insights")
        update_code(module_location)
        results = merge_hash(results, self._execute_module(module_name="insights", tmp=tmp, task_vars=task_vars))
        results.update({
            "shi": "kaka"
        })
        return results
