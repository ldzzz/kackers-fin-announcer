import discord
import botils.config

from discord import ui  
from dataclasses import dataclass
from botils.load_config_logger import get_module_logger

logger = get_module_logger(__name__)

@dataclass
class PageDef:
    name: str
    emoji: str
    default_subpage: int = 0
    
# Define two containers  
class GeneralStatsContainer(ui.Container):  
    def __init__(self, username, data):  
        super().__init__()  

        nameText = ui.TextDisplay(f"Username: **{username}**" )
        kr_fin_count = len(data["kr_finishes"])
        kx_fin_count = len(data["kx_finishes"])
        kr_total_maps = botils.config.CFG.BOT["hunting"]["kr_mappack_count"]
        kx_total_maps = botils.config.CFG.BOT["hunting"]["kx_mappack_count"]
        krText = ui.TextDisplay(f"Kacky Reloaded: **{kr_fin_count} / {kr_total_maps} ({round(kr_fin_count / kr_total_maps * 100, 2)}%)**")
        kxText = ui.TextDisplay(f"Kacky Remixed: **{kx_fin_count} / {kx_total_maps} ({round(kx_fin_count / kx_total_maps * 100, 2)}%)**")

        self.add_item(nameText)
        self.add_item(krText)
        self.add_item(kxText)

class MissingContainer(ui.Container):  
    def __init__(self, username, data):  
        super().__init__(ui.TextDisplay(f"**{username} is missing:**", id=102))
        self.current_page = 0
        self.max_per_page = 10
        self.edition = 0

        self.missingKR = get_kr_missing(data)
        self.missingKX = get_kx_missing(data)
        self.missingText = None

        self.updateList()

    def updateList(self):
        if self.missingText != None:
            self.remove_item(self.missingText)

        missingEntries = self.get_missing_entries()

        string = ""
        for i in missingEntries:
            if self.edition == 0:
                string += "Kacky Reloaded #" + str(i) + "\n"
            else: 
                string += "Kacky Remixed #" + str(i) + "\n"

        self.missingText = ui.TextDisplay(string, id=101)
        self.add_item(self.missingText)

    def get_missing_entries(self):
        minEntry = self.current_page * self.max_per_page
        maxEntry = (self.current_page + 1) * self.max_per_page

        missing = self.missingKR
        if self.edition == 1:
            missing = self.missingKX

        maxEntry = min(maxEntry, len(missing))

        return missing[minEntry:maxEntry]

    def nextPage(self):
        missing = self.missingKR
        if self.edition == 1:
            missing = self.missingKX

        self.current_page += 1
        if (self.current_page + 1) * self.max_per_page >= len(missing):
            return True
        return False

    def prevPage(self):
        self.current_page -= 1
        if self.current_page == 0:
            return True
        return False
    
    def switch_edition(self):
        self.edition = (self.edition + 1) % 2
        
        self.current_page = 0
        self.updateList()
        pass

# Main view that switches between containers  
class SwitchableView(ui.LayoutView):  
    def __init__(self, generalStats: GeneralStatsContainer, missing: MissingContainer):  
        super().__init__()  
        self.generalStats = generalStats
        self.missing = missing
        self.current = self.generalStats  
  
        # Toggle buttons  
        self.controls = ui.ActionRow() 
        self.setupTopActionRow()

        self.eventControls = ui.ActionRow()
        self.setupEventSelection()

        self.PageControls = ui.ActionRow()
        self.setupPageActionRow()  

        self.mainContainer = ui.Container()
        self.mainContainer.add_item(self.controls)
        self.mainContainer.add_item(ui.Separator())

        for component in self.current.children:
            self.mainContainer.add_item(component)
        
        self.add_item(self.mainContainer)

    def setupEventSelection(self):
        self.buttonKr = discord.ui.Button(
            emoji="🇷",
            label="KR",
            custom_id="KR_button",
            disabled=True
        )

        self.buttonKx = discord.ui.Button(
            emoji="🇽",
            label="KX",
            custom_id="KX_button",
            disabled=False
        )

        async def callbackKRButton(interaction: discord.Interaction):
            self.missing.switch_edition()
            self.buttonKr.disabled = True
            self.buttonKx.disabled = False
            self.buttonNext.disabled = False
            self.buttonPrev.disabled = True
            self.update_container()
            await interaction.response.edit_message(view=self)

        async def callbackKXButton(interaction: discord.Interaction):
            self.missing.switch_edition()
            self.buttonKr.disabled = False
            self.buttonKx.disabled = True
            self.buttonNext.disabled = False
            self.buttonPrev.disabled = True
            self.update_container()
            await interaction.response.edit_message(view=self)

        self.buttonKr.callback = callbackKRButton
        self.buttonKx.callback = callbackKXButton

        self.eventControls.add_item(self.buttonKr)
        self.eventControls.add_item(self.buttonKx)

    def setupTopActionRow(self):
        buttonGeneralStats = discord.ui.Button(
            emoji="📊",
            label="Stats",
            custom_id="stats",
        )

        buttonMissing = discord.ui.Button(
            emoji="🔍",
            label="Missing",
            custom_id="missing",
        )
    
        async def callbackGeneralStats(interaction: discord.Interaction):
            await self._switch_to(interaction, self.generalStats)

        async def callbackMissing(interaction: discord.Interaction):
            try:
                await self._switch_to(interaction, self.missing)
            except Exception as e:
                logger.info(e)

        buttonGeneralStats.callback = callbackGeneralStats
        buttonMissing.callback = callbackMissing

        self.controls.add_item(buttonGeneralStats)
        self.controls.add_item(buttonMissing)

    def setupPageActionRow(self):
        self.buttonNext = discord.ui.Button(
            emoji="▶️",
            custom_id="Next_Page",
            disabled=False
        )

        self.buttonPrev = discord.ui.Button(
            emoji="◀️",
            custom_id="Previous_Page",
            disabled=True
        )

        self.buttonNext.callback = self.callbackNextPage
        self.buttonPrev.callback = self.callbackPrevPage

        self.PageControls.add_item(self.buttonPrev)
        self.PageControls.add_item(self.buttonNext)

    def update_container(self):
        self.mainContainer.clear_items()

        self.mainContainer.add_item(self.controls)
        self.mainContainer.add_item(ui.Separator())

        if type(self.current) == MissingContainer:
            self.mainContainer.add_item(self.eventControls)
            self.mainContainer.add_item(ui.Separator())

        for component in self.current.children:
            self.mainContainer.add_item(component)

        if type(self.current) == MissingContainer:
            self.mainContainer.add_item(self.PageControls)

    async def _switch_to(self, interaction: discord.Interaction, new_container: ui.Container):  
        if new_container is self.current:  
            await interaction.response.defer()  
            return  
        
        self.current = new_container  
        self.update_container()
        await interaction.response.edit_message(view=self)

    async def callbackNextPage(self, interaction: discord.Interaction):
        res = self.missing.nextPage()
        self.buttonPrev.disabled = False
        if res:
            self.buttonNext.disabled = True

        self.missing.updateList()
        self.update_container()

        await interaction.response.edit_message(view=self)

    async def callbackPrevPage(self, interaction: discord.Interaction):
        res = self.missing.prevPage()
        self.buttonNext.disabled = False
        if res:
            self.buttonPrev.disabled = True
        self.missing.updateList()
        self.update_container()
        await interaction.response.edit_message(view=self)

def get_kr_missing(data):
    kr_fins = data["kr_finishes"]
    kr_fins.sort(key = lambda x: x["number"])

    missing = []
    index = 0
    for i in range(1, botils.config.CFG.BOT["hunting"]["kr_mappack_count"] + 1):
        if index == len(kr_fins):
            missing.append(i)
        elif kr_fins[index]["number"] == i:
            index += 1
        else:
            missing.append(i)

    return missing

def get_kx_missing(data):
    kx_fins = data["kx_finishes"]
    kx_fins.sort(key = lambda x: x["number"])

    missing = []
    index = 0
    for i in range(0, botils.config.CFG.BOT["hunting"]["kx_mappack_count"]):
        if index == len(kx_fins):
            missing.append(i)
        elif kx_fins[index]["number"] == i:
            index += 1
        else:
            missing.append(i)

    return missing