# ==============================================================================
# views/settings_view.py
# Settings View Module - Balanced Split View
# ==============================================================================

import re
import os
import customtkinter as ctk
import tkinter.messagebox as messagebox

from core.settings_data import SETTINGS_HELP, DEFAULT_SETTINGS_TEMPLATE
from core.tooltip import ToolTip
from core.metrics_controller import is_server_running_on_system
from core.ui_components import StandardTab, StandardCard, InnerCard, COLOR_NEON_BLUE

SETTINGS_CATEGORIES = {
    "🌐 CONNECTION & SECURITY": [
        "ServerName", "ServerDescription", "ServerPassword", "AdminPassword",
        "PublicIP", "PublicPort", "Region", "ServerPlayerMaxNum", "bUseAuth",
        "BanListURL", "RCONEnabled", "RCONPort", "RESTAPIEnabled", "RESTAPIPort",
        "bIsShowJoinLeftMessage", "CrossplayPlatforms", "bAllowClientMod", "AllowConnectPlatform",
        "bShowPlayerList"
    ],
    "⚖️ DIFFICULTY & WORLD GENERATION": [
        "Difficulty", "DayTimeSpeedRate", "NightTimeSpeedRate", "RandomizerType",
        "RandomizerSeed", "SupplyDropSpan", "ServerReplicatePawnCullDistance", 
        "EnablePredatorBossPal", "bCharacterRecreateInHardcore", "bActiveUNRTONativeRollback", 
        "bActiveFirstJobMod", "CoopPlayerMaxNum"
    ],
    "📈 PROGRESSION & MULTIPLIERS": [
        "ExpRate", "PalCaptureRate", "PalSpawnNumRate", "CollectionDropRate",
        "CollectionObjectRespawnSpeedRate", "EnemyDropItemRate", "ItemWeightRate",
        "EquipmentDurabilityDamageRate", "ItemCorruptionMultiplier", "WorkSpeedRate"
    ],
    "⚔️ GAMEPLAY & COMBAT RULES": [
        "DeathPenalty", "bEnablePlayerToPlayerDamage", "bEnableFriendlyFire", "bIsPvP",
        "bHardcore", "bPalLost", "bEnableInvaderEnemy", "PalDamageRateAttack",
        "PalDamageRateDefense", "PlayerDamageRateAttack", "PlayerDamageRateDefense",
        "PlayerStomachDecreaceRate", "PlayerStaminaDecreaceRate", "PlayerAutoHPRegeneRate",
        "PlayerAutoHpRegeneRateInSleep", "PalStomachDecreaceRate", "PalStaminaDecreaceRate",
        "PalAutoHPRegeneRate", "PalAutoHpRegeneRateInSleep", "BlockRespawnTime",
        "RespawnPenaltyTimeScale", "RespawnPenaltyDurationThreshold", "bActiveUNKO",
        "bEnableAimAssistPad", "bEnableAimAssistKeyboard", "bEnableDefenseOtherGuildPlayer",
        "bAllowEnhanceStat_Health", "bAllowEnhanceStat_Attack", "bAllowEnhanceStat_Stamina",
        "bAllowEnhanceStat_WorkSpeed", "bAllowEnhanceStat_Weight", "bIsRandomizerPalLevelRandom"
    ],
    "⛺ CAMP & BUILDING MANAGEMENT": [
        "BuildObjectHpRate", "BuildObjectDamageRate", "BuildObjectDeteriorationDamageRate",
        "CollectionObjectHpRate", "DropItemMaxNum", "DropItemMaxNum_UNKO", "DropItemAliveMaxHours",
        "DropItemPoolMaxNum", "DropItemAliveTime", "bCanPickupOtherGuildDeathPenaltyDrop",
        "BaseCampMaxNum", "BaseCampWorkerMaxNum", "BaseCampMaxNumInGuild", "bGuildPlayerMoveLimitDefense",
        "GuildPlayerMaxNum", "bAutoResetGuildNoOnlinePlayers", "AutoResetGuildTimeNoOnlinePlayers",
        "PalEggDefaultHatchingTime", "bInvisibleOtherGuildBaseCampAreaFX", "bBuildAreaLimit",
        "MaxBuildingLimitNum", "GuildRejoinCooldownMinutes", "ItemContainerForceMarkDirtyInterval"
    ],
    "🛠️ SYSTEM LEVEL META OPTIONS": [
        "AutoSaveSpan", "ChatPostLimitPerMinute", "bIsMultiplay", "bEnableNonLoginPenalty",
        "bEnableFastTravel", "bEnableFastTravelOnlyBaseCamp", "bIsStartLocationSelectByMap",
        "bExistPlayerAfterLogout", "bIsUseBackupSaveData", "LogFormatType",
        "bAllowGlobalPalboxImport", "bAllowGlobalPalboxExport", "bDisplayPvPItemNumOnWorldMap_Player",
        "bDisplayPvPItemNumOnWorldMap_BaseCamp", "bAdditionalDropItemWhenPlayerKillingInPvPMode",
        "AdditionalDropItemWhenPlayerKillingInPvPMode", "AdditionalDropItemNumWhenPlayerKillingInPvPMode",
        "DenyTechnologyList"
    ]
}

PREDEFINED_ENUMS = {
    "Difficulty": ["None", "Easy", "Normal", "Hard"],
    "DeathPenalty": ["None", "Item", "ItemAndEquipment", "All"],
    "LogFormatType": ["Text", "Json"],
    "RandomizerType": ["None", "Basic", "Advanced", "Region", "All"]
}

def setup_settings_tab(app, tab):
    """Sets up the UI structure for the settings tab."""
    housing = StandardTab(tab)
    housing.pack(fill="both", expand=True)
    
    # Store the scrollable container reference
    app.settings_scroll_container = housing.container

    housing.add_header(
        "Palworld Server Configuration", 
        "Modify world settings, multipliers, and connection parameters for your dedicated server instance."
    )
    
    # Create the split chassis structure inside the scroll container
    app.settings_split_chassis = ctk.CTkFrame(app.settings_scroll_container, fg_color="transparent")
    app.settings_split_chassis.pack(fill="both", expand=True, padx=25)
    
    app.settings_split_chassis.grid_columnconfigure(0, weight=1, uniform="settings")
    app.settings_split_chassis.grid_columnconfigure(1, weight=1, uniform="settings")
    
    # Left and Right containers
    app.settings_col_left = ctk.CTkFrame(app.settings_split_chassis, fg_color="transparent")
    app.settings_col_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    app.settings_col_right = ctk.CTkFrame(app.settings_split_chassis, fg_color="transparent")
    app.settings_col_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

    app.setting_entries = {}

    # Footer Setup
    housing.footer.grid(row=1, column=0, sticky="ew", padx=15, pady=(5, 15))
    
    ctk.CTkLabel(
        housing.footer,
        text="⚠️ Ensure the game server is stopped before committing modifications.",
        font=("Segoe UI", 11, "italic"),
        text_color="#9CA3AF"
    ).pack(side="left", padx=20, pady=12)

    btn_save_config = ctk.CTkButton(
        housing.footer,
        text="SAVE CONFIGURATION PROFILE",
        height=36,
        width=240,
        fg_color=COLOR_NEON_BLUE,
        hover_color="#00B4CC",
        text_color="#08080A",
        font=("Segoe UI", 12, "bold"),
        command=app.save_settings
    )
    btn_save_config.pack(side="right", padx=15, pady=10)

    # Initial load will populate the columns
    load_settings_data(app)


def load_settings_data(app):
    """Loads configuration data and builds the input fields into the split view."""
    if not app.base_dir:
        return

    config_path = app.base_dir / "Pal/Saved/Config/WindowsServer/PalWorldSettings.ini"
    default_path = app.base_dir / "DefaultPalWorldSettings.ini"
    
    content = ""
    if config_path.exists() and os.path.getsize(config_path) > 0:
        try: content = config_path.read_text(encoding="utf-8")
        except Exception: content = config_path.read_text()
    
    if (not content or "OptionSettings=" not in content) and default_path.exists():
        try: content = default_path.read_text(encoding="utf-8")
        except Exception: content = default_path.read_text()
        app.log("Active configuration blank or missing. Loaded base variables from DefaultPalWorldSettings.ini.")

    if not content or "OptionSettings=" not in content:
        content = DEFAULT_SETTINGS_TEMPLATE
        app.log("Local INI files missing. Loaded default template from internal settings_data.py.")

    settings_dict = {}
    if content:
        match = re.search(r"OptionSettings=\((.*)\)", content, re.DOTALL)
        if match:
            raw_settings = match.group(1).strip()
            for match_obj in re.finditer(r'(\w+)\s*=\s*(?:"([^"]*)"|\(([^)]*)\)|([^,)]*))', raw_settings):
                key = match_obj.group(1)
                val_str = match_obj.group(2)
                arr_str = match_obj.group(3)
                plain_str = match_obj.group(4)
                
                if val_str is not None:
                    settings_dict[key] = f'"{val_str}"'
                elif arr_str is not None:
                    settings_dict[key] = f"({arr_str})"
                else:
                    settings_dict[key] = plain_str.strip()

    # Clear dynamically loaded cards from columns before rebuilding
    for child in app.settings_col_left.winfo_children(): child.destroy()
    for child in app.settings_col_right.winfo_children(): child.destroy()

    app.setting_entries.clear()
    vcmd = (app.register(app._validate_numeric), '%P')

    # Categories to split
    cat_names = list(SETTINGS_CATEGORIES.keys())
    
    # Left column: Connection, Difficulty, Progression, and System Meta
    left_cats = [cat_names[0], cat_names[1], cat_names[2], cat_names[5]]
    # Right column: Gameplay/Combat and Camp/Building
    right_cats = [cat_names[3], cat_names[4]]

    # Build Left Column
    for category_name in left_cats:
        _build_category_card(app, category_name, app.settings_col_left, settings_dict, vcmd)

    # Build Right Column
    for category_name in right_cats:
        _build_category_card(app, category_name, app.settings_col_right, settings_dict, vcmd)


def _build_category_card(app, category_name, parent_container, settings_dict, vcmd):
    """Helper function to build a single category card and its fields."""
    parameters_list = SETTINGS_CATEGORIES[category_name]
    
    cat_card = StandardCard(parent_container, title=category_name)
    cat_card.pack(fill="x", padx=0)
    
    fields_container = InnerCard(cat_card)

    for key in parameters_list:
        item_row = ctk.CTkFrame(fields_container, fg_color="transparent")
        item_row.pack(fill="x", padx=20, pady=8)
        
        lbl_key = ctk.CTkLabel(item_row, text=key + ":", font=("Segoe UI", 11, "bold"), text_color="#E2E8F0")
        lbl_key.pack(side="left", anchor="w")

        help_text = SETTINGS_HELP.get(key, f"Palworld server configuration parameter: {key}")
        ToolTip(lbl_key, help_text)

        raw_val = settings_dict.get(key, "")
        is_quoted = raw_val.startswith('"') and raw_val.endswith('"')
        val_unquoted = raw_val[1:-1] if is_quoted else raw_val

        if key == "RandomizerSeed" and (val_unquoted == "0" or not val_unquoted):
            val_unquoted = ""

        is_bool = val_unquoted.lower() in ["true", "false"] or key.startswith("b")
        is_predef_enum = key in PREDEFINED_ENUMS

        if is_predef_enum:
            options = PREDEFINED_ENUMS[key]
            display_val = val_unquoted if val_unquoted else options[0]
            if display_val not in options:
                options = [display_val] + options
            entry = ctk.CTkOptionMenu(item_row, values=options, font=("Segoe UI", 11), width=180, fg_color="#16161F", button_color="#1F1F2A", button_hover_color=COLOR_NEON_BLUE, text_color="#E2E8F0")
            entry.set(display_val)
        elif is_bool:
            norm_val = "True" if val_unquoted.lower() == "true" else "False"
            entry = ctk.CTkOptionMenu(item_row, values=["True", "False"], font=("Segoe UI", 11), width=180, fg_color="#16161F", button_color="#1F1F2A", button_hover_color=COLOR_NEON_BLUE, text_color="#E2E8F0")
            entry.set(norm_val)
        else:
            entry = ctk.CTkEntry(item_row, width=180, fg_color="#08080A", border_color="#1F2937", text_color=COLOR_NEON_BLUE, font=("JetBrains Mono", 11))
            entry.insert(0, val_unquoted)
            if re.match(r"^-?\d+(\.\d+)?$", val_unquoted):
                entry.configure(validate='key', validatecommand=vcmd)

        entry.pack(side="right")
        app.setting_entries[key] = entry


def save_settings_data(app):
    """Serializes the configuration inputs back to the INI file."""
    if not app.base_dir:
        messagebox.showwarning("Warning", "Server path root configuration missing.")
        return

    if is_server_running_on_system(app):
        messagebox.showerror(
            "Write Lock Infraction", 
            "Cannot modify configurations while the game server process is running! Please STOP the instance first."
        )
        return

    config_path = app.base_dir / "Pal/Saved/Config/WindowsServer/PalWorldSettings.ini"

    string_keys_whitelist = {
        "ServerName", "ServerDescription", "AdminPassword", "ServerPassword", 
        "PublicIP", "Region", "BanListURL", "AllowConnectPlatform", 
        "AdditionalDropItemWhenPlayerKillingInPvPMode", "RandomizerSeed"
    }

    new_params = []
    processed_keys = set()

    for group in SETTINGS_CATEGORIES.values():
        for key in group:
            if key in app.setting_entries and key not in processed_keys:
                processed_keys.add(key)
                v = app.setting_entries[key]
                val = v.get().strip()
                clean_val = val.strip('"').strip("'")

                if key in string_keys_whitelist:
                    new_params.append(f'{key}="{clean_val}"')
                elif val.startswith("(") and val.endswith(")"):
                    new_params.append(f"{key}={val}")
                else:
                    if not val:
                        val = "True" if key.startswith("b") else "0"
                    new_params.append(f"{key}={val}")

    final_string = f"[/Script/Pal.PalGameWorldSettings]\nOptionSettings=({','.join(new_params)})"
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(final_string, encoding="utf-8")
        messagebox.showinfo("Success", "Configuration changes serialized successfully!")
        app.log("Configuration successfully serialized to PalWorldSettings.ini.")
    except Exception as e:
        app.log(f"Failed to serialize settings file changes: {e}")
        messagebox.showerror("Error", f"Failed to commit file write sequence: {e}")