import os
import gherkan.utils.constants as c

from gherkan.flask_api.raw_text_to_signal import nl_to_signal

# request = {
#     "feature": "robot R4",
#     "feature_desc": "Robot R4 je kolaborativní robot Kuka IIWA. Má za úkol finální kompletaci autíčka. Postupně mu jsou na jeho stanici XX přivezeny zkompletované součásti autíčka. Robotu je nejdříve přivezono chassi autíčka. Následuje body (korba) a jako poslední je přivezena kabina.",
#     "background": "given line is on",
#     "text_raw": "scenario   As soon as robot R1 finished sorting all cubes, shuttle goes to station XXX",
#     "language": "en"
# }

request = {
    "feature" : "Robot N2",
    "feature_desc" : "Po dokončení svařováhí je výrobek pomocí robota N2 přemístěn ze stolu na dopravník. Na doravníkový pás se může položit výrobek poze při splěnní násoledujících podmínke. Místo pro umístění výrobku na pás je volné, pás není v pohybu a lakování předchozího výrobku bylo úspoěšně ukončeno tzn. předchozí výrobek odjel z pozice pro lakování. Pás se nesmí rozjet v případě, že robot nedolakoval výrobek. Hrozí poškození robota a jeho lakovacích pistolí a výrobek by nebyl správně nalakován.",
    "background" : "pokud linka je v provozu",
    "text_raw" : "scénář  Jakmile robot N1 skončí svařit díl 1 s dílem 2 a robot N2 skončí položit produkt na pás a robot N2 je inaktivní, pak robot N2 začne zvedat produkt \n scénář  Pokud produkt není na začátku a produkt není na pozici a dopravník zastaví a robot N2 skončí zvedat produkt, pak robot N2 začne položit produkt na pás \n scénář  Pokud je produkt na začátku nebo je produkt na pozici nebo dopravník začne, jakmile robot N2 skončí zvedat produkt, pak robot nepoloží produkt na pás",
    "language" : "cs"
}


base_path = os.path.join(c.DATA_DIR, "input", "raw_out")

nl_to_signal(base_path, request)

nl_file_path = base_path + ".feature"
signal_file_path = base_path + "_signals.feature"

print("\n\n--- NL FILE ---")
with open(nl_file_path, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)

print("\n\n--- SIGNAL FILE ---")
with open(signal_file_path, "rt", encoding="utf-8") as f:
    text = f.read()
    print(text)