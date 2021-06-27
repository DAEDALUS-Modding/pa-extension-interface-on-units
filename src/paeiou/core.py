import os
import shutil
import json

UNIT_PATH = "pa/units/paeiou/"
SI_PATH = "ui/main/atlas/icon_atlas/img/strategic_icons/"

def paeiou_substitution(json_string, folder):
    #This function is what allow's PAEIOU to substitute in full filepaths for bare filenames.
    inc_files = []
    while True:
        ind1 = json_string.find('"{')
        if ind1 == -1:
            break
        ind2 = json_string.find('}"')
        filename = json_string[ind1+2:ind2]
        if filename[0] != "!":
            inc_files.append(filename)
        else:
            filename = filename[1:]
        json_string = json_string[0:ind1] + '"/' + UNIT_PATH + folder + filename + '"' + json_string[ind2+2:]
    return (inc_files, json_string)


def full_substitution(json_string, folder, unit, curr_path):
    #Calls paeiou_substitution on all files in a folder
    (inc_files, json_string) = paeiou_substitution(json_string, folder)
    inc_files = set(inc_files)
    json_list = [i for i in inc_files if ((i.find('.json') + 1) or (i.find('.pfx') + 1))]
    json_strings = {unit: json_string}
    inc_files.add(unit)
    while len(json_list):
        curr = json_list.pop(-1)
        with open(curr_path + curr) as infile:
            json_string = infile.read()

        (new_inc_files, json_string) = paeiou_substitution(json_string, folder)
        json_list = json_list + [i for i in new_inc_files if ((i.find('.json') + 1) or (i.find('.pfx') + 1))]
        inc_files.update(new_inc_files)
        json_strings[curr] = json_string
    return (inc_files, json_strings)

def ai_unit_map_name(unitname, modname):
    return f"{modname}_paeiou_{unitname}"

STRING0_SUB_TYPES = (
    "CanFindPlaceToBuild",
    "CanAffordPotentialDrain"
)

def handle_ai_file(inp_json_str, folder, unitname, mod_prefix = ""):
    (_, build_list_str) = paeiou_substitution(inp_json_str, folder)
    build_list = json.loads(build_list_str)
    for i, build_test in enumerate(build_list):
        if "name_suffix" in build_test:
            name_suffix = build_test.pop("name_suffix")
        else:
            name_suffix = i

        if "name" not in build_test:
            build_test["name"] = f"{mod_prefix}_paeiou_{unitname}_{name_suffix}"
        
        to_build = ai_unit_map_name(unitname, mod_prefix)
        build_test["to_build"] = to_build

        for test_series in build_test["build_conditions"]:
            for condition in test_series:
                if condition["test_type"] in STRING0_SUB_TYPES:
                    if not "string0" in condition:
                        condition["string0"] = to_build

        if "paeiou_builders" in build_test:
            paeiou_builders = [ai_unit_map_name(b, mod_prefix) for b in build_test["paeiou_builders"]] 
            if "builders" in build_test:
                build_test["builders"] = build_test["builders"] + paeiou_builders
            else:
                build_test["builders"] = paeiou_builders

    out_dict = {
        "build_list": build_list
    }

    return json.dumps(out_dict, indent=4, sort_keys=True)
    
def write_ai_unit_maps(unitname_list, mod_prefix = ""):
    out_dict = {
        "unit_map": {}
    }

    for path, unitname in unitname_list:
        unit_map_name = ai_unit_map_name(unitname, mod_prefix)
        out_dict["unit_map"][unit_map_name] = {
            "spec_id": f"/{UNIT_PATH}{path}{unitname}.json"
        }

    return json.dumps(out_dict, indent=4, sort_keys=True)



def server_behavior(unitpath, addlist, savepath):
    # for i in addlist:
    #     curr_path = unitpath + i
    #     final_path = UNIT_PATH + i
    #     save_path = savepath + final_path

    #     loc_unit = "unit.json" 
    #     loc_img = "img.png"

    #     if os.path.isfile(curr_path + "meta.json"):
    #         with open(curr_path + "meta.json") as infile:
    #             meta = json.load(infile)
    #         if "unit" in meta:
    #             loc_unit = meta["unit"]
    #         if "img" in meta:
    #             loc_img = meta["img"]
    
    #     with open(curr_path + loc_unit) as infile:
    #         json_string = infile.read()

    #     (_, json_string) = paeiou_substitution(json_string, i)

    #     unit = json.loads(json_string)

    #     if "tools" in 
    print("server generation temporarily disabled entirely")

def write_atlas(unitname_list):
    js = "var paeiouIcons = ["

    for i in unitname_list:
        js = js + f'"{i}",\n'
    
    js = js + "];\nmodel.strategicIcons(model.strategicIcons().concat(paeiouIcons));"

    return js

def write_buildbar(build_bar_locs):
    js = "var newBuild = {\n"
    for i,j in build_bar_locs.items():
        js = js + f'"{i}": ["{j[0]}", {j[1]},'
        js = js + "{ row: " + str(j[2]["row"]) + ", column: " + str(j[2]["column"]) + ", titans: true }],\n"
    js = js + '\n}\nif (Build && Build.HotkeyModel && Build.HotkeyModel.SpecIdToGridMap) {\n'
    js = js + '_.extend(Build.HotkeyModel.SpecIdToGridMap, newBuild);\n}'

    return js

def write_unit_list(new_unit_list, old_unit_list = False, pa_path = False):
    if not (pa_path or old_unit_list):
        print("ERROR: Neither location nor previous unit list given for write_unit_list()")

    if pa_path:
        with open(pa_path + "pa_ex1/units/unit_list.json") as infile:
            old_unit_list = json.load(infile)

    old_unit_list["units"] = old_unit_list["units"] + new_unit_list

    return json.dumps(old_unit_list, indent=4, sort_keys=True)

def write_comm_list(new_comm_list, old_comm_list = False, pa_path = False):
    if not (pa_path or old_comm_list):
        print("ERROR: Neither location nor previous unit list given for write_comm_list()")

    if pa_path:
        with open(pa_path + "pa_ex1/units/commanders/commander_list.json") as infile:
            old_comm_list = json.load(infile)

    old_comm_list["commanders"] = old_comm_list["commanders"] + new_comm_list

    return json.dumps(old_comm_list, indent=4, sort_keys=True)

def client_behavior(unitpath, addlist, savepath, modname, mod_prefix, old_unit_list, pa_path, project_default_filepaths = {}):
    build_bar_locs = {}
    unit_list = []
    unitname_list = []
    ai_unitname_lists = {}
    ai_folders_seen = set()

    def_loc_unit = "unit.json" 
    def_loc_img = "img.png"
    def_loc_si = "si.png"
    def_loc_build = "build.json"
    def_loc_models = ["model.papa"]
    def_ai_build = {
        "ai": {
            "fabber_builds": "ai_fab.json",
            "factory_builds": "ai_fac.json"
        }
    }
    def_loc_meta = "meta.json"

    if "unit" in project_default_filepaths:
        def_loc_unit = project_default_filepaths["unit"]
    if "img" in project_default_filepaths:
        def_loc_img = project_default_filepaths["img"]
    if "si" in project_default_filepaths:
        def_loc_si = project_default_filepaths["si"]
    if "build" in project_default_filepaths:
        def_loc_build = project_default_filepaths["build"]
    if "models" in project_default_filepaths:
        def_loc_models = project_default_filepaths["models"]
    if "ai_build" in project_default_filepaths:
        def_ai_build = project_default_filepaths["ai_build"]
    if "meta" in project_default_filepaths:
        def_loc_meta = project_default_filepaths["meta"]

    for i in addlist:
        curr_path = unitpath + i
        final_path = UNIT_PATH + i
        save_path = savepath + final_path

        loc_unit = def_loc_unit
        loc_img = def_loc_img
        loc_si = def_loc_si
        loc_build = def_loc_build
        loc_models = def_loc_models
        ai_build_rules = def_ai_build

        unitname = i.split('/')[-2]

        if os.path.isfile(curr_path + def_loc_meta):
            with open(curr_path + def_loc_meta) as infile:
                meta = json.load(infile)
            if "unit" in meta:
                loc_unit = meta["unit"]
            if "img" in meta:
                loc_img = meta["img"]
            if "si" in meta:
                loc_si = meta["si"]
            if "build" in meta:
                loc_build = meta["build"]
            if "models" in meta:
                loc_models = meta["models"]
            if "ai_build" in meta:
                ai_build_rules = meta["ai_build"]
            if "unitname" in meta:
                unitname = meta["unitname"]

        unitname_list.append(unitname)
    
        if loc_unit:
            with open(curr_path + loc_unit) as infile:
                json_string = infile.read()

            (inc_files, json_strings) = full_substitution(json_string, i, unitname + '.json', curr_path)

        for j in loc_models:
            if j in inc_files:
                model = j[:-5]
                inc_files.update([f"{model}_diffuse.papa", f"{model}_mask.papa", f"{model}_material.papa"])

        os.makedirs(save_path, exist_ok=True)
        for j in inc_files:
            savefile = save_path + j
            savefolder = os.path.split(savefile)[0]
            if not os.path.isdir(savefolder):
                os.makedirs(savefolder, exist_ok=True)
            if j not in json_strings.keys():
                shutil.copyfile(curr_path + j, savefile)
            else:
                with open(savefile, 'w') as output:
                    output.write(json_strings[j])

        if loc_img:
            shutil.copyfile(curr_path + loc_img, save_path + unitname + "_icon_buildbar.png")

        unit_filename = '/' + final_path + unitname + ".json"
        if loc_unit:
            unit_list.append(unit_filename)

        if loc_build:
            with open(curr_path + loc_build) as infile:
                data = json.load(infile)
            temp = []
            temp.append(data["tab"])
            temp.append(0)
            temp.append({"row": data["row"],
                            "column": data["col"],
                            "titans": True})
            build_bar_locs[unit_filename] = temp
        
        if loc_si:
            si_path = savepath + "ui/main/atlas/icon_atlas/img/strategic_icons/"
            os.makedirs(si_path, exist_ok=True)
            shutil.copyfile(curr_path + loc_si, si_path + f"icon_si_{unitname}.png")

        for ai in ai_build_rules:
            if ai_build_rules[ai] == "builder_only":
                if not ai in ai_unitname_lists:
                    ai_unitname_lists[ai] = set()
                    ai_folders_seen.add(ai)
                ai_unitname_lists[ai].add((i, unitname))
                continue
            for buildtype in ai_build_rules[ai]:
                loc_ai_build = ai_build_rules[ai][buildtype]
                if loc_ai_build and os.path.exists(curr_path + loc_ai_build):
                    ai_build_path = savepath + f"pa/{ai}/{buildtype}"
                    os.makedirs(ai_build_path, exist_ok=True)
                    if not ai in ai_unitname_lists:
                        ai_unitname_lists[ai] = set()
                        ai_folders_seen.add(ai)
                    ai_unitname_lists[ai].add((i, unitname))
                        
                    with open(curr_path + loc_ai_build) as infile:
                        ai_json_str = infile.read()

                    ai_json_str = handle_ai_file(ai_json_str, i, unitname, mod_prefix)

                    with open(f"{ai_build_path}/{unitname}.json", "w") as outfile:
                        outfile.write(ai_json_str)

    ui_path = savepath + f"ui/mods/{modname}/"
    icon_atlas_js = ui_path + "icon_atlas.js"
    build_js = ui_path + "shared_build.js"
    os.makedirs(ui_path, exist_ok=True)

    with open(build_js, 'w') as out:
        out.write(write_buildbar(build_bar_locs))
    with open(icon_atlas_js, 'w') as out:
        out.write(write_atlas(unitname_list))

    unit_list_json = savepath + "pa/units/unit_list.json"    
    with open(unit_list_json, 'w') as out:
        out.write(write_unit_list(unit_list, old_unit_list, pa_path))

    for ai in ai_folders_seen:
        os.makedirs(savepath + f"pa/{ai}/unit_maps/", exist_ok=True)
        ai_unit_maps_fname = savepath + f"pa/{ai}/unit_maps/{mod_prefix}_paeiou.json"
        with open(ai_unit_maps_fname, 'w') as outfile:
            outfile.write(write_ai_unit_maps(ai_unitname_lists[ai], mod_prefix))

def paeiou(
    mod_id = "my.paeiou.mod", mod_prefix = "", paeiou_unit_path = "PAEIOU_units/", 
    unit_add_list = "unit_add_list.txt", output_path = "paeiou_gen/", 
    project_default_filepaths = {}, server = True, client = False,
    old_unit_list = False, pa_path = False
    ): 
    with open(unit_add_list) as infile:
        addlist = infile.readlines()

    for i in range(len(addlist)):
        addlist[i] = addlist[i].rstrip('\n')

    if client:
        client_behavior(paeiou_unit_path, addlist, output_path, mod_id, mod_prefix, old_unit_list, pa_path, project_default_filepaths)
    if server:
        # server_behavior(unitpath, addlist, savepath)
        client_behavior(paeiou_unit_path, addlist, output_path, mod_id, mod_prefix, old_unit_list, pa_path, project_default_filepaths)

def process_comm_add_list(comm_add_list, paeiou_unit_path, base_save_path, old_comm_list = False, pa_path = False, project_default_filepaths = {}):
    with open(comm_add_list) as infile:
        commander_addlist = infile.readlines()

    new_comm_list = []

    if "meta" in project_default_filepaths:
        def_loc_meta = project_default_filepaths["meta"]
    else:
        def_loc_meta = "meta.json"

    for i in commander_addlist:
        curr_path = paeiou_unit_path + i
        unitname = i.split('/')[-2]

        if os.path.isfile(curr_path + def_loc_meta):
            with open(curr_path + def_loc_meta) as infile:
                meta = json.load(infile)
            if "unitname" in meta:
                unitname = meta["unitname"]

        new_comm_list.append("/" + UNIT_PATH + i + unitname + ".json")

    os.makedirs(base_save_path + "pa/units/commanders/", exist_ok=True)
    with open(base_save_path + "pa/units/commanders/commander_list.json", "w") as out:
        out.write(write_comm_list(new_comm_list, old_comm_list, pa_path))
