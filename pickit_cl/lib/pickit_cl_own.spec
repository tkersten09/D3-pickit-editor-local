# -*- mode: python -*-

block_cipher = None


a = Analysis(['..\\pickit_cl.py'],
             pathex=['C:\\Users\\Thomas\\Documents\\GitHub\\pickit-cl\\lib'],
             binaries=[],
             datas=[('..\\data', 'data'), ('..\\lib', 'lib'), ('..\\output', 'output'),('..\\build_numbers.txt', '.')],
             hiddenimports=['pickit_cl_ori_py3'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pickit_cl',
          debug=True,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='pickit_cl')
