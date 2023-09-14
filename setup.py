import platform
import subprocess
import os
from setuptools import setup, Extension

# TODO:
# - test on windows
# - test on Linux
# - test on Darwin without SDL2 AND brew

# Function to check if a command exists
def command_exists(command):
    try:
        subprocess.run([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

# Initialize SDL2 paths
sdl2_include_path = None
sdl2_lib_path = None

def get_c_sources(folder, include_headers=False):
    """Find all C/C++ source files in the `folder` directory."""
    allowed_extensions = [".c", ".C", ".cc", ".cpp", ".cxx", ".c++"]
    if include_headers:
        allowed_extensions.extend([".h", ".hpp"])
    sources = []
    for name in os.listdir(folder):
        ext = os.path.splitext(name)[1]
        if ext in allowed_extensions:
            sources.append(os.path.join(folder, name))
    return sources

# Check OS
if platform.system() == 'Linux':  # Ubuntu
    if not command_exists('sdl2-config'):
        subprocess.run(['sudo', 'apt-get', 'update'])
        subprocess.run(['sudo', 'apt-get', 'install', 'libsdl2-dev'])

    # Get SDL2 paths
    sdl2_include_path = subprocess.getoutput('sdl2-config --cflags').split()[-1][2:]
    sdl2_lib_path = subprocess.getoutput('sdl2-config --libs').split()[-1][2:]

elif platform.system() == 'Darwin':  # macOS
    if not command_exists('brew'):
        # Install Homebrew
        subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

    if not command_exists('sdl2-config'):
        # Install SDL2
        subprocess.run(['brew', 'install', 'sdl2'])

    # Get SDL2 paths
    sdl2_cflags = subprocess.getoutput('sdl2-config --cflags')
    sdl2_libs = subprocess.getoutput('sdl2-config --libs')
    
    # Extract the include and library directories
    sdl2_include_path = [flag[2:] for flag in sdl2_cflags.split() if flag.startswith('-I')][0]
    sdl2_lib_path = [flag[2:] for flag in sdl2_libs.split() if flag.startswith('-L')][0]

whisper = Extension(
    name="whisper.cpp", 
    sources=get_c_sources("whisper.cpp"),
    extra_compile_args=["-std=c++11"],
    include_dirs=["whisper.cpp"]
    )

stream = Extension(
    "stream.cpp", 
    sources=get_c_sources("whisper.cpp/examples/stream"),
    extra_compile_args=["-std=c++11"],
    libraries=['SDL2'],
    include_dirs=[sdl2_include_path, "whisper.cpp/examples", "whisper.cpp"],
    library_dirs=[sdl2_lib_path],
    )

setup(
    name="whisper-stream",
    version="1.0.0",
    ext_modules=[whisper, stream]
)