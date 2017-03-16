# Ansible-based Insights Client

Currently just a very basic prototype.  Execute with the following command:

```
ansible '*' -i rhel.ini -m insights -M insights
```

## Glossary

**Client**: The entire package installed on systems that will collect and upload data to Red Hat

**Collector**: The code module downloaded from Red Hat that is executed to collect all data from a target system

**Controller**: A host on which the client package is installed and executed

**Target**: A host on which the collector module is temporarily installed and executed by ansible
