#!/usr/bin/env sh
# find the gurobi tarball
tarball=$(find . -maxdepth 1 -name 'gurobi*_linux64.tar.gz' | head -n 1)

if [ -z "$tarball" ]; then
    echo "No gurobi tarball found in the current directory"
    exit 1
fi

# Extract the version from the tarball filename
version=$(echo $tarball | sed -n 's/.*gurobi\([0-9.]*\)_linux64.tar.gz/\1/p')
version_no_dots=$(echo $version | sed 's/\.//g')


# Move the tarball to /opt/
sudo mv $tarball /opt/
cd /opt/

# Extract tarball
sudo tar -xzf $tarball
sudo rm $tarball

# Compile the C library
cd gurobi$version_no_dots/linux64/src/build
sudo make

# Instruct the user to add the following to their .{ba,z,fi}shrc
echo "Add the following to your .{ba,z,fi}shrc:"
echo "export GUROBI_HOME=\"/opt/gurobi$version_no_dots/linux64\""
echo "export PATH=\"\$PATH:\$GUROBI_HOME/bin\""
echo "export LD_LIBRARY_PATH=\"\$LD_LIBRARY_PATH:\$GUROBI_HOME/lib\""

# on my CMakeLists.txt I have the following:
echo "Add the following to your CMakeLists.txt:"
echo "set(GUROBI_DIR \"/opt/gurobi$version_no_dots/linux64\")"
echo "include_directories(SYSTEM \${GUROBI_DIR}/include)"
echo "link_directories(\${GUROBI_DIR}/lib)"
echo "target_link_libraries(\${PROJECT_NAME} gurobi_c++ gurobi$version_no_dots)"
