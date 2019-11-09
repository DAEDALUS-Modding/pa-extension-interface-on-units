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
    inc_files.add(unit)
    json_list = [i for i in inc_files if ((i.find('.json') + 1) or (i.find('.pfx') + 1))]
    json_strings = {unit: json_string}
    while len(json_list):
        print(json_list)
        curr = json_list.pop(-1)
        print(curr)
        with open(curr_path + curr) as infile:
            json_string = infile.read()

        (new_inc_files, json_string) = paeiou_substitution(json_string, folder)
        json_list = json_list + [i for i in new_inc_files if ((i.find('.json') + 1) or (i.find('.pfx') + 1))]
        inc_files.update(new_inc_files)
        json_strings[curr] = json_string
    return (inc_files, json_strings)


def server_behavior(unitpath, addlist, savepath, modname):
    for i in addlist:
        curr_path = unitpath + i
        final_path = UNIT_PATH + i
        save_path = savepath + final_path

        loc_unit = "unit.json" 
        loc_img = "img.png"

        if os.path.isfile(curr_path + "meta.json"):
            with open(curr_path + "meta.json") as infile:
                meta = json.load(infile)
            if "unit" in meta:
                loc_unit = meta["unit"]
            if "img" in meta:
                loc_img = meta["img"]
    
        with open(curr_path + loc_unit) as infile:
            json_string = infile.read()

def client_behavior(unitpath, addlist, savepath):
    for i in addlist:
        curr_path = unitpath + i
        final_path = UNIT_PATH + i
        save_path = savepath + final_path

        loc_unit = "unit.json" 
        loc_img = "img.png"

        if os.path.isfile(curr_path + "meta.json"):
            with open(curr_path + "meta.json") as infile:
                meta = json.load(infile)
            if "unit" in meta:
                loc_unit = meta["unit"]
            if "img" in meta:
                loc_img = meta["img"]
    
        with open(curr_path + loc_unit) as infile:
            json_string = infile.read()
        
        (inc_files, json_strings) = full_substitution(json_string, i, loc_unit, curr_path)

        os.makedirs(save_path, exist_ok=True)
        for j in inc_files:
            savefile = save_path + j
            if j not in json_strings.keys():
                print("HOI")
                shutil.copyfile(curr_path + j, savefile)
            else:
                with open(savefile, 'w') as output:
                    output.write(json_strings[j])
        shutil.copyfile(curr_path + loc_img, save_path + loc_img[0:-4] + "png")


def direct_function(client, server, test, fullmod, modname, unitpath, addlistpath, savepath): 
    with open(addlistpath) as infile:
        addlist = infile.readlines()

    for i in range(len(addlist)):
        addlist[i] = addlist[i].rstrip('\n')

    print(addlist)

    if client:
        client_behavior(unitpath, addlist, savepath)
    if server:
        server_behavior(unitpath, addlist, savepath, modname)

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