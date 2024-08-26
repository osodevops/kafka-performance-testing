# Testing your Apache Kafka cluster with Ansible

The following collection commands are made available by this repo:
```shell
# Testing
ansible-playbook -i inventories/local oso.test.produce_consume       # Test topic produce and consume
ansible-playbook -i  inventories/local oso.test.simple                # Simple Performance test 

# WIP
ansible-playbook -i inventories/dev oso.test.perf_test_[1, 2, ]   # Performance testing entrypoints
ansible-playbook -i inventories/dev oso.test.schema_registry      # Test schema registry is available
```

### Check-mode
**Verify the ansible will do what you expect with the `-C` flag (or `--check`)**


### Testing
#### Configuring tests
Tests parameters are defined in `ansible_collections/oso/test/playbooks/perf_test_*`

To define a new test
- Copy an existing file to a new name (e.g. perf_test_1.yml)
- Tailor the parameters in the file
- Execute the ansible playbook as detailed under `Running ansible`