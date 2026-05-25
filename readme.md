
## Install `docker compose` tool

- Install docker compose v2 from Docker's official APT repo
- Keep the existing docker Engine; we're just adding the repo and installing the plugin

```
# Prereqs

``
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker's GPG key & repo (Ubuntu 22.04 = jammy)
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release; echo "$VERSION_CODENAME") stable" \
| sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

# Install the Compose v2 plugin
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# Verify
docker compose version
```

