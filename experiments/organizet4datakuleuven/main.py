import os
import shutil


data_dir = "L:\\FHML_SURGERY\\AImodel\\T4\\KU_Leuven"
data_dir_org = "L:\\FHML_SURGERY\\AImodel\\T4\\KU_Leuven\\OriginalData"

steps = {
    "copy": True,
    "remove_unrelated_files": True,
    "remove_duplicates": True,
    "add_extensions": True,
}

if steps["copy"]:
    print("Copying data...")
    for d in os.listdir(data_dir_org):
        if d.startswith("BC"):
            d_path = os.path.join(data_dir_org, d)
            for f in os.listdir(d_path):
                f_path = os.path.join(d_path, f)
                shutil.copy(f_path, data_dir)
            print(f"Copied {d}")


if steps["remove_unrelated_files"]:
    print("Removing unrelated files...")
    if os.path.exists(os.path.join(data_dir, ".DS_Store")):
        os.remove(os.path.join(data_dir, ".DS_Store"))
    if os.path.exists(os.path.join(data_dir, "._.DS_Store")):
        os.remove(os.path.join(data_dir, "._.DS_Store"))


if steps["remove_duplicates"]:
    print("Removing duplicates...")
    for f in os.listdir(data_dir):
        if f.startswith("BC") and not f.endswith("tag"):
            f_path = os.path.join(data_dir, f)
            f_path_duplicate = os.path.join(data_dir, "._" + f)
            if os.path.exists(f_path_duplicate):
                os.remove(f_path_duplicate)
                print("Removed duplicate with leading dot")
            if os.path.exists(f_path_duplicate + ".tag"):
                os.remove(f_path_duplicate + ".tag")
                print("Removed duplicate with leading dot and tag extension")


if steps["add_extensions"]:
    print("Adding extensions...")
    for f in os.listdir(data_dir):
        if f.startswith("BC") and not f.endswith("tag"):
            if not f.endswith("dcm"):
                f_path = os.path.join(data_dir, f)
                f_path_tag = os.path.join(data_dir, f + ".tag")
                f_path_new = os.path.join(data_dir, f + ".dcm")
                f_path_tag_new = os.path.join(data_dir, f + ".dcm.tag")
                shutil.move(f_path, f_path_new)
                shutil.move(f_path_tag, f_path_tag_new)
                print(f"Added extension to {f}")