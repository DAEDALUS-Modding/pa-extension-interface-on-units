import json
import os.path
import urllib.request as req
import zipfile
import tempfile
import shutil

def simulate_mod_mount(pa_path, mod_urls = {}, dl_path = "download", stage_path = "stage"):
    for (mod, mod_url) in mod_urls.items():
        # download and unzip mods
        mod_folder = os.path.join(dl_path, mod)

        if os.path.isdir(mod_folder):
            # don't redownload if mod already downloaded
            # clear downloads if need to update version
            continue

        with req.urlopen(mod_url) as resp:
            with tempfile.TemporaryFile() as tmp_zip:
                shutil.copyfileobj(resp, tmp_zip)

                with zipfile.ZipFile(tmp_zip) as zf:
                    names = zf.namelist()
                    if "modinfo.json" in names:
                        zf.extractall(mod_folder)
                    else: # modinfo not in top level
                        firstpath = names[0].split("/")[0]
                        zf.extractall(dl_path)
                        os.rename(os.path.join(dl_path, firstpath), os.path.join(dl_path, mod))


    mod_priorities = {}
    mod_order = list()

    for mod in mod_urls.keys():
        # high priority mounts first; low priority overrides later!
        with open(os.path.join(mod_folder, "modinfo.json")) as infile:
            priority = json.load(infile)["priority"]
            mod_priorities[mod] = priority

            for (i, m) in enumerate(mod_order):
                if priority > mod_priorities[m]:
                    mod_order.insert(i, mod)
                    continue

            mod_order.append(mod) # lowest priority so far
        
    # create aggregate unit list
    unit_list_path = os.path.join(pa_path, "pa_ex1/units/unit_list.json")

    with open(unit_list_path) as unit_list:
        unit_set = set(json.load(unit_list)['units'])

    for mod in mod_order:
        unit_list_path = os.path.join(dl_path, mod, "pa/units/unit_list.json")

        with open(unit_list_path) as unit_list:
            mod_units = set(json.load(unit_list)['units'])
            unit_set = unit_set.union(mod_units)

    units = [x[1:] for x in unit_set] # remove starting / from filepath

    # mount PA, Titans, and mod files in stage/
    if os.path.isdir(stage_path):
        shutil.rmtree(stage_path)

    os.mkdir(stage_path)

    tools = []

    def update_tool_list(unit_path):
        with open(unit_path) as unitfile:
            unit = json.load(unitfile)
            if "tools" in unit:
                for j in unit['tools']:
                    tools.append(j['spec_id'])

    def copyfile_w_dir(src, dst):
        os.makedirs(os.path.dirname(dst), exist_ok = True)
        shutil.copyfile(src, dst)

    # mount PA and Titans unit/tool .jsons

    for unit in units:
        # There is a chance that a mod might bring in a unit defined in
        # the base game but which is absent in the base unit_list.
        # i.e. stinger or deepspace radar
        # Not a problem unless the unit isn't redefined in the mod.
        # However, this script protects against that just in case.
        vanilla_path = os.path.join(pa_path, unit)
        titans_path = os.path.join(pa_path, 'pa_ex1' + unit[2:])

        out_path = os.path.join(stage_path, unit)

        if os.path.isfile(titans_path):
            update_tool_list(titans_path)
            copyfile_w_dir(titans_path, out_path)
        elif os.path.isfile(vanilla_path):
            update_tool_list(vanilla_path)
            copyfile_w_dir(vanilla_path, out_path)

    tools = [x[1:] for x in tools]

    for tool in tools:
        # There is a chance that a mod might use a tool defined in
        # the base game but which is not directly used by any unit
        # we've moved to stage/.
        # This is a problem but this script currently makes no attempt
        # to address this potential issue.
        vanilla_path = os.path.join(pa_path, tool)
        titans_path = os.path.join(pa_path, "pa_ex1" + tool[2:])

        out_path = os.path.join(stage_path, tool)

        if os.path.isfile(titans_path):
            copyfile_w_dir(titans_path, out_path)
        elif os.path.isfile(vanilla_path):
            copyfile_w_dir(vanilla_path, out_path)    

    # mount mod files in stage/

    for mod in mod_order:
        # There is a chance that modded units may be in weird places.
        # Mods are relatively small so we can mount them in their 
        # #entirety just in case.
        shutil.copytree(os.path.join(dl_path, mod), stage_path, dirs_exist_ok=True)

    return True


