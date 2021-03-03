import os
import shutil
import json

import click

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
        inc_files.append(filename)
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
        
        build_test["to_build"] = ai_unit_map_name(unitname, mod_prefix)

    out_dict = {
        "build_list": build_list
    }

    return json.dumps(out_dict, indent=4, sort_keys=True)
    
def write_ai_unit_maps(unitname_list, mod_prefix = ""):
    out_dict = {
        "unit_map": {}
    }

    for unitname in unitname_list:
        unit_map_name = ai_unit_map_name(unitname, mod_prefix)
        out_dict["unit_map"][unit_map_name] = {
            "spec_id": f"/{UNIT_PATH}{unitname}/{unitname}.json"
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

def write_atlas(addlist):
    name_list = [i.split('/')[-2] for i in addlist]

    js = "var paeiouIcons = ["

    for i in name_list:
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

def write_unitlist(unit_list):
    pa_dir_in = "pa_location.txt"
    if (os.path.isfile(pa_dir_in)):
        with open(pa_dir_in) as infile:
            pa_path = infile.readline()
    else:
        pa_path = input("Planetary Annihilation installation path: ")
        with open(pa_dir_in, 'w+') as outfile:
            outfile.write(pa_path)

    with open(pa_path + "media/pa_ex1/units/unit_list.json") as infile:
        orig_unit_list = json.load(infile)

    orig_unit_list["units"] = orig_unit_list["units"] + unit_list

    return json.dumps(orig_unit_list, indent=4, sort_keys=True)

def client_behavior(unitpath, addlist, savepath, modname, mod_prefix = ""):
    build_bar_locs = {}
    unit_list = []
    ai_unitname_list = set()
    for i in addlist:
        curr_path = unitpath + i
        final_path = UNIT_PATH + i
        save_path = savepath + final_path

        loc_unit = "unit.json" 
        loc_img = "img.png"
        loc_si = "si.png"
        loc_build = "build.json"
        loc_models = ["model.papa"]
        loc_ai_fab = "ai_fab.json"
        loc_ai_fac = "ai_fac.json"

        unitname = i.split('/')[-2]

        if os.path.isfile(curr_path + "meta.json"):
            with open(curr_path + "meta.json") as infile:
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
            if "ai_fab" in meta:
                loc_ai = meta["ai"]
            if "ai_fac" in meta:
                loc_ai = meta["ai"]
            if "unitname" in meta:
                unitname = meta["unitname"]

    
        if loc_unit:
            with open(curr_path + loc_unit) as infile:
                json_string = infile.read()

            (inc_files, json_strings) = full_substitution(json_string, i, unitname + '.json', curr_path)

        for i in loc_models:
            if i in inc_files:
                model = i[:-5]
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

        if loc_build:
            with open(curr_path + loc_build) as infile:
                data = json.load(infile)
            temp = []
            temp.append(data["tab"])
            temp.append(0)
            temp.append({"row": data["row"],
                            "column": data["col"],
                            "titans": True})
            
            unit_filename = '/' + final_path + unitname + ".json"
            build_bar_locs[unit_filename] = temp

        if loc_unit:
            unit_list.append(unit_filename)
        
        if loc_si:
            si_path = savepath + "ui/main/atlas/icon_atlas/img/strategic_icons/"
            os.makedirs(si_path, exist_ok=True)
            shutil.copyfile(curr_path + loc_si, si_path + f"icon_si_{unitname}.png")

        if loc_ai_fab and os.path.exists(curr_path + loc_ai_fab):
            ai_fab_path = savepath + f"pa/ai/fabber_builds" 
            os.makedirs(ai_fab_path, exist_ok=True)
            ai_unitname_list.add(unitname)

            with open(curr_path + loc_ai_fab) as infile:
                ai_json_str = infile.read()

            ai_json_str = handle_ai_file(ai_json_str, i, unitname, mod_prefix)

            with open(f"{ai_fab_path}/{unitname}.json", "w") as outfile:
                outfile.write(ai_json_str)

        if loc_ai_fac and os.path.exists(curr_path + loc_ai_fac):
            ai_fac_path = savepath + f"pa/ai/factory_builds" 
            os.makedirs(ai_fac_path, exist_ok=True)
            ai_unitname_list.add(unitname)

            with open(curr_path + loc_ai_fac) as infile:
                ai_json_str = infile.read()

            ai_json_str = handle_ai_file(ai_json_str, i, unitname, mod_prefix)

            with open(f"{ai_fac_path}/{unitname}.json", "w") as outfile:
                outfile.write(ai_json_str)

    ui_path = savepath + f"ui/mods/{modname}/"
    icon_atlas_js = ui_path + "icon_atlas.js"
    build_js = ui_path + "shared_build.js"
    os.makedirs(ui_path, exist_ok=True)

    with open(build_js, 'w') as out:
        out.write(write_buildbar(build_bar_locs))
    with open(icon_atlas_js, 'w') as out:
        out.write(write_atlas(addlist))

    unit_list_json = savepath + "pa/units/unit_list.json"    
    with open(unit_list_json, 'w') as out:
        out.write(write_unitlist(unit_list))

    os.makedirs(savepath + "pa/ai/unit_maps/", exist_ok=True)
    ai_unit_maps_fname = savepath + f"pa/ai/unit_maps/{mod_prefix}_paeiou.json"
    with open(ai_unit_maps_fname, 'w') as outfile:
        outfile.write(write_ai_unit_maps(ai_unitname_list, mod_prefix))

        


def direct_function(client, server, test, fullmod, modname, unitpath, addlistpath, savepath, mod_prefix): 
    with open(addlistpath) as infile:
        addlist = infile.readlines()

    for i in range(len(addlist)):
        addlist[i] = addlist[i].rstrip('\n')

    if client:
        client_behavior(unitpath, addlist, savepath, modname, mod_prefix)
    if server:
        # server_behavior(unitpath, addlist, savepath)
        client_behavior(unitpath, addlist, savepath, modname, mod_prefix)

@click.command()
@click.option('--client/--no-client', default=True)
@click.option('--server/--no-server', default=True)
@click.option('--test/--prod', default=True)
@click.option('--fullmod/--units-only', default=True)
@click.argument('modname', default='my_paeiou_mod')
@click.argument('unitpath', default='units/', type=click.Path(exists=True))
@click.argument('addlist', default='unit_add_list.txt', type=click.Path(exists=True))
@click.argument('savepath', default='gen/', type=click.Path(exists=False))
def main(client, server, test, fullmod, modname, unitpath, addlist, savepath):
    direct_function(client, server, test, fullmod, modname, unitpath, addlist, savepath)
    

if __name__ == '__main__':
    main()