import mushr_neomodel
import pandas as pd
from datetime import datetime
import re

spawn_df = pd.read_excel(
    "~/Cloud/TUCloud/ETCE (2)/projects/2022_MushR/0_ACCOUNTING-Musshrooms.ods",
    "Körnerbrut")[4:]


spawn_columns = ["bl", "id", "strain", "container", "substrate", "impfstoff",
                 "productionDate", "rff", "su", "blank", "notes", "recipie",
                 "sterile", "remarks"]

spawn_df.columns = spawn_columns

strains = {"pilzmänchen_pioppino": {"weight": 400,
                                    "source": "Pilzmänchen",
                                    "species": "Agrocybe aegerita",
                                    "mushroomCommonName": "Pioppino"},
           "pilzmänchen_oyster": {"weight": 600,
                                  "source": "Pilzmänchen",
                                  "species": "Pleurotus ostreatus",
                                  "mushroomCommonName": "Oyster"},
           "KB#25_BL": {"weight": 200,
                        "source": "KB#25 from BL",
                        "species": "Pleurotus ostreatus",
                        "mushroomCommonName": "Oyster"},
           "KB#23_BL": {"weight": 200,
                        "source": "KB#23 from BL",
                        "species": "Pleurotus ostreatus",
                        "mushroomCommonName": "Oyster"},
           "bucket_oyster": {"weight": 200,
                             "source": "came with the bucket",
                             "species": "Pleurotus ostreatus",
                             "mushroomCommonName": "Oyster"},
           "KB#26_BL": {"weight": 200,
                        "source": "KB#26 from BL",
                        "species": "Pleurotus ostreatus",
                        "mushroomCommonName": "Oyster"},
           "X_king_oyster": {"weight": 400,
                             "source": "Gekauft von X",
                             "species": "Pleurotus eryngii",
                             "mushroomCommonName": "King Oyster"},
           "LM10ml_king_oyster": {"weight": 400,
                                  "source": "Gekauft von X",
                                  "species": "Pleurotus eryngii",
                                  "mushroomCommonName": "King Oyster"},
           "LM10ml_oyster": {"weight": 400,
                             "source": "Gekauft von X",
                             "species": "Pleurotus ostreatus",
                             "mushroomCommonName": "Oyster"},
           "#": {"weight": 100,
                 "source": "No idea (unknown)",
                 "species": "Pleurotus ostreatus (probably)",
                 "mushroomCommonName": "Oyster*"},
           "#bucket_oyster": {"weight": 100,
                              "source": "Purchased",
                              "species": "Pleurotus ostreatus",
                              "mushroomCommonName": "Oyster"}
           }

strain_nodes = {}

for key, strain in strains.items():
    strain_nodes[key] = mushr_neomodel.Strain(
        weight=strain["weight"],
        source=strain["source"]+"("+key+")",
        species=strain["species"],
        mushroomCommonName=strain["mushroomCommonName"])
    strain_nodes[key].save()


spawn_nodes = dict(strain_nodes)

for index, row in spawn_df.iterrows():

    currid = "#" + str(row["id"])

    dateCreated = datetime.strptime(row["productionDate"],
                                    "%d.%m.%Y").astimezone()
    print(type(str(row["recipie"])), row["recipie"])
    spawn_nodes[currid] = mushr_neomodel.Spawn(
        composition=(str(row["recipie"]) + " (" + str(row["id"]) + ")"),
        weight=200,
        dateCreated=dateCreated)
    spawn_nodes[currid].save()

    innoculant = spawn_nodes[row["impfstoff"]]
    if dateCreated < innoculant.dateCreated:
        innoculant.dateCreated = dateCreated
        innoculant.save()

    spawn_nodes[currid].is_innoculated_from.connect(
        innoculant,
        {"timestamp": datetime.strptime(row["productionDate"],
                                        "%d.%m.%Y").astimezone(),
         "amount": 100})


substrate_df = pd.read_excel(
    "~/Cloud/TUCloud/ETCE (2)/projects/2022_MushR/0_ACCOUNTING-Musshrooms.ods",
    "Ertrag")[7:]


substrate_columns = ["bl", "id", "strain", "container", "substrate",
                     "manufacturer", "productionDate", "fd1", "mhd1",
                     "mh1", "fd2", "mhd2", "mh2", "fd3", "mhd3",
                     "mh3", "bl2", "overall", "notes", "recipie",
                     "sterile", "who"]

substrate_df.columns = substrate_columns

substrate_nodes = []

for index, row in substrate_df.iterrows():
    if not row["id"]:
        break
    innoculants = re.search(r"\((.+)\)", row["strain"]).group(1)

    innoculants = innoculants.split("+")

    print(row["id"], innoculants)
    dateCreated = datetime.strptime(row["productionDate"],
                                    "%d.%m.%Y").astimezone()

    substrate = mushr_neomodel.Substrate(weight=1500,
                                         composition=str(row["recipie"])+" ("+str(row["id"])+")",
                                         dateCreated=dateCreated)
    substrate.save()

    dummy_fruiting_hole = mushr_neomodel.FruitingHole(dateCreated=dateCreated)

    for innoculant in innoculants:
        substrate.is_innoculated_from.connect(spawn_nodes[innoculant],
                                              {"amount": 200,
                                               "timestamp": dateCreated})

    try:
        fd1 = datetime.strptime(row["fd1"],
                                "%d.%m.%Y").astimezone()
        flush1 = mushr_neomodel.Flush()
        flush1.save()
        relff1 = flush1.fruits_from.connect(substrate)
        dummy_fruiting_hole.save()
        relft1 = flush1.fruits_through.connect(dummy_fruiting_hole,
                                               {"start": fd1})
        print(row["id"], fd1)

    except Exception as E:
        print(E, fd1)
        continue

    try:
        mhd1 = datetime.strptime(row["mhd1"],
                                 "%d.%m.%Y").astimezone()

        relft1.end = mhd1
        relft1.save()
        print(row["id"], fd1, mhd1)

    except Exception as E:
        relft1.end1 = fd1
        relft1.save()
        print(E, mhd1)
        continue

    try:
        mh1 = row["mh1"]
        mh1_node = mushr_neomodel.MushroomHarvest(weight=mh1,
                                                  dateHarvested=mhd1)
        mh1_node.save()
        mh1_node.is_harvested_from.connect(flush1)

        print(row["id"], fd1, mhd1, mh1)

    except Exception as E:
        print(E, mh1)
        continue

    try:
        fd2 = datetime.strptime(row["fd2"],
                                "%d.%m.%Y").astimezone()
        flush2 = mushr_neomodel.Flush()
        flush2.save()
        relff2 = flush2.fruits_from.connect(substrate)
        relft2 = flush2.fruits_through.connect(dummy_fruiting_hole,
                                               {"start": fd2})
        print(row["id"], fd2)

    except Exception as E:
        print(E, fd2)
        continue

    try:
        mhd2 = datetime.strptime(row["mhd2"],
                                 "%d.%m.%Y").astimezone()

        relft2.end = mhd2
        relft2.save()
        print(row["id"], fd2, mhd2)

    except Exception as E:
        relft2.end = fd2
        relft2.save()
        print(E, mhd2)
        continue

    try:
        mh2 = row["mh2"]
        mh2_node = mushr_neomodel.MushroomHarvest(weight=mh2,
                                                  dateHarvested=mhd2)
        mh2_node.save()
        mh2_node.is_harvested_from.connect(flush2)

        print(row["id"], fd2, mhd2, mh2)

    except Exception as E:
        print(E, mh1)
        continue
    try:
        fd3 = datetime.strptime(row["fd3"],
                                "%d.%m.%Y").astimezone()
        flush3 = mushr_neomodel.Flush()
        flush3.save()
        relff3 = flush3.fruits_from.connect(substrate)
        relft3 = flush3.fruits_through.connect(dummy_fruiting_hole,
                                               {"start": fd3})
        print(row["id"], fd3)

    except Exception as E:
        print(E, fd3)
        continue

    try:
        mhd3 = datetime.strptime(row["mhd3"],
                                 "%d.%m.%Y").astimezone()

        relft3.end = mhd3
        relft3.save()
        print(row["id"], fd3, mhd3)

    except Exception as E:
        relft3.end = fd3
        relft3.save()
        print(E, mhd3)
        continue

    try:
        mh3 = row["mh3"]
        mh3_node = mushr_neomodel.MushroomHarvest(weight=mh3,
                                                  dateHarvested=mhd3)
        mh3_node.save()
        mh3_node.is_harvested_from.connect(flush3)

        print(row["id"], fd3, mhd3, mh3)

    except Exception as E:
        print(E, mh3)
        continue
