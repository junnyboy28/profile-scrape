# setup.sh
set -e

# Install GLIBC version 2.38
GLIBC_VERSION="2.38"
curl -fsSL "http://ftp.gnu.org/gnu/libc/glibc-${GLIBC_VERSION}.tar.gz" | tar -xz
cd "glibc-${GLIBC_VERSION}"
mkdir build
cd build
../configure --prefix=/opt/glibc
make -j$(nproc)
make install
cd /app
export LD_LIBRARY_PATH=/opt/glibc/lib:$LD_LIBRARY_PATH

# Install Playwright dependencies
apt-get update
apt-get install -y libnss3 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2

# Install Playwright browsers
playwright install
