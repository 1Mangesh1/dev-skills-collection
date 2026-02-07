# SSH Security

## Hardening SSH Server

```bash
# /etc/ssh/sshd_config

# Disable root login
PermitRootLogin no

# Disable password auth
PasswordAuthentication no
PubkeyAuthentication yes

# Use only strong ciphers
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com

# Limit authentication attempts
MaxAuthTries 3

# Disable X11 forwarding if not needed
X11Forwarding no

# Banner for warning message
Banner /etc/ssh/banner.txt

# Restart SSH
sudo systemctl restart sshd
```

## Key Rotation

```bash
# Generate new key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_new

# Add to agent
ssh-add ~/.ssh/id_ed25519_new

# Update authorized_keys on servers
for host in server1 server2; do
    ssh-copy-id -i ~/.ssh/id_ed25519_new.pub user@$host
done

# Remove old key from agent
ssh-add -d ~/.ssh/id_ed25519_old

# Delete old key
rm ~/.ssh/id_ed25519_old*
```

## SSH Tunneling

```bash
# Local port forwarding
ssh -L 8080:internal.company.com:80 bastion.host

# Remote port forwarding
ssh -R 9000:localhost:3000 server

# SOCKS proxy
ssh -D 1080 server
# Then: curl -x socks5://localhost:1080 http://example.com
```

## Certificates

```bash
# Create certificate authority
ssh-keygen -t ed25519 -f ca_key -C "CA" -N ""

# Sign user key
ssh-keygen -s ca_key -I user@company.com \
    -n deploy -V +52w ~/.ssh/id_rsa

# Verify certificate
ssh-keygen -L -f ~/.ssh/id_rsa-cert.pub
```
