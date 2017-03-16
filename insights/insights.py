#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule({})
    module.exit_json(booger="regoob")

if __name__ == "__main__":
    main()
