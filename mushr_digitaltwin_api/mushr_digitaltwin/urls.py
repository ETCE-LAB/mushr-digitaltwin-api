from django.urls import path, register_converter
# from rest_framework.urlpatterns import format_suffix_patterns
from mushr_digitaltwin import views
from mushr_digitaltwin.converters import ISO8601Converter

register_converter(ISO8601Converter, "ISO8601DateTime")

urlpatterns = [

    # Paths for main nodes

    path("substrate/", views.SubstrateUIDs.as_view()),
    path("substrate/<ISO8601DateTime:timestamp>", views.SubstrateUIDs.as_view()),
    path("substrate/all/", views.SubstrateNodes.as_view()),
    path("substrate/all/<ISO8601DateTime:timestamp>", views.SubstrateNodes.as_view()),
    path("substrate/create/<substrate_container_uid>", views.CreateSubstrate.as_view()),
    path("substrate/active/", views.ActiveSubstrateUIDs.as_view()),
    path("substrate/active/<ISO8601DateTime:timestamp>", views.ActiveSubstrateUIDs.as_view()),
    path("substrate/innoculable/", views.InnoculableSubstrateUIDs.as_view()),
    path("substrate/innoculable/<ISO8601DateTime:timestamp>", views.InnoculableSubstrateUIDs.as_view()),
    path("substrate/innoculated/", views.InnoculatedSubstrateUIDs.as_view()),
    path("substrate/innoculated/<ISO8601DateTime:timestamp>", views.InnoculatedSubstrateUIDs.as_view()),
    path("substrate/<uid>/", views.SubstrateInstance.as_view()),

    path("location/", views.LocationUIDs.as_view()),
    path("location/<ISO8601DateTime:timestamp>", views.LocationUIDs.as_view()),
    path("location/all/", views.LocationNodes.as_view()),
    path("location/all/<ISO8601DateTime:timestamp>", views.LocationNodes.as_view()),
    path("location/<uid>/", views.LocationInstance.as_view()),

    path("grow_chamber/", views.GrowChamberUIDs.as_view()),
    path("grow_chamber/all", views.GrowChamberNodes.as_view()),
    path("grow_chamber/create", views.CreateGrowChamberInstance.as_view()),
    path("grow_chamber/<ISO8601DateTime:timestamp>", views.GrowChamberUIDs.as_view()),
    path("grow_chamber/all/<ISO8601DateTime:timestamp>", views.GrowChamberNodes.as_view()),
    path("grow_chamber/<uid>/", views.GrowChamberInstance.as_view()),
    path("grow_chamber/<uid>/active_substrate_containers/", views.GrowChamberActiveSubstrateContainers.as_view()),
    path("grow_chamber/<uid>/active_substrate_containers/<ISO8601DateTime:timestamp>", views.GrowChamberActiveSubstrateContainers.as_view()),

    path("storage_location/", views.StorageLocationUIDs.as_view()),
    path("storage_location/<ISO8601DateTime:timestamp>", views.StorageLocationUIDs.as_view()),
    path("storage_location/all/", views.StorageLocationNodes.as_view()),
    path("storage_location/all/<ISO8601DateTime:timestamp>", views.StorageLocationNodes.as_view()),
    path("storage_location/create", views.CreateStorageLocationInstance.as_view()),
    path("storage_location/<uid>/", views.StorageLocationInstance.as_view()),

    path("mycelium_sample/", views.MyceliumSampleUIDs.as_view()),
    path("mycelium_sample/<ISO8601DateTime:timestamp>", views.MyceliumSampleUIDs.as_view()),
    path("mycelium_sample/all/", views.MyceliumSampleNodes.as_view()),
    path("mycelium_sample/all/<ISO8601DateTime:timestamp>", views.MyceliumSampleNodes.as_view()),
    path("mycelium_sample/<uid>/", views.MyceliumSampleInstance.as_view()),

    path("strain/", views.StrainUIDs.as_view()),
    path("strain/create", views.CreateStrainInstance.as_view()),
    path("strain/<ISO8601DateTime:timestamp>", views.StrainUIDs.as_view()),
    path("strain/all/", views.StrainNodes.as_view()),
    path("strain/all/<ISO8601DateTime:timestamp>", views.StrainNodes.as_view()),
    path("strain/<uid>/", views.StrainInstance.as_view()),
    path("strain/<uid>/active_spawns/", views.StrainActiveSpawns.as_view()),
    path("strain/<uid>/active_spawns/<ISO8601DateTime:timestamp>", views.StrainActiveSpawns.as_view()),
    path("strain/<uid>/active_substrates/", views.StrainActiveSubstrates.as_view()),
    path("strain/<uid>/active_substrates/<ISO8601DateTime:timestamp>", views.StrainActiveSubstrates.as_view()),

    path("spawn/", views.SpawnUIDs.as_view()),
    path("spawn/create/<spawn_container_uid>", views.CreateSpawn.as_view()),
    path("spawn/<ISO8601DateTime:timestamp>", views.SpawnUIDs.as_view()),
    path("spawn/all/", views.SpawnNodes.as_view()),
    path("spawn/all/<ISO8601DateTime:timestamp>", views.SpawnNodes.as_view()),
    path("spawn/active/", views.ActiveSpawnUIDs.as_view()),
    path("spawn/active/<ISO8601DateTime:timestamp>", views.ActiveSpawnUIDs.as_view()),
    path("spawn/innoculable/", views.InnoculableSpawnUIDs.as_view()),
    path("spawn/innoculable/<ISO8601DateTime:timestamp>", views.InnoculableSpawnUIDs.as_view()),
    path("spawn/innoculated/", views.InnoculatedSpawnUIDs.as_view()),
    path("spawn/innoculated/<ISO8601DateTime:timestamp>", views.InnoculatedSpawnUIDs.as_view()),
    path("spawn/<uid>/", views.SpawnInstance.as_view()),

    path("spawn_container/", views.SpawnContainerUIDs.as_view()),
    path("spawn_container/create", views.CreateSpawnContainerInstance.as_view()),
    path("spawn_container/empty/", views.FreeSpawnContainerUIDs.as_view()),
    path("spawn_container/empty/<ISO8601DateTime:timestamp>", views.FreeSpawnContainerUIDs.as_view()),
    path("spawn_container/<ISO8601DateTime:timestamp>", views.SpawnContainerUIDs.as_view()),
    path("spawn_container/all/", views.SpawnContainerNodes.as_view()),
    path("spawn_container/all/<ISO8601DateTime:timestamp>", views.SpawnContainerNodes.as_view()),
    path("spawn_container/<uid>/", views.SpawnContainerInstance.as_view()),
    path("spawn_container/<uid>/change_storage_location/<location_uid>", views.ChangeSpawnContainerStorageLocation.as_view()),
    path("spawn_container/<uid>/location_at_timestamp/<ISO8601DateTime:timestamp>", views.SpawnContainerLocationAtTimestamp.as_view()),
    path("spawn_container/<uid>/spawn_at_timestamp/<ISO8601DateTime:timestamp>", views.SpawnContainerSpawnAtTimestamp.as_view()),

    path("substrate_container/", views.SubstrateContainerUIDs.as_view()),
    path("substrate_container/create/<int:num_fruiting_holes>", views.CreateSubstrateContainerInstance.as_view()),
    path("substrate_container/empty/", views.FreeSubstrateContainerUIDs.as_view()),
    path("substrate_container/empty/<ISO8601DateTime:timestamp>", views.FreeSubstrateContainerUIDs.as_view()),
    path("substrate_container/<ISO8601DateTime:timestamp>", views.SubstrateContainerUIDs.as_view()),
    path("substrate_container/all/", views.SubstrateContainerNodes.as_view()),
    path("substrate_container/all/<ISO8601DateTime:timestamp>", views.SubstrateContainerNodes.as_view()),
    path("substrate_container/<uid>/", views.SubstrateContainerInstance.as_view()),
    path("substrate_container/<uid>/change_storage_location/<location_uid>", views.ChangeSubstrateContainerStorageLocation.as_view()),
    path("substrate_container/<uid>/location_at_timestamp/<ISO8601DateTime:timestamp>", views.SubstrateContainerLocationAtTimestamp.as_view()),
    path("substrate_container/<uid>/substrate_at_timestamp/<ISO8601DateTime:timestamp>", views.SubstrateContainerSubstrateAtTimestamp.as_view()),

    path("fruiting_hole/", views.FruitingHoleUIDs.as_view()),
    path("fruiting_hole/<ISO8601DateTime:timestamp>", views.FruitingHoleUIDs.as_view()),
    path("fruiting_hole/all/", views.FruitingHoleNodes.as_view()),
    path("fruiting_hole/all/<ISO8601DateTime:timestamp>", views.FruitingHoleNodes.as_view()),
    path("fruiting_hole/available_for_fruiting", views.AvailableFruitingHoles.as_view()),
    path("fruiting_hole/available_for_harvesting", views.HarvestableFruitingHoles.as_view()),
    path("fruiting_hole/<uid>/", views.FruitingHoleInstance.as_view()),
    path("fruiting_hole/<uid>/active_flushes/<ISO8601DateTime:timestamp>", views.FruitingHoleActiveFlushes.as_view()),

    path("flush/", views.FlushUIDs.as_view()),
    path("flush/<ISO8601DateTime:timestamp>", views.FlushUIDs.as_view()),
    path("flush/all/", views.FlushNodes.as_view()),
    path("flush/all/<ISO8601DateTime:timestamp>", views.FlushNodes.as_view()),
    path("flush/<uid>/", views.FlushInstance.as_view()),


    path("mushroom_harvest/", views.MushroomHarvestUIDs.as_view()),
    path("mushroom_harvest/<ISO8601DateTime:timestamp>", views.MushroomHarvestUIDs.as_view()),
    path("mushroom_harvest/all/", views.MushroomHarvestNodes.as_view()),
    path("mushroom_harvest/all/<ISO8601DateTime:timestamp>", views.MushroomHarvestNodes.as_view()),
    path("mushroom_harvest/<uid>/", views.MushroomHarvestInstance.as_view()),

    path("sensor/", views.SensorUIDs.as_view()),
    path("sensor/create/<grow_chamber_uid>", views.CreateSensor.as_view()),
    path("sensor/<ISO8601DateTime:timestamp>", views.SensorUIDs.as_view()),
    path("sensor/all/", views.SensorNodes.as_view()),
    path("sensor/all/<ISO8601DateTime:timestamp>", views.SensorNodes.as_view()),
    path("sensor/<uid>/", views.SensorInstance.as_view()),
    path("sensor/<uid>/stop_sensing", views.StopSensing.as_view()),

    # Paths for specific relationships

    path("is_descendent_of_relationship/<int:id>", views.MushRIsDescendentOfRelationshipInstance.as_view()),
    path("is_located_at_relationship/<int:id>", views.MushRIsLocatedAtRelationshipInstance.as_view()),


    # Actions
    path("discard_spawn/<spawn_container_uid>", views.DiscardSpawn.as_view()),
    path("discard_substrate/<substrate_container_uid>", views.DiscardSubstrate.as_view()),
    path("innoculate/<innoculant_uid>/<recipient_container_uid>", views.Innoculate.as_view()),
    path("start_fruiting/<fruiting_hole_uid>/<grow_chamber_uid>", views.StartFruiting.as_view()),
    path("harvest/<fruiting_hole_uid>", views.Harvest.as_view()),
]
