import os
import shutil
import json

import click

UNIT_PATH = "pa/units/PAEIOU/"
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

def write_unitlist(unit_list, nmu_list):
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

    orig_unit_list["units"] = orig_unit_list["units"] + nmu_list + unit_list 

    return json.dumps(orig_unit_list)

def client_behavior(unitpath, addlist, savepath, modname, nmu_list = []):
    build_bar_locs = {}
    unit_list = []
    for i in addlist:
        curr_path = unitpath + i
        final_path = UNIT_PATH + i
        save_path = savepath + final_path

        loc_unit = "unit.json" 
        loc_img = "img.png"
        loc_si = "si.png"
        loc_build = "build.json"

        unitname = i.split('/')[-2]

        if os.path.isfile(curr_path + "meta.json"):
            with open(curr_path + "meta.json") as infile:
                meta = json.load(infile)
            if "unit" in meta:
                loc_unit = meta["unit"]
            if "img" in meta:
                loc_img = meta["img"]
            if "si" in meta:
                loc_img = meta["si"]
            if "build" in meta:
                loc_build = meta["build"]
    
        with open(curr_path + loc_unit) as infile:
            json_string = infile.read()

        (inc_files, json_strings) = full_substitution(json_string, i, unitname + '.json', curr_path)

        if "model.papa" in inc_files:
            inc_files.update(["model_diffuse.papa", "model_mask.papa", "model_material.papa"])

        os.makedirs(save_path, exist_ok=True)
        for j in inc_files:
            savefile = save_path + j
            if j not in json_strings.keys():
                shutil.copyfile(curr_path + j, savefile)
            else:
                with open(savefile, 'w') as output:
                    output.write(json_strings[j])
        if os.path.exists(curr_path + loc_img):
            shutil.copyfile(curr_path + loc_img, save_path + unitname + "_icon_buildbar.png")

        unit_filename = '/' + final_path + unitname + ".json"

        if os.path.exists(curr_path + loc_build):
            with open(curr_path + loc_build) as infile:
                data = json.load(infile)
            temp = []
            temp.append(data["tab"])
            temp.append(0)
            temp.append({"row": data["row"],
                            "column": data["col"],
                            "titans": True})
            
            
            build_bar_locs[unit_filename] = temp
            
        unit_list.append(unit_filename)
        
        si_path = savepath + "ui/main/atlas/icon_atlas/img/strategic_icons/"
        os.makedirs(si_path, exist_ok=True)

        if os.path.exists(curr_path + loc_si):
            shutil.copyfile(curr_path + loc_si, si_path + f"icon_si_{unitname}.png")

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
        out.write(write_unitlist(unit_list, nmu_list))

        


def direct_function(client, server, test, fullmod, modname, unitpath, addlistpath, savepath, nmu_path = ""): 
    with open(addlistpath) as infile:
        addlist = infile.readlines()

    for i in range(len(addlist)):
        addlist[i] = addlist[i].rstrip('\n')
    
    if nmu_path != "":
        with open(nmu_path) as infile:
            nmu_list = [i.rstrip('\n') for i in infile.readlines()]
    else:
        nmu_path = []

    if client:
        client_behavior(unitpath, addlist, savepath + 'client/', modname)
    if server:
        # server_behavior(unitpath, addlist, savepath)
        client_behavior(unitpath, addlist, savepath + 'server/', modname, nmu_list = nmu_list)

@click.command()
@click.option('--client/--no-client', default=True)
@click.option('--server/--no-server', default=True)
@click.option('--test/--prod', default=True)
@click.option('--fullmod/--units-only', default=True)
@click.argument('modname', default='my_PAEIOU_mod')
@click.argument('unitpath', default='units/', type=click.Path(exists=True))
@click.argument('addlist', default='unit_add_list.txt', type=click.Path(exists=True))
@click.argument('savepath', default='gen/', type=click.Path(exists=False))
def main(client, server, test, fullmod, modname, unitpath, addlist, savepath):
    direct_function(client, server, test, fullmod, modname, unitpath, addlist, savepath)
    

if __name__ == '__main__':
    main()