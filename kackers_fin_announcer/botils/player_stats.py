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
        kr_total_maps = 450
        kx_total_maps = 201
        krText = ui.TextDisplay(f"Kacky Reloaded: **{kr_fin_count} / {kr_total_maps} ({round(kr_fin_count / kr_total_maps * 100, 2)}%)**")
        kxText = ui.TextDisplay(f"Kacky Remixed: **{kx_fin_count} / {kx_total_maps} ({round(kx_fin_count / kx_total_maps * 100, 2)}%)**")

        self.add_item(nameText)
        self.add_item(krText)
        self.add_item(kxText)

class MissingContainer(ui.Container):  
    def __init__(self, username, data):  
        super().__init__(ui.TextDisplay("Missing"))    
  
# Main view that switches between containers  
class SwitchableView(ui.LayoutView):  
    def __init__(self, generalStats: GeneralStatsContainer, missing: MissingContainer):  
        super().__init__()  
        self.generalStats = generalStats
        self.missing = missing
        self.current = self.generalStats  
  
        # Toggle buttons  
        controls = ui.ActionRow()       

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
            await self._switch_to(interaction, self.missing)

        buttonGeneralStats.callback = callbackGeneralStats
        buttonMissing.callback = callbackMissing

        controls.add_item(buttonGeneralStats)
        controls.add_item(buttonMissing)

        self.mainContainer = ui.Container()
        self.mainContainer.add_item(controls)
        self.mainContainer.add_item(ui.Separator())

        for component in self.current.children:
            self.mainContainer.add_item(component)
        
        self.add_item(self.mainContainer)


    async def _switch_to(self, interaction: discord.Interaction, new_container: ui.Container):  
        if new_container is self.current:  
            await interaction.response.defer()  
            return  
        
        for component in self.current.children:
            self.mainContainer.remove_item(component)
        
        for component in new_container.children:
            self.mainContainer.add_item(component)

        self.current = new_container  
        await interaction.response.edit_message(view=self)