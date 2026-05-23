# ==============================================================================
# core/settings_data.py
# Settings Data Module
# Contains the official Pocketpair documentation template and parameter descriptions.
# ==============================================================================

DEFAULT_SETTINGS_TEMPLATE = (
    "[/Script/Pal.PalGameWorldSettings]\n"
    "OptionSettings=(Difficulty=None,RandomizerType=None,RandomizerSeed=\"\",bIsRandomizerPalLevelRandom=False,"
    "DayTimeSpeedRate=1.000000,NightTimeSpeedRate=1.000000,ExpRate=1.000000,PalCaptureRate=1.000000,"
    "PalSpawnNumRate=1.000000,PalDamageRateAttack=1.000000,PalDamageRateDefense=1.000000,PlayerDamageRateAttack=1.000000,"
    "PlayerDamageRateDefense=1.000000,PlayerStomachDecreaceRate=1.000000,PlayerStaminaDecreaceRate=1.000000,PlayerAutoHPRegeneRate=1.000000,"
    "PlayerAutoHpRegeneRateInSleep=1.000000,PalStomachDecreaceRate=1.000000,PalStaminaDecreaceRate=1.000000,PalAutoHPRegeneRate=1.000000,"
    "PalAutoHpRegeneRateInSleep=1.000000,BuildObjectHpRate=1.000000,BuildObjectDamageRate=1.000000,BuildObjectDeteriorationDamageRate=1.000000,"
    "CollectionDropRate=1.000000,CollectionObjectHpRate=1.000000,CollectionObjectRespawnSpeedRate=1.000000,EnemyDropItemRate=1.000000,"
    "DeathPenalty=Item,bEnablePlayerToPlayerDamage=False,bEnableFriendlyFire=False,bEnableInvaderEnemy=True,"
    "bActiveUNKO=False,bEnableAimAssistPad=True,bEnableAimAssistKeyboard=False,DropItemMaxNum=3000,"
    "DropItemMaxNum_UNKO=100,BaseCampMaxNum=128,BaseCampWorkerMaxNum=15,DropItemAliveMaxHours=1.000000,"
    "bAutoResetGuildNoOnlinePlayers=False,AutoResetGuildTimeNoOnlinePlayers=72.000000,GuildPlayerMaxNum=20,BaseCampMaxNumInGuild=4,"
    "PalEggDefaultHatchingTime=2.000000,WorkSpeedRate=1.000000,AutoSaveSpan=30.000000,bIsMultiplay=False,"
    "bIsPvP=False,bHardcore=False,bPalLost=False,bCharacterRecreateInHardcore=False,"
    "bCanPickupOtherGuildDeathPenaltyDrop=False,bEnableNonLoginPenalty=True,bEnableFastTravel=True,bEnableFastTravelOnlyBaseCamp=False,"
    "bIsStartLocationSelectByMap=True,bExistPlayerAfterLogout=False,bEnableDefenseOtherGuildPlayer=False,bInvisibleOtherGuildBaseCampAreaFX=False,"
    "bBuildAreaLimit=True,ItemWeightRate=1.000000,CoopPlayerMaxNum=4,ServerPlayerMaxNum=32,"
    "ServerName=\"Default Palworld Server\",ServerDescription=\"\",AdminPassword=\"\",ServerPassword=\"\","
    "bAllowClientMod=False,PublicPort=8211,PublicIP=\"\",RCONEnabled=False,"
    "RCONPort=25575,Region=\"\",bUseAuth=True,BanListURL=\"https://api.palworldgame.com/api/banlist.txt\","
    "RESTAPIEnabled=False,RESTAPIPort=8212,bShowPlayerList=True,ChatPostLimitPerMinute=10,"
    "CrossplayPlatforms=(Steam,Xbox,PS5,Mac),bIsUseBackupSaveData=True,LogFormatType=Text,bIsShowJoinLeftMessage=True,"
    "SupplyDropSpan=180,EnablePredatorBossPal=True,MaxBuildingLimitNum=0,ServerReplicatePawnCullDistance=15000.000000,"
    "bAllowGlobalPalboxExport=False,bAllowGlobalPalboxImport=False,EquipmentDurabilityDamageRate=1.000000,ItemContainerForceMarkDirtyInterval=10,"
    "ItemCorruptionMultiplier=1.000000,DenyTechnologyList=(),GuildRejoinCooldownMinutes=0,BlockRespawnTime=0,"
    "RespawnPenaltyDurationThreshold=10,RespawnPenaltyTimeScale=1.000000,bDisplayPvPItemNumOnWorldMap_BaseCamp=False,bDisplayPvPItemNumOnWorldMap_Player=False,"
    "AdditionalDropItemWhenPlayerKillingInPvPMode=\"\",AdditionalDropItemNumWhenPlayerKillingInPvPMode=0,bAdditionalDropItemWhenPlayerKillingInPvPMode=False,bAllowEnhanceStat_Health=True,"
    "bAllowEnhanceStat_Attack=True,bAllowEnhanceStat_Stamina=True,bAllowEnhanceStat_Weight=True,bAllowEnhanceStat_WorkSpeed=True,"
    "bActiveUNRTONativeRollback=False,bActiveFirstJobMod=False,bGuildPlayerMoveLimitDefense=False,DropItemPoolMaxNum=3000,DropItemAliveTime=3600.000000,AllowConnectPlatform=\"\")"
)

SETTINGS_HELP = {
    "ServerName": "Server Name visible in the browser selection tree.",
    "ServerDescription": "Server Description text details.",
    "ServerPassword": "Password required for regular players to log in.",
    "AdminPassword": "Password used to obtain administrative privileges on the server.",
    "PublicIP": "Explicitly specify an external public IP in the community server settings.",
    "PublicPort": "Explicitly specify the external public port in the community server configuration.",
    "Region": "Purely informational geographical region tracker.",
    "ServerPlayerMaxNum": "Maximum number of concurrent players allowed on the server.",
    "AllowConnectPlatform": "Specify which platforms are allowed to connect.",
    "bUseAuth": "Verifies the identity of players upon connection via official platform tokens.",
    "BanListURL": "URL of the global player bans database list text file.",
    "bShowPlayerList": "Enable player list viewing when pressing the ESC key in-game.",
    "RCONEnabled": "Enables remote console administrative connection access protocol.",
    "RCONPort": "Target listening port used for incoming RCON query links.",
    "RESTAPIEnabled": "Enables local advanced REST API monitoring systems.",
    "RESTAPIPort": "Listen port configuration details for REST API queries.",
    "Difficulty": "Difficulty Level selector flag.",
    "DayTimeSpeedRate": "Daytime passage speed modifier scale.",
    "NightTimeSpeedRate": "Nighttime passage speed modifier scale.",
    "RandomizerType": "Pal spawn randomization mode configurations.",
    "RandomizerSeed": "Seed value used when spawn randomization mode is enabled.",
    "SupplyDropSpan": "Interval duration in minutes for scheduled supply drop events.",
    "EnablePredatorBossPal": "Enables predator boss Pals options on map layers.",
    "ServerReplicatePawnCullDistance": "Entity network synchronization and render distance threshold (cm).",
    "ExpRate": "Global experience acquisition rate multiplier.",
    "PalCaptureRate": "Base multiplier chance for successfully capturing wild Pals.",
    "PalSpawnNumRate": "Wild Pal group density scaling layout parameter.",
    "CollectionDropRate": "Resource node harvest quantity yield multiplier.",
    "CollectionObjectRespawnSpeedRate": "Respawn speed multiplier for harvestable resource nodes.",
    "EnemyDropItemRate": "Loot item drop rate multiplier from defeated targets.",
    "WorkSpeedRate": "Pal base camp crafting efficiency operation speed scaling factor.",
    "ItemWeightRate": "Global modifier scaling character inventory weight values.",
    "DeathPenalty": "Configures inventory item and asset retainment rules upon player death.",
    "bEnablePlayerToPlayerDamage": "Enables or disables standard Player vs Player combat interactions.",
    "bEnableFriendlyFire": "Enables or disables friendly fire within identical guild groups.",
    "bIsPvP": "Toggles global server Player vs Player tracking logic parameters.",
    "bHardcore": "Enables permadeath mode. Defeated players cannot respawn.",
    "bPalLost": "Permanently deletes any Pals currently assigned to the player's party upon death.",
    "bEnableInvaderEnemy": "Toggles base raid events by hostile groups.",
    "PalDamageRateAttack": "Multiplier adjusting total output damage inflicted by Pals.",
    "PalDamageRateDefense": "Multiplier adjusting total incoming damage absorption by Pals.",
    "PlayerDamageRateAttack": "Multiplier adjusting total output damage inflicted by players.",
    "PlayerDamageRateDefense": "Multiplier adjusting total incoming damage absorption by players.",
    "PlayerStomachDecreaceRate": "Satiety level depletion rate multiplier for player characters.",
    "PlayerStaminaDecreaceRate": "Stamina level drain rate multiplier for player actions.",
    "PlayerAutoHPRegeneRate": "Natural automated health regeneration scale for active players.",
    "PlayerAutoHpRegeneRateInSleep": "Health regeneration scaling factor for characters resting inside beds.",
    "PalStomachDecreaceRate": "Satiety level depletion rate multiplier for camp and party Pals.",
    "PalStaminaDecreaceRate": "Stamina level drain rate multiplier for working or combat Pals.",
    "PalAutoHPRegeneRate": "Natural automated health regeneration scale for active Pals.",
    "PalAutoHpRegeneRateInSleep": "Health regeneration scaling factor for Pals resting within the Palbox.",
    "bActiveUNKO": "Enables unconscious state recovery mechanics instead of traditional immediate death.",
    "bEnableAimAssistPad": "Enables aim assist targeting functionality for controller hardware links.",
    "bEnableAimAssistKeyboard": "Enables aim assist targeting functionality for keyboard and mouse setups.",
    "bEnableDefenseOtherGuildPlayer": "Enables automated base defense behaviors against visiting external players.",
    "BuildObjectHpRate": "Health scale modifier applied to player-built base structures.",
    "BuildObjectDamageRate": "Incoming damage multiplier applied to player-built base structures.",
    "BuildObjectDeteriorationDamageRate": "Decay degradation scaling factor for assets placed outside base boundaries.",
    "CollectionObjectHpRate": "Health scale tracker governing harvestable world resource nodes.",
    "DropItemMaxNum": "Global server entity physics limit tracking dropped items before garbage cleanups.",
    "DropItemMaxNum_UNKO": "Maximum allowed dropped item instances dropped specifically by unconscious targets.",
    "DropItemAliveMaxHours": "Maximum persistence lifespan hours for dropped ground loot items.",
    "bCanPickupOtherGuildDeathPenaltyDrop": "Allows players from alternate guilds to loot coordinates of death penalty containers.",
    "BaseCampMaxNum": "Global absolute limits monitoring maximum base structures built simultaneously.",
    "BaseCampWorkerMaxNum": "Maximum number of working Pals allowed to deploy within a base grid footprint.",
    "BaseCampMaxNumInGuild": "Maximum allowed base camp base layouts associated to a single guild group.",
    "GuildPlayerMaxNum": "Maximum number of active player profiles allowed to join an individual guild.",
    "bAutoResetGuildNoOnlinePlayers": "Automatically disbands inactive guilds when no members connect over extended periods.",
    "AutoResetGuildTimeNoOnlinePlayers": "Lifespan countdown in hours required before inactive guild auto-wipes activate.",
    "PalEggDefaultHatchingTime": "Time duration requirement in hours tracking massive egg incubation completions.",
    "bInvisibleOtherGuildBaseCampAreaFX": "Toggles rendering transparency configurations for alternate guild base boundary lines.",
    "bBuildAreaLimit": "Enables anti-grief zoning restrictions near key structures or fast-travel hubs.",
    "MaxBuildingLimitNum": "Enables asset counts limit per player profile. Zero designates unrestricted access.",
    "AutoSaveSpan": "Auto-save persistence write runtime backup loop countdown track (minutes).",
    "ChatPostLimitPerMinute": "Anti-spam message limits tracking player terminal submissions per minute.",
    "bIsMultiplay": "Toggles internal engine multiplayer session parameters.",
    "bEnableNonLoginPenalty": "Enables penalty rules applied to accounts offline for extended periods.",
    "bEnableFastTravel": "Enables mapping fast travel point transitions globally.",
    "bEnableFastTravelOnlyBaseCamp": "Restricts active fast travel sequences exclusively between built base terminal grids.",
    "bIsStartLocationSelectByMap": "Allows newly authenticated connections to pick spawn zones via the world map grid.",
    "bExistPlayerAfterLogout": "Causes player character models to remain sleeping in the world after logging out.",
    "bIsUseBackupSaveData": "Enables local rolling save file history logs backups.",
    "LogFormatType": "Configures console logger data structure options to standard Text or Json layers.",
    "bIsShowJoinLeftMessage": "Toggles standard global text chat alerts when accounts connect or disconnect.",
    "bAllowClientMod": "Allows players running local custom mod software packages to authenticate and join.",
    "CrossplayPlatforms": "Platforms allowed to link. (Default parameters: Steam, Xbox, PS5, Mac).",
    "EquipmentDurabilityDamageRate": "Durability reduction speed multiplier governing tools and armor pieces.",
    "ItemContainerForceMarkDirtyInterval": "Synchronization frequency interval seconds governing container data links.",
    "ItemCorruptionMultiplier": "Item spoilage decay timeline multiplier parameters for perishable resources.",
    "bAdditionalDropItemWhenPlayerKillingInPvPMode": "Toggles dropping a special event item when killing players in active PvP zones.",
    "AdditionalDropItemWhenPlayerKillingInPvPMode": "Item ID string that drops when dropping items in PvP.",
    "AdditionalDropItemNumWhenPlayerKillingInPvPMode": "Item quantity count that drops when killing players in PvP.",
    "bAllowGlobalPalboxImport": "Allows profile structures to retrieve Pal logs from synchronized global storage box grids.",
    "bAllowGlobalPalboxExport": "Allows profile structures to save Pal logs out to synchronized global storage box grids.",
    "GuildRejoinCooldownMinutes": "Required cooldown tracking minutes before rejoining a guild structure you voluntarily left.",
    "BlockRespawnTime": "Enforces a required death configuration wait duration before respawning actions become selectable.",
    "RespawnPenaltyDurationThreshold": "Regulates timeline windows scaling initial death penalty calculations.",
    "RespawnPenaltyTimeScale": "Time multiplier parameters governing calculation delays on subsequent deaths.",
    "bAllowEnhanceStat_Health": "Allows stat progression tracking values to scale character Maximum HP metrics.",
    "bAllowEnhanceStat_Attack": "Allows stat progression tracking values to scale character Base Attack metrics.",
    "bAllowEnhanceStat_Stamina": "Allows stat progression tracking values to scale character Maximum Stamina metrics.",
    "bAllowEnhanceStat_WorkSpeed": "Allows stat progression tracking values to scale character Base Work Efficiency metrics.",
    "bAllowEnhanceStat_Weight": "Allows stat progression tracking values to scale character Inventory Carrying Weight limits.",
    "bIsRandomizerPalLevelRandom": "Completely un-pairs randomized wild spawn level constraints from native area brackets.",
    "bDisplayPvPItemNumOnWorldMap_Player": "Enables map icon tracking overlays displaying location indices for player assets in PvP configurations.",
    "bDisplayPvPItemNumOnWorldMap_BaseCamp": "Enables map icon tracking overlays displaying storage quantities for player bases in PvP configurations.",
    "DenyTechnologyList": "Specifies arrays of forbidden structural Technology database entry IDs that block unlocks.",
    "bActiveUNRTONativeRollback": "Toggles internal network debugging rollback tracking algorithms.",
    "bActiveFirstJobMod": "Enables specialized first-job character capability modifier variables.",
    "bGuildPlayerMoveLimitDefense": "Restricts asset movement rules boundaries during active guild base territory defenses.",
    "DropItemPoolMaxNum": "Defines physics threshold boundaries tracking aggregate loose dropped ground items before cleanups.",
    "DropItemAliveTime": "Maximum allowed lifespan duration tracking loose ground items before cleanup garbage cycles trigger."
}