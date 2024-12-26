# setup.sh
set -e

# Install dependencies
apt-get update
apt-get install -y wget build-essential

# Install GLIBC version 2.38 (required by Playwright)
GLIBC_VERSION="2.38"
GLIBC_TAR="glibc-${GLIBC_VERSION}.tar.gz"
wget http://ftp.gnu.org/gnu/libc/${GLIBC_TAR}
tar -xvzf ${GLIBC_TAR}
cd glibc-${GLIBC_VERSION}
mkdir build
cd build
../configure --prefix=/opt/glibc
make -j$(nproc)
make install

# Set the environment to use the new GLIBC version
export LD_LIBRARY_PATH=/opt/glibc/lib:$LD_LIBRARY_PATH

# Install Playwright dependencies
apt-get install -y libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2

# Install Playwright browsers
playwright install

cd /app
