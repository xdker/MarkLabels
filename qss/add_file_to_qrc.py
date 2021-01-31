import os

qrc = """<RCC>\n{}</RCC>"""
file_str = ""
style_list = []
qrc_strs = """<qresource prefix="/qss">\n{}</qresource>"""
for root, dir, files in os.walk("."):
    for f in files:
        if f.endswith(".qss"):
            style_list.append(f.split(".")[0])
        if f.endswith(".png") or f.endswith(".qss") or f.endswith(".ico"):
            file_str += "<file>%s</file>\n" % (root + "/" + f)[2:]
qrc_strs=qrc_strs.format(file_str)
with open("resources.qrc", "w") as f:
    f.write(qrc.format(qrc_strs))
print(style_list)
