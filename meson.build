project('nvibrant', 'cpp',
  version: run_command('nvibrant/version.py', check: true).stdout().strip()
)

# Paths to nvidia sources and headers
nvidia_src     = 'open-gpu/src'
nvidia_modeset = join_paths(nvidia_src, 'nvidia-modeset')
nvidia_kernel  = join_paths(nvidia_src, 'kernel-open')
nvidia_incs    = include_directories(
  join_paths(nvidia_modeset, 'interface'),
  join_paths(nvidia_modeset, 'include'),
  join_paths(nvidia_src, 'common/inc'),
  join_paths(nvidia_src, 'common/sdk/nvidia/inc'),
  join_paths(nvidia_src, 'common/unix/common/inc')
)

executable('nvibrant',
  'nvibrant/main.cpp',
  include_directories: nvidia_incs,
  install: true
)