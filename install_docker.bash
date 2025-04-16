# Set up repository variables
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)

# Add NVIDIA’s GPG key
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -

# Add the repository (this example uses your distribution info)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/libnvidia-container.list

# Update the package index and install the toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

