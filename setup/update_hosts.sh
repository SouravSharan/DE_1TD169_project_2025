#!/bin/bash

# Master and worker details
MASTER_IP="192.168.2.127"
MASTER_NAME="group27_vm_v2-1"
MASTER_EXTERNAL_IP="130.238.27.127"

WORKER_IPS="192.168.2.25 192.168.2.158 192.168.2.222 192.168.2.32"
WORKER_NAMES="group27_vm2_worker-1 group27_vm2_worker-2 group27_vm2_worker-3 group27_vm2_worker-4"
WORKER_EXTERNAL_IPS="130.238.27.86 130.238.27.161 130.238.27.56 130.238.27.193"

# Function to update /etc/hosts on a single node
update_hosts() {
    local HOSTS_FILE="/etc/hosts"
    echo "Updating $HOSTS_FILE on $1..."

    # Backup existing hosts file
    sudo cp $HOSTS_FILE $HOSTS_FILE.bak

    # Remove old entries for these hostnames (if any)
    sudo sed -i "/$MASTER_NAME/d" $HOSTS_FILE
    sudo sed -i "/group27_vm2_worker-/d" $HOSTS_FILE

    # Add new entries
    echo "$MASTER_IP $MASTER_NAME" | sudo tee -a $HOSTS_FILE
    i=1
    for ip in $WORKER_IPS; do
        worker_name=$(echo $WORKER_NAMES | cut -d' ' -f$i)
        echo "$ip $worker_name" | sudo tee -a $HOSTS_FILE
        ((i++))
    done
}

# Update master’s /etc/hosts
update_hosts "$MASTER_NAME"

# Propagate to workers
i=1
for ext_ip in $WORKER_EXTERNAL_IPS; do
    worker_name=$(echo $WORKER_NAMES | cut -d' ' -f$i)
    echo "Propagating to $worker_name ($ext_ip)..."
    ssh ubuntu@$ext_ip "sudo bash -c 'cp /etc/hosts /etc/hosts.bak'"  # Backup
    ssh ubuntu@$ext_ip "sudo bash -c 'sed -i \"/$MASTER_NAME/d\" /etc/hosts'"  # Remove old master
    ssh ubuntu@$ext_ip "sudo bash -c 'sed -i \"/group27_vm2_worker-/d\" /etc/hosts'"  # Remove old workers
    ssh ubuntu@$ext_ip "sudo bash -c 'echo \"$MASTER_IP $MASTER_NAME\" >> /etc/hosts'"  # Add master
    j=1
    for ip in $WORKER_IPS; do
        w_name=$(echo $WORKER_NAMES | cut -d' ' -f$j)
        ssh ubuntu@$ext_ip "sudo bash -c 'echo \"$ip $w_name\" >> /etc/hosts'"  # Add workers
        ((j++))
    done
    ((i++))
done

echo "Updated /etc/hosts on all nodes. Verify with 'cat /etc/hosts' on each VM."
