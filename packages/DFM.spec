# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\DFM.py'],
             pathex=['C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\packages'],
             binaries=[],
             datas=[('C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\resource\\dll\\libvlc.dll', '.'), ('C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\resource\\dll\\libvlccore.dll', '.'), ('C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\resource\\icon\\Connect.ico', 'resource\\icon'), ('C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\resource\\icon\\Disconnect.ico', 'resource\\icon'), ('C:\\Users\\OEMUSER\\PycharmProjects\\DFM_B2\\resource\\icon\\Refresh.ico', 'resource\\icon')],
             hiddenimports=[],
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
          name='DFM',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='favicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='DFM')
