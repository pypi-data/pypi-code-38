from Homevee.VoiceAssistant.Modules.AddNutritionDataModule import VoiceAddNutritionDataModule
from Homevee.VoiceAssistant.Modules.CalculatorModule import VoiceCalculatorModule
from Homevee.VoiceAssistant.Modules.CalendarModule.AddCalendarModule import VoiceAddCalendarModule
from Homevee.VoiceAssistant.Modules.CalendarModule.GetCalendarModule import VoiceGetCalendarModule
from Homevee.VoiceAssistant.Modules.ConversationModule import VoiceConversationModule
from Homevee.VoiceAssistant.Modules.DeviceControlModule.GetSensorDataModule import VoiceDeviceGetSensorDataModule
from Homevee.VoiceAssistant.Modules.DeviceControlModule.RGBControlModule import VoiceRgbDeviceControlModule
from Homevee.VoiceAssistant.Modules.DeviceControlModule.SetModesModule import VoiceDeviceSetModesModule
from Homevee.VoiceAssistant.Modules.GetActivitiesModule import VoiceGetActivitiesModule
from Homevee.VoiceAssistant.Modules.GetJokesModule import VoiceGetJokesModule
from Homevee.VoiceAssistant.Modules.GetNutritionDiaryModule import VoiceGetNutritionDiaryModule
from Homevee.VoiceAssistant.Modules.GetNutritionInfoModule import VoiceGetNutritionInfoModule
from Homevee.VoiceAssistant.Modules.GetRecipesModule import VoiceGetRecipesModule
from Homevee.VoiceAssistant.Modules.GetSummaryModule import VoiceGetSummaryModule
from Homevee.VoiceAssistant.Modules.GetTVScheduleModule import VoiceGetTvScheduleModule
from Homevee.VoiceAssistant.Modules.GetTVTippsModule import VoiceGetTvTippsModule
from Homevee.VoiceAssistant.Modules.GetWeatherModule import VoiceGetWeatherModule
from Homevee.VoiceAssistant.Modules.GetWeekdayModule import VoiceGetWeekdayModule
from Homevee.VoiceAssistant.Modules.MovieApiModule import VoiceMovieApiModule
from Homevee.VoiceAssistant.Modules.PlacesApiModule import VoicePlacesApiModule
from Homevee.VoiceAssistant.Modules.ShoppingListModule.AddToShoppingListModule import \
    VoiceAddToShoppingListModule
from Homevee.VoiceAssistant.Modules.ShoppingListModule.GetShoppingListModule import VoiceGetShoppingListModule
from Homevee.VoiceAssistant.Modules.WikipediaDefinitionModule import VoiceGetWikipediaDefinitionModule


def get_voice_modules():
    voice_modules = [
        VoiceAddCalendarModule(priority=1),
        VoiceGetCalendarModule(priority=1),
        VoiceAddNutritionDataModule(priority=1),
        VoiceGetActivitiesModule(priority=1),
        VoiceGetNutritionInfoModule(priority=1),
        VoiceGetRecipesModule(priority=1),
        VoiceDeviceGetSensorDataModule(priority=1),
        VoiceGetSummaryModule(priority=1),
        VoiceGetTvScheduleModule(priority=1),
        VoiceGetTvTippsModule(priority=1),
        VoiceGetWeatherModule(priority=1),
        VoiceGetWeekdayModule(priority=1),
        VoiceGetWikipediaDefinitionModule(priority=1),
        VoiceGetJokesModule(priority=1),
        VoiceMovieApiModule(priority=1),
        VoiceGetNutritionDiaryModule(priority=1),
        VoicePlacesApiModule(priority=1),
        VoiceRgbDeviceControlModule(priority=1),
        VoiceDeviceSetModesModule(priority=1),
        VoiceAddToShoppingListModule(priority=1),
        VoiceGetShoppingListModule(priority=1),
        VoiceCalculatorModule(priority=1),
        VoiceConversationModule(priority=0),
        #VoiceModule(priority=1),
    ]

    #voice_modules = sorted(voice_modules, key=lambda x: x.get_priority(), reverse=True)

    return voice_modules