#!/usr/bin/python
import sys


def main():
    from ansible.module_utils.basic import AnsibleModule
    module = AnsibleModule({
        "egg_path": {"required": True, "type": "path"}
    })
    sys.path.append(module.params["egg_path"])
    import falafel
    module.exit_json(nvr=falafel.get_nvr())

if __name__ == "__main__":
    main()
