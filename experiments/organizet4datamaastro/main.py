import os
import shutil

data_dir = "L:\\FHML_SURGERY\\AImodel\\T4\\Maastro"
data_dir_org = "L:\\FHML_SURGERY\\AImodel\\T4\\Maastro\\OriginalData"


steps = {
    "copy": True,
}


if steps["copy"]:
    for d in os.listdir(data_dir_org):
        d_path = os.path.join(data_dir_org, d)
        if os.path.isdir(d_path):
            for f in os.listdir(d_path):
                if f.endswith('.dcm'):
                    elems = os.path.splitext(f)
                    f_name = elems[0]
                    f_path = os.path.join(d_path, f)
                    f_path_new = os.path.join(data_dir, d + '.dcm')
                    shutil.copy(f_path, f_path_new)
                    print(f'Copied {f_path} to {f_path_new}')
                elif f.endswith('.dcm.tag'):
                    elems = os.path.splitext(os.path.splitext(f)[0])
                    f_name = elems[0]
                    f_path = os.path.join(d_path, f)
                    f_path_new = os.path.join(data_dir, d + '.dcm.tag')
                    shutil.copy(f_path, f_path_new)
                    print(f'Copied {f_path} to {f_path_new}')
                else:
                    pass