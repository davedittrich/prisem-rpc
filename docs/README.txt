Fri Aug 18 12:30:39 PDT 2017

This document is designed to be customized using an Ansible inventory
to template the variables for this document, allowing it to be
customized for the specific deployment. This works with the
ansible-dims-playbooks repository version 2.X.X or higher.

https://github.com/uw-dims/ansible-dims-playbooks/

Until this process is more automated, generate
a customized "dimsvars.txt" using this command:

 $ ansible-playbook -i $PBR/inventory \
 > -e host=amqp \
 > -e template_src=$(pwd)/dimsvars.j2 \
 > -e template_dest=$(pwd)/dimsvars.txt \
 > $PBR/playbooks/base_template.yml
