#!/usr/bin/python


def get_content():
    return {"booger": "Content updated!"}


def noansible():
    import json
    print json.dumps(get_content())


def main():
    from ansible.module_utils.basic import AnsibleModule
    module = AnsibleModule({})
    module.exit_json(**get_content())

if __name__ == "__main__":
    noansible()
